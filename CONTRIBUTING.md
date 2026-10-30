# Contributing to Hidra

Hidra is a research project. Contributions are welcome if they move a
milestone forward, not just add another crash demo.

## What is useful

- **Reproducible test results** on A12/A13 devices running iOS 18.7.x.
- **Panic logs** (`panic-full-*.ips`) with the AppleJPEGDriver signature and
  exact steps.
- **Reverse engineering** of `AppleJPEGDriver 7.6.9`, IOSurface, PAC/PPL, and
  the XNU queue/power paths.
- **Tooling** for building, signing, and collecting logs from Windows/WSL.
- **Documentation** that corrects an overclaim or fills a gap.

## What is not useful

- Screenshots without a log or steps.
- "It works on my device" without the build hash and OS build.
- Requests to bypass activation locks, iCloud, or MDM.
- Exploit sales, stolen certificates, or malware.

## Test report template

```
Device:
SoC:
iOS build:
Hidra build / commit:
Installer:
Steps:
Expected:
Actual:
Log / panic file:
```

## Development

- The research base is
  [`hidgate-poc`](https://github.com/nenasevartem70-cmyk/hidgate-poc).
- Test builds are version-specific. Do not assume a build for 18.7.2 works on
  18.7.7+; the CVE is fixed there.
- Keep changes small and reproducible. One commit should answer one question.

## Safety

Use a spare device. Research builds can panic, reboot, or wedge the JPEG
driver's power state. Keep a restore path available.

## Disclosure

If you find a new kernel vulnerability, report it to the vendor first. Do not
publish a new zero-day through this repository. See [`SECURITY.md`](SECURITY.md).
