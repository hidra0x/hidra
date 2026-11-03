# HIDRA loader (semi-tethered harness)

The PC side of the semi-tethered model:

```
reboot -> normal iOS -> run hidra-loader -> launch the on-device agent
      -> agent runs the current stage -> logs/status -> (future) kernel patch
```

**This is not a working jailbreak.** It contains no kernel exploit. It is the
USB harness and the place where a future S4/S5 primitive will be plugged in.
The on-device research agent is
[CandProbe](https://github.com/hidra0x/hidgate-poc/tree/main/experiments/candprobe).

## Why semi-tethered

- The device always boots normal iOS.
- After a reboot the jailbreak is gone until the user runs the loader again.
- No bootchain modification, no tethered boot, no DFU loop.
- This is the only realistic persistence model for a research jailbreak
  that starts from a sideloaded app.

## Install

```bash
python -m pip install pymobiledevice3
```

`pymobiledevice3` provides the USB device list, lockdown info, app launch,
and syslog streaming. The loader shells out to it so the command can be
overridden for different versions.

## Commands

Run from the **repository root**, not from `C:\Users\<you>`:

```bat
cd C:\Users\Артем\hidra
python loader\hidra_loader.py doctor
python loader\hidra_loader.py devices
python loader\hidra_loader.py info
python loader\hidra_loader.py launch
python loader\hidra_loader.py syslog --seconds 30 --out logs\agent.log
python loader\hidra_loader.py jailbreak --seconds 300
```

The loader resolves the sideload team-ID suffix automatically, for example
`com.example.hidgate4.H4UP99UW92`. On iOS 17+ it launches the agent with:

```bat
python -m pymobiledevice3 mounter auto-mount
python -m pymobiledevice3 developer dvt launch --userspace <resolved-bundle>
```

No device attached? Preview the commands:

```bash
python hidra_loader.py --dry-run jailbreak --seconds 5
```

If your `pymobiledevice3` version does not support `apps launch`, use:

```bash
python hidra_loader.py --pmd3 "python -m pymobiledevice3" launch
pymobiledevice3 developer dvt launch com.example.hidgate4
```

## What the loader checks

The agent writes `os_log` markers with subsystem `com.hidra.agent`:

| Marker | Meaning |
|---|---|
| `HIDRA_AGENT_UP` | agent launched, device/iOS reported |
| `HIDRA_STAGE0_DONE` | IOKit enumeration finished |
| `HIDRA_STAGE2_DONE` | VT/AVE tests finished |
| `HIDRA_STAGE3_DONE` | raw AVE attempt finished |
| `HIDRA_STAGE6_DONE` | Mach VM tests finished |
| `HIDRA_STAGE7_DONE` | targeted media/GPU/ANE scan finished |
| `HIDRA_STAGE8_DONE` | malformed IOSurface test finished |
| `HIDRA_JAILBROKEN` | reserved; only when a real kernel primitive lands |

The loader returns:

- `0` if `HIDRA_JAILBROKEN` is present;
- `2` if `HIDRA_PANIC` is present;
- `3` if the USB loop worked but no kernel primitive was reported.

Today the expected result is **3**.

## What is missing for a real semi-tethered jailbreak

| Gate | Component | State |
|---|---|---|
| S4 | kernel write/read primitive | **open** |
| S5 | KASLR leak + PAC/data-only path | not started |
| S6 | PPL/AMFI/csflags patch | not started |
| S7 | launchd hook + bootstrap + package manager | not started |

The loader, agent, log protocol, and recovery loop are ready before the
exploit. That is deliberate: when S4 lands, the same harness can carry the
payload and start the bootstrap.

## Safety

- Use the spare iPhone XR only.
- The agent can panic the device; that is expected in research.
- After a panic, reboot, unlock, trust the computer, and re-run the loader.
- Never run research builds on a primary phone.
