# Skills & Learning

This repository is part of a broader effort to build practical, hands-on cybersecurity
skills on top of structured learning. This page maps formal knowledge to applied work.

---

## Google Cybersecurity Certificate
**Issued:** April 29, 2026 — Google / Coursera

The certificate covers eight domains: security foundations, network security, Linux and
SQL for security, assets and threats, detection and response, Python automation, and
putting it all together in a capstone. Below is where each domain shows up in real work
across this repository and the wider portfolio.

| Certificate Domain | Applied In |
|---|---|
| Network security fundamentals | ARP spoofing attack chain, detection logic, hardening guidance |
| Linux command line | All attacks — Kali tooling, airmon-ng, ettercap, aircrack-ng |
| Incident detection & response | Analysis notes written in SOC analyst style; IOC documentation |
| Security hardening | Prevention sections across all three attack files |
| Python for security automation | [`arp-spoof-detector.py`](detection/arp-spoof-detector.py) — detection script built post-attack |
| Threats, assets & vulnerabilities | Threat modelling in each attack's "what the attacker gains" section |
| SIEM & log analysis | [Log-Analysis-Automation-Script](https://github.com/omarallam-ai/Log-Analysis-Automation-Script) |
| Traffic analysis | [warmcookie-malware-analysis](https://github.com/omarallam-ai/warmcookie-malware-analysis) — Wireshark forensics |

The certificate provided the conceptual framework. This repository and the rest of the
portfolio represent that framework applied to real tools, real traffic, and real networks.

---

## Broader Portfolio Map

| Area | Formal Learning | Hands-On Work |
|---|---|---|
| Network forensics | Google Cert — network security | warmcookie-malware-analysis |
| Threat intelligence | Google Cert — threats & assets | SentinelSync |
| SIEM / log analysis | Google Cert — detection & response | Log-Analysis-Automation-Script |
| Network defence | Google Cert — hardening | network-segmentation-security-lab |
| Offensive techniques | Self-directed home lab | This repository |
| Detection engineering | Google Cert + self-directed | arp-spoof-detector.py, IOC documentation |

---

## Current Focus

Developing detection engineering skills — writing detection logic from first-hand
knowledge of how attacks execute, rather than from documentation alone. The attacker
mindset gained in this lab directly informs the defensive tooling and analysis work
across the rest of the portfolio.
