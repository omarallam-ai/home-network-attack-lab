#!/usr/bin/env python3
"""
ARP Spoof Detector
Monitors ARP traffic on the local network and alerts on indicators
of ARP cache poisoning / MITM attacks.

Requirements: scapy
Install:      pip install scapy
Run:          sudo python3 arp-spoof-detector.py
"""

from scapy.all import ARP, sniff
from collections import defaultdict
import time


# Tracks IP -> set of MACs seen
ip_mac_map = defaultdict(set)

# Tracks alert timestamps to avoid flooding output
last_alert = {}
ALERT_COOLDOWN = 10  # seconds


def check_arp_packet(packet):
    if not packet.haslayer(ARP):
        return

    arp = packet[ARP]

    # Only inspect ARP replies (op=2) — these are what poisoning uses
    if arp.op != 2:
        return

    src_ip  = arp.psrc
    src_mac = arp.hwsrc.lower()

    if not src_ip or not src_mac:
        return

    ip_mac_map[src_ip].add(src_mac)

    # Alert if more than one MAC claims to own this IP
    if len(ip_mac_map[src_ip]) > 1:
        now = time.time()
        if now - last_alert.get(src_ip, 0) > ALERT_COOLDOWN:
            last_alert[src_ip] = now
            macs = ", ".join(ip_mac_map[src_ip])
            print(f"\n[!] ALERT — Possible ARP spoofing detected")
            print(f"    IP address : {src_ip}")
            print(f"    MACs seen  : {macs}")
            print(f"    Time       : {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"    Action     : Verify ARP table with 'arp -a' or 'ip neigh show'")


def main():
    print("ARP Spoof Detector — listening for ARP replies")
    print("Press Ctrl+C to stop\n")
    sniff(
        filter="arp",
        prn=check_arp_packet,
        store=False
    )


if __name__ == "__main__":
    main()
