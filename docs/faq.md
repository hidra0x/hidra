# Hidra FAQ

## Is Hidra a working jailbreak?

No. Hidra is a research project. The current state is a reproducible kernel
UAF and a controlled same-type reclaim in `AppleJPEGDriver`. There is no
kernel read/write, no PAC/PPL bypass, and no public build.

## Which devices are supported?

The primary test device is:

- iPhone XR (`iPhone11,8`), A12 / T8020, iOS 18.7.2 (22H124).

Other A12/A13 devices on 18.7.x may share the driver, but they are untested.
A14+ devices are not planned initially.

## Which iOS versions work?

Only iOS 18.7.2 is being tested. The CVE is fixed in iOS 18.7.7 / iPadOS
18.7.7 and iOS 26.4 / iPadOS 26.4. Those versions are not supported.

## Is it tethered?

The first target is **semi-tethered**: the device boots normally, the user
launches Hidra after a reboot, and the bootstrap is reapplied. Untethered
persistence is a later goal.

## When will it be released?

The current research estimate is:

- closed beta: **Q2 2027**;
- public beta: **Q3 2027**.

This is not a promise. The date depends on a double-free/write primitive,
KASLR, PAC, and PPL/SPTM. If any gate fails, the date moves or the project
ships a kernel r/w research toolkit instead.

## Why not release the current build?

The current build can panic, reboot, or wedge the JPEG driver's power state.
It has no useful primitive for users and no recovery story. Releasing it
would be a crash tool, not a jailbreak.

## Will it support A14/A15/A16 devices?

Not initially. Newer SoCs have different PAC/PPL behavior and a different
AppleJPEGDriver build. Support would require a separate research effort.

## Will it bypass iCloud or activation locks?

No. Hidra targets owned devices with a normal sideloading setup. It does not
bypass activation locks, iCloud locks, or MDM.

## Is this legal?

Security research on devices you own is legal in many jurisdictions. Laws
vary; you are responsible for your local rules. Do not use the project for
unauthorized access, malware, or piracy.

## Why the name Hidra?

Hydra: many heads, many paths into the kernel. The project started with HID
(IOHIDFamily) and continued through AppleJPEGDriver. The kernel entry stage
is codenamed **JPEGSWORD**.

## How can I help?

- Test on a spare A12/A13 device running 18.7.x.
- Provide `panic-full-*.ips` logs with the AppleJPEGDriver signature.
- Reverse engineer `AppleJPEGDriver 7.6.9`, PAC/PPL, IOSurface.
- Write reproducible reports, not just screenshots.

## Where is the research?

The PoCs, test matrix, and panic analysis live in
[`hidgate-poc`](https://github.com/nenasevartem70-cmyk/hidgate-poc):

- [Kernel control ladder](https://github.com/nenasevartem70-cmyk/hidgate-poc/blob/main/docs/kernel-control.md)
- [Final tests](https://github.com/nenasevartem70-cmyk/hidgate-poc/blob/main/docs/final-tests.md)
- [AppleJPEG CVE notes](https://github.com/nenasevartem70-cmyk/hidgate-poc/blob/main/docs/applejpeg-cve-2026-20687.md)
- [Experiment log](https://github.com/nenasevartem70-cmyk/hidgate-poc/blob/main/docs/experiment-log.md)

## Is this DarkSword?

No. DarkSword is a different research chain. Hidra's kernel entry is the
AppleJPEGDriver timeout UAF (CVE-2026-20687) on A12/18.7.2.
