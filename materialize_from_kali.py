#!/usr/bin/env python3
"""
Materialise Glass bundle manifests from the Kali reverse-engineering data.

Reads references/kali/glass-split.json (per-bundle rpm/container split, produced from
the live Kali apt graph triaged against Fedora) and writes bundles/<name>.yaml for each,
with:
  - rpm:        the verified-in-Fedora subset (safe to layer on the host)
  - containers: a reference to the bundle's distrobox lab image (carries the rest)
  - category:   the bundle key (drives XDG menu category in the image generator)

Hand-authored bundles (networking, web, passwords) are NOT overwritten unless --force.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPLIT = HERE / "references/kali/glass-split.json"

# Kali category key -> human description
DESC = {
    "information-gathering": "Reconnaissance and information gathering",
    "vulnerability": "Vulnerability analysis and scanning",
    "web": "Web application assessment",
    "database": "Database assessment",
    "passwords": "Password cracking and hash auditing",
    "exploitation": "Exploitation frameworks and tools",
    "post-exploitation": "Post-exploitation and lateral movement",
    "sniffing-spoofing": "Sniffing and spoofing",
    "social-engineering": "Social engineering",
    "reverse-engineering": "Reverse engineering",
    "fuzzing": "Fuzzing",
    "forensics": "Digital forensics",
    "wireless": "Wireless attacks",
    "802-11": "802.11 (Wi-Fi) attacks",
    "bluetooth": "Bluetooth attacks",
    "sdr": "Software-defined radio",
    "rfid": "RFID/NFC tooling",
    "hardware": "Hardware hacking",
    "voip": "VoIP assessment",
    "identify": "Defensive: identify (NIST CSF)",
    "protect": "Defensive: protect (NIST CSF)",
    "detect": "Defensive: detect (NIST CSF)",
    "respond": "Defensive: respond (NIST CSF)",
    "recover": "Defensive: recover (NIST CSF)",
    "reporting": "Reporting",
    "top10": "Kali top-10 headline tools",
    "windows-resources": "Windows resources & binaries",
    "crypto-stego": "Cryptography & steganography",
    "gpu": "GPU-accelerated tooling",
}

# Bundles whose unpackaged tools warrant a dedicated distrobox lab image.
NEEDS_LAB = {
    "web", "exploitation", "vulnerability", "forensics", "reverse-engineering",
    "information-gathering", "passwords", "wireless", "voip", "windows-resources",
    "post-exploitation", "database", "sniffing-spoofing", "fuzzing",
    "social-engineering", "identify", "protect", "detect", "respond", "recover",
}

# Do not clobber these hand-authored ones unless --force.
HAND_AUTHORED = {"networking", "web", "passwords"}

LAB_ALIAS = {"information-gathering": "osint", "reverse-engineering": "reversing",
             "windows-resources": "windows"}


def yaml_list(items: list[str], indent: str = "  ") -> str:
    return "\n".join(f"{indent}- {i}" for i in items) if items else ""


def render(name: str, data: dict) -> str:
    rpm = data.get("rpm", [])
    container_only = data.get("container", [])
    desc = DESC.get(name, f"Kali {name} tools")
    lab = LAB_ALIAS.get(name, name)
    lines = [f"# Goshenite bundle: {name}",
             f"# Auto-generated from Kali reverse-engineering (references/kali/).",
             f"# rpm: = verified in Fedora 44; container tools shipped via the {lab}-lab distrobox.",
             f"name: {name}",
             f"description: {json.dumps(desc)}",
             f"category: {name}",
             ""]
    if rpm:
        lines.append("rpm:")
        lines.append(yaml_list(rpm))
        lines.append("")
    if name in NEEDS_LAB and container_only:
        lines.append("# The following Kali tools have no Fedora RPM and ship in the lab container:")
        # list up to 12 as a comment for visibility, full set lives in glass-containers
        preview = container_only[:12]
        for t in preview:
            lines.append(f"#   {t}")
        if len(container_only) > 12:
            lines.append(f"#   ... +{len(container_only)-12} more")
        lines.append("containers:")
        lines.append(f"  - ghcr.io/goshenite-systems/{lab}-lab:latest")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=HERE / "bundles")
    ap.add_argument("--force", action="store_true", help="overwrite hand-authored bundles too")
    ap.add_argument("--only", nargs="*", help="only generate these bundle names")
    args = ap.parse_args()

    split = json.loads(SPLIT.read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    written, skipped = [], []
    for name, data in sorted(split.items()):
        if args.only and name not in args.only:
            continue
        if name in HAND_AUTHORED and not args.force:
            skipped.append(name); continue
        (args.out / f"{name}.yaml").write_text(render(name, data))
        written.append(name)
    print(f"wrote {len(written)} bundles: {', '.join(written)}")
    if skipped:
        print(f"skipped hand-authored (use --force): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
