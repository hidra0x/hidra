# Security policy

## Scope

Hidra is a security research project for owned Apple devices. It is not a
product and it is not a supported jailbreak yet.

The project does not:

- bypass activation locks or iCloud locks;
- target devices the researcher does not own;
- provide stolen certificates, MDM profiles, or enterprise signing material;
- support malware, piracy, or unauthorized access.

## Testing safety

- Use a spare device.
- Save your data; the test builds can panic, reboot, or wedge the JPEG
  driver's power state.
- Keep a restore path (Finder/iTunes/DFU) available.
- Do not run research builds on a primary phone.

## Reporting a problem in Hidra

Open a GitHub issue with:

- device model and SoC;
- iOS build;
- Hidra build/commit;
- exact steps;
- `panic-full-*.ips` or app log;
- expected vs actual behavior.

Do not include personal data, Apple ID credentials, or device identifiers you
do not want public.

## Reporting a new kernel vulnerability

If you find a new vulnerability while working on Hidra, do not publish it
immediately. Report it to the affected vendor (Apple Security) first, then
coordinate disclosure. Hidra's scope is the public CVE-2026-20687 research on
iOS 18.7.2, not a new zero-day campaign.

## Supported versions

| Version | Status |
|---|---|
| iOS 18.7.2 / A12 | research target |
| iOS 18.7.7+ | patched, not supported |
| iOS 26.4+ | patched, not supported |

## No warranty

The software is provided "as is", without warranty of any kind. See
[`LICENSE`](LICENSE).
