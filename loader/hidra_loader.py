#!/usr/bin/env python3
"""HIDRA semi-tethered loader (research harness).

This is the PC side of the semi-tethered model:

    reboot -> normal iOS -> run this tool -> launch the on-device agent
    -> agent runs the current stage -> logs/status -> (future) kernel patch

It does NOT contain a kernel exploit and it does NOT jailbreak iOS 18.7.2.
The exploit stages are still research gates S4-S7 in the HIDRA roadmap.
What it does provide is a reproducible USB loop for the agent and a place
to plug in the kernel primitive when it exists.

Dependency:
    python -m pip install pymobiledevice3

Examples:
    python hidra_loader.py doctor
    python hidra_loader.py devices
    python hidra_loader.py info
    python hidra_loader.py launch --bundle com.example.hidgate4
    python hidra_loader.py syslog --seconds 30 --out logs/agent.log
    python hidra_loader.py jailbreak --seconds 30

    # no device / command preview:
    python hidra_loader.py jailbreak --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_BUNDLE = "com.example.hidgate4"
DEFAULT_PMD3 = f"{sys.executable} -m pymobiledevice3"


def eprint(*a):
    print(*a, file=sys.stderr)


def run(cmd: list[str], dry: bool, check: bool = False, capture: bool = True) -> subprocess.CompletedProcess:
    print("+ " + " ".join(cmd))
    if dry:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def pmd3_base(args: argparse.Namespace) -> list[str]:
    return args.pmd3.split()


def doctor(args: argparse.Namespace) -> int:
    print("HIDRA loader doctor")
    print("  python:", sys.version.split()[0])
    print("  executable:", sys.executable)
    print("  platform:", sys.platform)
    print("  pymobiledevice3 command:", args.pmd3)

    if args.dry_run:
        print("  dry-run: dependency checks skipped")
        return 0

    cp = run(pmd3_base(args) + ["version"], dry=False)
    if cp.returncode != 0:
        eprint("\npymobiledevice3 is not available.")
        eprint("Install it with:  python -m pip install pymobiledevice3")
        eprint("Then re-run:      python hidra_loader.py doctor")
        return 1
    print("  pymobiledevice3:", (cp.stdout or cp.stderr).strip().splitlines()[:1])
    for tool in ("git", "ideviceinfo", "idevicesyslog"):
        print(f"  {tool}: {shutil.which(tool) or '(not found)'}")
    return 0


def devices(args: argparse.Namespace) -> int:
    cp = run(pmd3_base(args) + ["usbmux", "list"], args.dry_run)
    if cp.returncode != 0:
        eprint(cp.stderr.strip())
        return cp.returncode
    print(cp.stdout.strip())
    return 0


def info(args: argparse.Namespace) -> int:
    cmd = pmd3_base(args) + ["lockdown", "info"]
    if args.udid:
        cmd += ["--udid", args.udid]
    cp = run(cmd, args.dry_run)
    if cp.returncode != 0:
        eprint(cp.stderr.strip())
        return cp.returncode
    print(cp.stdout.strip())
    return 0


def launch(args: argparse.Namespace) -> int:
    cmd = pmd3_base(args) + ["apps", "launch", args.bundle]
    if args.udid:
        cmd += ["--udid", args.udid]
    cp = run(cmd, args.dry_run)
    if cp.returncode != 0:
        eprint(cp.stderr.strip())
        eprint("If 'apps launch' is not supported by your pymobiledevice3 version,")
        eprint("use:  pymobiledevice3 developer dvt launch " + args.bundle)
        return cp.returncode
    print(cp.stdout.strip())
    return 0


def syslog(args: argparse.Namespace) -> int:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = pmd3_base(args) + ["syslog", "live"]
    if args.udid:
        cmd += ["--udid", args.udid]
    print("+ " + " ".join(cmd) + f"   (streaming for {args.seconds}s)")
    if args.dry_run:
        print(f"[dry-run] would write {out}")
        return 0

    deadline = time.time() + args.seconds
    matched = 0
    try:
        with out.open("w", encoding="utf-8", errors="replace") as f:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, bufsize=1)
            assert proc.stdout is not None
            for line in proc.stdout:
                f.write(line)
                f.flush()
                if args.filter and re.search(args.filter, line, re.I):
                    matched += 1
                    print(line.rstrip())
                if time.time() >= deadline:
                    break
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    except FileNotFoundError:
        eprint("pymobiledevice3 not found")
        return 1
    print(f"syslog: wrote {out} ({matched} matching lines)")
    return 0


def jailbreak(args: argparse.Namespace) -> int:
    print("HIDRA semi-tethered sequence")
    print("  target : iPhone XR / A12 / iOS 18.7.2")
    print("  model  : reboot -> normal iOS -> run loader -> launch agent")
    print("  status : loader harness only; kernel primitive S4 is not implemented")
    print()

    rc = devices(args)
    if rc != 0:
        return rc
    if not args.dry_run:
        time.sleep(0.3)
    rc = info(args)
    if rc != 0:
        eprint("device info failed; is the device unlocked and trusted?")
        return rc

    if args.install:
        cmd = pmd3_base(args) + ["apps", "install", args.install]
        cp = run(cmd, args.dry_run)
        if cp.returncode != 0:
            eprint(cp.stderr.strip())
            eprint("The IPA must be signed for this device. The research builds are unsigned.")
            return cp.returncode

    rc = launch(args)
    if rc != 0:
        return rc

    print()
    log_path = Path(args.out)
    args.out = str(log_path)
    rc = syslog(args)
    if rc != 0:
        return rc

    text = ""
    if not args.dry_run and log_path.exists():
        text = log_path.read_text(encoding="utf-8", errors="replace")

    if "HIDRA_JAILBROKEN" in text:
        print("\nRESULT: agent reported HIDRA_JAILBROKEN")
        return 0
    if "HIDRA_PANIC" in text:
        print("\nRESULT: agent reported a panic breadcrumb; inspect the log")
        return 2
    print("\nRESULT: no kernel primitive reported.")
    print("Expected agent markers: HIDRA_STAGE0_OK, HIDRA_STAGE4_OK, HIDRA_JAILBROKEN.")
    print("S4 (double-free/write) is still open; this run only verifies the USB loop.")
    return 3


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="HIDRA semi-tethered research loader")
    p.add_argument("--pmd3", default=DEFAULT_PMD3,
                   help=f"pymobiledevice3 command (default: {DEFAULT_PMD3})")
    p.add_argument("--udid", default=None, help="target device UDID")
    p.add_argument("--dry-run", action="store_true", help="print commands without executing")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("doctor", help="check dependencies")
    sp.set_defaults(func=doctor)

    sp = sub.add_parser("devices", help="list USB devices")
    sp.set_defaults(func=devices)

    sp = sub.add_parser("info", help="print lockdown info")
    sp.set_defaults(func=info)

    sp = sub.add_parser("launch", help="launch the on-device agent")
    sp.add_argument("--bundle", default=DEFAULT_BUNDLE)
    sp.set_defaults(func=launch)

    sp = sub.add_parser("syslog", help="capture agent logs over USB")
    sp.add_argument("--seconds", type=int, default=30)
    sp.add_argument("--out", default="logs/hidra-syslog.log")
    sp.add_argument("--filter", default=r"HIDRA|hidgate4|CandProbe|panic|AppleJPEG|AVE")
    sp.set_defaults(func=syslog)

    sp = sub.add_parser("jailbreak", help="run the semi-tethered sequence")
    sp.add_argument("--bundle", default=DEFAULT_BUNDLE)
    sp.add_argument("--seconds", type=int, default=30)
    sp.add_argument("--out", default="logs/hidra-jailbreak.log")
    sp.add_argument("--filter", default=r"HIDRA|hidgate4|CandProbe|panic|AppleJPEG|AVE")
    sp.add_argument("--install", default=None, help="optional signed IPA to install first")
    sp.set_defaults(func=jailbreak)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
