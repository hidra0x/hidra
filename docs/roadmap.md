# Hidra roadmap

This is a research roadmap, not a release contract. Dates are estimates and
will slip if a gate fails.

## Milestones

| ID | Milestone | Target | Exit criterion | Confidence |
|---|---|---|---|---|
| M0 | Research base | done | AppleJPEG userclient + 0x58 ABI on A12/18.7.2 | **done** |
| M1 | Deferred UAF | done | reproducible panic in `AppleJPEGDriver` | **done** |
| M2 | Controlled free | done | `kIOReturnTimeout` after 10.001 s | **done** |
| M3 | Same-type reclaim | done | 10 async allocations after the free, kernel survives | **done** |
| M4 | Kernel primitive | Nov–Dec 2026 | reproducible double-free or write primitive | medium-low |
| M5 | KASLR | Dec 2026–Jan 2027 | kernel slide leak | low |
| M6 | PAC | Jan–Feb 2027 | signing gadget/oracle or data-only path | low |
| M7 | PPL / SPTM | Mar–May 2027 | patch or data-only bypass | low |
| M8 | Bootstrap | Apr–May 2027 | launchd hook + package manager prototype | low |
| M9 | Closed beta | **Q2 2027** | 10/10 reliable on iPhone XR 18.7.2 | low |
| M10 | Public beta | **Q3 2027** | closed beta stable, recovery path documented | low |

## Possible release date

**Public beta: Q3 2027 (July–September 2027).**

This is the current best-case estimate, not a promise. It assumes:

- M4 (double-free/write) lands by the end of 2026;
- KASLR and PAC are solvable on A12/18.7.2;
- PPL/SPTM does not require a separate kernel bug;
- the bootstrap survives a reboot.

If any of those assumptions fails, the date moves or the project ships a
kernel r/w research toolkit instead of a jailbreak.

## Release channels

| Channel | Audience | Contents |
|---|---|---|
| `dev` | researchers | unstable IPAs, panic logs, test builds |
| `closed-beta` | trusted testers | signed IPA, bootstrap, recovery instructions |
| `public-beta` | everyone | signed release, documentation, support matrix |

No build is published until M9 passes. A build that only panics is not a
release.

## What “done” means

A Hidra release must:

1. boot the device normally;
2. run from a sideloaded app after a reboot (semi-tethered);
3. install a bootstrap and a package manager;
4. survive at least 20 reboot/run cycles on the test device;
5. have a documented recovery path (DFU/restore) for failed installs;
6. not require a stolen certificate, MDM, or activation bypass.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| PAC blocks the call path | no kernel control | data-only primitive, signing gadget research |
| PPL/SPTM blocks patching | no bootstrap | data-only hook, launchd-only persistence |
| Typed zone blocks reclaim | no write primitive | IOSurface/UC refcount path |
| Power-state wedge | device unstable | avoid immediate close; keep requests in flight |
| Apple patches 18.7.2 | target disappears | research is version-specific; no downgrade promise |
| Test device failure | no hardware | spare device, documented recovery |

## Version support

- **Primary:** iPhone XR, iOS 18.7.2.
- **Later:** other A12/A13 devices on 18.7.x, only after the primitive is
  stable.
- **Never:** iOS 18.7.7+ / 26.4+ (the CVE is fixed there).
- **Not planned initially:** A14+ (different PAC/PPL and driver behavior).

## Research cadence

- Weekly test builds while M4 is active.
- Every build gets a test ID and a panic/log link.
- A milestone is complete only when the result is reproducible on a clean
  boot, not after one lucky run.
