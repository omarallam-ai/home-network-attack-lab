
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
import threading

# Tracks IP -> set of MACs seen
ip_mac_map = defaultdict(set)
# Tracks alert timestamps to avoid flooding output
last_alert = {}
ALERT_COOLDOWN = 10  # seconds
packet_count = 0

def check_arp_packet(packet):
    global packet_count
    if not packet.haslayer(ARP):
        return

    arp = packet[ARP]
    packet_count += 1  # count every ARP packet seen

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

def heartbeat():
    """Prints a status line every 15 seconds so you know it's alive."""
    while True:
        time.sleep(15)
        print(f"[*] Still monitoring... ARP packets captured so far: {packet_count}")

def main():
    print("ARP Spoof Detector — listening for ARP replies")
    print("Press Ctrl+C to stop\n")

    # Start heartbeat in background
    t = threading.Thread(target=heartbeat, daemon=True)
    t.start()

    sniff(
        filter="arp",
        prn=check_arp_packet,
        store=False
    )

if __name__ == "__main__":
    main()
