# Home Network Attack Lab

**Type:** Offensive Security Research / Defensive Analysis  
**Environment:** Personal home network — owned devices only  
**Goal:** Build an attacker mindset to become a better defender

---

## Overview

This repository documents network attacks I performed against my own home network
as part of building hands-on offensive security knowledge. Every technique studied
here is paired with detection guidance and defensive countermeasures — because
understanding how attacks work is the foundation of effective defense.

The lab follows a consistent structure: **how it works → what the attacker gains →
how to detect it → how to stop it.** The repo is designed to grow; new attacks are
added as a numbered entry following the same template.

> **Note:** No screenshots are included. All experiments were conducted on personally
> owned devices on a private network. Raw captures and sensitive artifacts are excluded
> to protect home network privacy.

---

## Motivation

Most of my existing work is on the defensive side — SOC workflows, detection
engineering, threat intelligence. This lab exists to close the gap. Knowing how ARP
poisoning is actually executed makes writing a detection rule for it meaningful.
Knowing how WPA2 handshakes are cracked makes enforcing password policy feel urgent.

---

## Environment

| Component        | Detail                                      |
|-----------------|---------------------------------------------|
| Network type     | Home LAN (private, all devices owned)       |
| Attacker machine | Kali Linux                                  |
| WiFi adapter     | USB adapter with monitor mode / injection support |
| Targets          | Personal devices on same subnet             |
| Captures         | Excluded from repo for privacy              |

---

## Attack Index

| # | Attack | Category | Tools | Status |
|---|--------|----------|-------|--------|
| 01 | [ARP Spoofing / MITM](attacks/01-arp-spoofing.md) | LAN / Layer 2 | Ettercap | ✅ Completed |
| 02 | [WiFi Handshake Capture & Cracking](attacks/02-wifi-handshake-cracking.md) | Wireless | airmon-ng, aircrack-ng, hashcat | ✅ Completed |
| 03 | [Evil Twin / Rogue AP](attacks/03-evil-twin-rogue-ap.md) | Wireless | Fluxion (studied) | 🔬 Partial — single adapter |

---

## Repository Structure

```
home-network-attack-lab/
├── README.md
├── disclaimer.md
├── attacks/
│   ├── 01-arp-spoofing.md
│   ├── 02-wifi-handshake-cracking.md
│   └── 03-evil-twin-rogue-ap.md
└── setup/
    └── lab-environment.md
```

## Skills Demonstrated

- Active reconnaissance and LAN-level exploitation (ARP, MITM)
- Wireless security assessment (monitor mode, handshake capture, offline cracking)
- Threat modeling from an attacker's perspective
- Writing detection logic and hardening guidance from first-hand attack knowledge
- Structured documentation of security research

---

## Related Projects

| Repo | Focus |
|------|-------|
| [warmcookie-malware-analysis](https://github.com/omarallam-ai/warmcookie-malware-analysis) | SOC-style traffic forensics |
| [SentinelSync](https://github.com/omarallam-ai/SentinelSync) | Threat intelligence enrichment CLI |
| [Log-Analysis-Automation-Script](https://github.com/omarallam-ai/Log-Analysis-Automation-Script) | Python SIEM tooling |
| [network-segmentation-security-lab](https://github.com/omarallam-ai/network-segmentation-security-lab) | VLAN/ACL defensive lab |

---

*All research conducted ethically on owned infrastructure. See [disclaimer.md](disclaimer.md) for full legal and ethical context.*
