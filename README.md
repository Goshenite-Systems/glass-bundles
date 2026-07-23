# glass-bundles

> Declarative security-tool **bundle manifests** for [Goshenite Linux](https://github.com/Goshenite-Systems/glass) — the single source of truth for what each edition ships.

**Status:** 🚧 early bootstrap.

---

## Concept

Kali organizes tools into layered metapackages (`kali-linux-everything` → `kali-tools-*` → packages). Goshenite preserves that excellent organizational model but replaces Debian metapackages with **declarative YAML manifests** that can describe far more than packages:

```
glass-everything
      ↓
ublue-sec-tools-*   (bundles)
      ↓
RPMs · Flatpaks · OCI/distrobox containers · config · desktop entries · docs · helper scripts
```

A bundle is **not limited to packages** — that is the key improvement over Kali.

## Manifest format

Each bundle is one YAML file. Example (`bundles/web.yaml`):

```yaml
name: web
description: Web application assessment tooling
category: Web

rpm:
  - sqlmap
  - gobuster
  - nikto
  - wafw00f

flatpak:
  - us.zoom.Zoom          # example; real IDs resolved at build

containers:
  - ghcr.io/goshenite-systems/web-lab

desktop:
  - web.menu             # generated categorized menu entries

config:
  - aliases: shell aliases sourced into the profile
  - defaults: default tool configs dropped into system_files/
```

This manifest is consumed by the generator in [`glass`](https://github.com/Goshenite-Systems/glass) to emit Containerfile RUN blocks, flatpak `preinstall.d` stanzas, distrobox assembles, and categorized `.desktop` menus.

## Planned bundles

```
networking   wireless   web        passwords   osint
forensics    reversing  malware    cloud       ad
hardware     sdr        rfid       mobile      firmware   ai
```

## Editions

Editions are just curated sets of bundles:

| Edition | Bundles |
|---------|---------|
| **Standard** | selected core bundles |
| **Large** | more bundles |
| **Everything** | all bundles |

## Reality checks (why manifests, not raw RPM lists)

- **Not every Kali tool has a Fedora RPM.** Bundles prefer COPR/Terra or an OCI container over inventing an RPM. Fast-moving offensive tooling → `containers:`, not `rpm:`.
- **Flatpaks are not layered into the image.** The generator emits `preinstall.d` stanzas + a first-boot unit; it never runs `flatpak install` in the Containerfile.
- **Wireless/SDR kmods** are host-side (akmods), tracked separately in `glass-akmods` — a bundle references them but does not build them.

## License

[Apache-2.0](./LICENSE)
