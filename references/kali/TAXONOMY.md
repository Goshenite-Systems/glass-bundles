# Kali → Glass bundle taxonomy & RPM/container split

Derived by reverse-engineering the live Kali apt metapackage graph on a Kali box
(`apt-cache show kali-tools-*`) and triaging every tool against Fedora 44 / Aurora repos.
Raw data in this directory:
- `kali-tools-membership.json` — every tool in each of the 29 `kali-tools-*` bundles
- `all-tools.txt` — 404 unique tool names
- `fedora-availability.txt` — per-tool OK/MISS against Fedora repos
- `glass-split.json` — per-bundle split into `rpm:` (in Fedora) vs `container:` (not)

## Kali's real structure (what we're adapting)

Kali layers three tiers:
```
kali-linux-{core,headless,default,large,everything}   (editions, cumulative)
        ⊃ kali-tools-*                                 (29 category bundles)
              ⊃ individual .deb packages               (404 unique tools)
```
- **Editions are cumulative**: `everything ⊃ large ⊃ default ⊃ headless ⊃ core`, and
  `everything` additionally pulls in all 29 `kali-tools-*`.
- **`top10`** = curated headliners: aircrack-ng, burpsuite, hydra, john,
  metasploit-framework, netexec, nmap, responder, sqlmap, wireshark.
- **Kali Purple defensive set** = `identify / protect / detect / respond / recover`
  — these are the five **NIST Cybersecurity Framework** functions — plus `reporting`.

## The R1 finding (why Glass is container-first)

**Only 113 of 404 Kali tools (28%) exist as directly-named Fedora RPMs.**

| Tier | Bundles | Fedora RPM coverage |
|------|---------|--------------------|
| **Host-friendly** (RPM-heavy) | hardware 73%, rfid 67%, sdr 58%, crypto-stego 50%, top10 50%, 802-11 42% | layer on the immutable host |
| **Mixed** | information-gathering 39%, forensics 38%, sniffing-spoofing 33%, passwords 25%, web 24% | RPM what exists, container the rest |
| **Container-mandatory** | exploitation 0%, fuzzing 0%, identify 0%, reporting 0%, social-engineering 0%, detect 0%, gpu 0%, windows-resources 6%, vulnerability 14%, voip 17% | distrobox/OCI only |

The signature offensive stack — Metasploit, exploitation, fuzzing, vuln scanning — has
**essentially zero Fedora packaging**. This is definitive proof the container-first
architecture is correct, not a convenience. (Name differences account for some MISSes —
e.g. `ncat`→`nmap-ncat` — and are worth reclaiming case-by-case, but the macro picture holds.)

## Glass bundle taxonomy (adapted, not copied)

We keep Kali's category names (familiarity + menu compatibility) but each Glass bundle
declares BOTH an `rpm:` list (verified-in-Fedora subset) AND a `containers:` reference
(a distrobox image in `glass-containers` carrying the unpackaged majority).

Offensive (kill-chain ordered):
```
information-gathering  vulnerability  web  database  passwords
exploitation  post-exploitation  sniffing-spoofing  social-engineering
reverse-engineering  fuzzing  forensics
```
Wireless / RF / hardware:
```
wireless  802-11  bluetooth  sdr  rfid  hardware  voip
```
Defensive (Kali Purple / NIST CSF) — optional, Glass's differentiator for blue-team:
```
identify  protect  detect  respond  recover  reporting
```
Support:
```
top10  windows-resources  crypto-stego  gpu
```

## Glass editions (mapped from Kali)

| Glass edition | Kali analogue | Bundles |
|---------------|---------------|---------|
| `base` | kali-linux-headless-ish | networking + host-friendly foundation |
| `standard` | kali-linux-default | top10 + information-gathering + web + passwords + wireless + vulnerability |
| `large` | kali-linux-large | standard + forensics + reversing + exploitation + post-exploitation + sniffing + database + hardware + sdr + rfid + bluetooth + 802-11 + voip |
| `everything` | kali-linux-everything | all bundles incl. defensive/Purple set |

## Container mapping (glass-containers repo)

One distrobox image per heavy/unpackaged bundle, tagged `ghcr.io/goshenite-systems/<name>-lab`:
`web-lab, exploitation-lab, vulnerability-lab, forensics-lab, reversing-lab,
osint-lab (information-gathering), passwords-lab, wireless-lab, voip-lab, windows-lab`.
Base these on Kali or a pip/go-heavy Fedora — a Kali-based distrobox gives instant access
to the 72% that Fedora lacks, while the host stays immutable Aurora/Bluefin.
