# Detection Scripts

Lightweight scripts written alongside this lab to detect the attacks documented here.
Each script is self-contained and runnable on any Linux machine with the listed dependency.

| Script | Detects | Dependency |
|--------|---------|------------|
| `arp-spoof-detector.py` | ARP cache poisoning / MITM | scapy |

## Usage

```bash
pip install scapy
sudo python3 arp-spoof-detector.py
```

Requires root/sudo because raw socket access is needed to capture ARP frames.

## Why these scripts exist

Writing a detection tool after running an attack forces a different kind of thinking —
you have to understand the attack well enough to know exactly what artifact it leaves
behind. These are not production-grade tools; they are learning artifacts that
demonstrate the attacker-to-defender translation this lab is built around.
