# Hidra architecture

This document describes the intended exploit chain. It is a plan, not a
claim that every stage works. The only stages demonstrated on hardware are S0
through S3.

## Target

```
Device:  iPhone XR (iPhone11,8)
SoC:     A12 / T8020, arm64e
OS:      iOS 18.7.2 (22H124)
Kernel:  xnu-11417.140.69.702.20~1
Kext:    com.apple.driver.AppleJPEGDriver 7.6.9
```

The primary entry is a sideloaded app. No Mac is required for the research;
the app is built with clang and an iPhoneOS SDK and signed with a normal
sideloading workflow.

## Stage 0 — Entry

The app opens `AppleJPEGDriver` type 0 and talks to
`AppleJPEGDriverUserClient`. The `0x58`-byte `AppleJPEGDriverIOStruct` is
accepted by selector 1.

Entry checklist:

- `IOServiceOpen("AppleJPEGDriver", 0)` returns `KERN_SUCCESS`;
- `sel1` sync decode returns `KERN_SUCCESS`;
- `sel1` async decode with a non-zero token returns `KERN_SUCCESS`;
- the app can create source/destination IOSurfaces.

All four are confirmed on the test device.

## Stage 1 — Deferred UAF

`AppleJPEGDriver::startDecoder` allocates a `JpegRequest` (0x440-ish), copies
the input struct, and queues the embedded node at `request+0x78` into the
per-codec vector at `driver+0xc0`.

The vulnerable sequence:

1. async decodes are in flight when the userclient closes;
2. `terminatePhase1` marks the client inactive through the arbitration lock;
3. `finish_io_gated` sees `isInactive` and skips the normal release/dequeue;
4. the request is freed, but its queue node remains in the vector;
5. a later queue walk reads the freed object.

Observed panic:

```
pc  = ... (AppleJPEGDriver)
x5  = 0xfeedfacefeedfacf
x6  = 0xfeedfacefeedfacf
x12 = 0
far = 0x308

0xfffffff008df3418:  ldrb w12, [x12, #0x308]
```

The panicking thread is `kernel_task`, so the UAF is deferred. This is the
first confirmed kernel UAF outside the IOHID path.

## Stage 2 — Controlled free

`startDecoder` waits for `request+0x74` in a loop. The wait uses a 10 s
budget (`w2 = 0x2710`). If the completion does not arrive, the timeout path
frees the request and returns `kIOReturnTimeout` (`0xe00002d6`).

An 8000-request mass prime stalls the codec enough that a true sync decode
hits the timeout:

```
cycle round=0 sync kr=0xe00002d6 dt=10.001s
```

This gives a deterministic free point in our own thread.

## Stage 3 — Same-type reclaim

Immediately after the timeout, the app submits async decodes on the same
connection. The first allocation reuses the freed `JpegRequest` slot. The
stale queue node now points at a live request; the kernel survives the next
walk.

This is the current rung: a controlled free plus a same-type reclaim. It is
not a write primitive.

## Stage 4 — Kernel primitive

The goal is to convert the stale node/reclaim into one of:

### 4a. Double free

If the timeout path frees the request without dequeuing, and the reclaimed
request is later freed again through the stale node, the zone receives the
same object twice. A double-free in a typed zone can be turned into an
allocation overlap if the second allocation is controllable.

Open questions:

- does the stale node ever call the free path, or is it read-only?
- does `queue_remove` remove one or all duplicate node pointers?
- can the reclaim request be kept in flight so its completion cannot clean
  the node?

### 4b. IOSurface / IOUserClient refcount

The `JpegRequest` holds references to the source/destination IOSurfaces and
to the userclient. A double release could underflow a refcount and free one of
those objects while it is still reachable. IOSurface and IOUserClient are
different types from `JpegRequest`; the typed zone blocks a direct cross-type
reclaim, but a refcount underflow is a separate path.

### 4c. Queue-node unlink write

The embedded node has `next`/`prev` links. A `queue_remove` on a stale node
writes through those links. If the reclaim can influence them, the unlink
becomes a write-what-where. The node pointers are set by the driver's queue
code, so this needs either a partial overwrite or a second bug.

### 4d. DART / decoder buffer write

The decoder programs the hardware to write pixels into the destination
IOSurface. If the request's surface pointer or DART mapping can be corrupted,
the hardware write becomes a physical-memory write. This is the most direct
route to "write kernel memory", but it needs a controlled field in the freed
request.

## Stage 5 — KASLR

The kernel slide must be known before any pointer can be used. The standard
surfaces are clean on 18.7.2:

- `proc_pidfdinfo` socket/pipe/vnode: no kernel pointers;
- `mach_port_kobject`: `addr = 0`;
- `mach_vm_region`/recurse/remap: no pointers.

Options:

- a kernel read from the new primitive;
- an IOSurface/IOUserClient info leak;
- a timing or PAC-oracle side channel.

## Stage 6 — PAC

A12 is arm64e. The direct call in `finish_io_gated` is:

```asm
ldr x0, [x19]          ; request->task
ldr x16, [x0]          ; task->vtable
autda x16, x17         ; data PAC, modifier = task address
ldr x8, [x16, #0x28]!
blraa x8, x17          ; authenticated call
```

A fake `task_t` needs a signed vtable pointer for its address. Options:

- a signing gadget that signs an attacker-controlled pointer;
- a data-only attack that never calls through the pointer;
- a leak of a valid signed pointer for a reusable object;
- a PAC bypass in a different kernel component.

Without one of these, the `blraa` path is not usable.

## Stage 7 — PPL / SPTM

Kernel text and page tables are protected. A jailbreak needs to:

- patch kernel text or data used by AMFI/codesign;
- or install a launchd/bootstrap hook without patching protected pages;
- or use a supported data-only primitive to disable signature checks.

PPL/SPTM behavior on A12/18.7.2 is the largest unknown after PAC.

## Stage 8 — Persistence and package

First target: **semi-tethered**.

- the device boots normally;
- the user launches Hidra after a reboot;
- the app reapplies the kernel patch and starts the bootstrap.

Package components:

- Hidra IPA (entry + payload);
- on-device bootstrap (launchd hook, substitute/ElleKit, package manager);
- desktop helper for install/recovery.

## Reliability

The current AppleJPEG primitives are timing-sensitive:

- the 10 s timeout depends on a mass prime and codec state;
- the reclaim depends on same-thread allocation after the free;
- immediate close can wedge `setPowerState(1 -> 0)`.

A jailbreak needs a reliability target, not a one-shot demo. The first
milestone is 10/10 successful reclaims on a clean boot, then 10/10 successful
kernel primitives.

## Threat model

- The device is owned by the researcher.
- The app is sideloaded with a normal development certificate.
- No enterprise certificates, no MDM, no stolen signing material.
- The project does not bypass activation locks or iCloud locks.
- The project does not target devices it does not own.

## Open questions

1. Does the stale node ever reach a free path, or only a read?
2. Can the reclaim request be kept in flight indefinitely?
3. Which object does the timeout path release first: request, IOSurface, or
   userclient?
4. Is there a PAC signing gadget reachable from the primitive?
5. Is a data-only PPL bypass possible on A12/18.7.2?
