# 01. ARP Spoofing / MITM

**Category:** LAN / Layer 2  
**Tools:** Ettercap, Wireshark, apackets.com  
**Status:** ✅ Completed  
**MITRE ATT&CK:** [T1557.002 — ARP Cache Poisoning](https://attack.mitre.org/techniques/T1557/002/)

---

## Overview

ARP (Address Resolution Protocol) maps IP addresses to MAC addresses on a local network.
It is stateless and unauthenticated — any host can send an ARP reply at any time, and
other hosts will accept it without verification. ARP spoofing exploits this by flooding
the network with forged ARP replies, poisoning the ARP caches of target devices and
redirecting their traffic through the attacker's machine.

The result is a Man-in-the-Middle (MITM) position: the attacker sits invisibly between
two communicating hosts, able to read, modify, or drop traffic in transit.

---

## How It Works

1. The attacker sends a crafted ARP reply to the **victim** claiming: *"The gateway's IP is at my MAC address."*
2. The attacker simultaneously sends a crafted ARP reply to the **gateway** claiming: *"The victim's IP is at my MAC address."*
3. Both devices update their ARP caches with the poisoned entries.
4. Traffic from the victim to the gateway (and vice versa) now routes through the attacker.
5. The attacker enables IP forwarding so traffic continues flowing — making the attack invisible to the victim.

---

## Attack Flow

```
Normal traffic:
  [Victim] ──────────────────────────► [Gateway] ──► [Internet]

After ARP poisoning:
  [Victim] ──► [Attacker (Kali)] ──► [Gateway] ──► [Internet]
                      │
                 captures all
                 passing traffic
                 (Wireshark)

ARP Cache on Victim (poisoned):
  Gateway IP  →  Attacker MAC   ← injected by Ettercap
  
ARP Cache on Gateway (poisoned):
  Victim IP   →  Attacker MAC   ← injected by Ettercap
```

---

## Tools Used

### Ettercap
Ettercap automates the ARP poisoning process. It handles sending the forged ARP replies
at regular intervals (to maintain the poisoned cache entries as devices refresh), and
optionally enables IP forwarding so traffic continues flowing through the attacker.

Running a unified sniff against two targets on the LAN, Ettercap continuously re-poisons
both the victim and gateway, sustaining the MITM position for the duration of the session.

### Wireshark
With the MITM position established, Wireshark captures all traffic flowing through the
attacker's interface. This produces a full packet capture of the victim's unencrypted
network activity — HTTP requests, DNS queries, plaintext credentials, and so on.

### apackets.com
The captured traffic was uploaded to [apackets.com](https://apackets.com) for visual
analysis — it parses pcap files and presents sessions, protocols, and extracted data
in a readable format, making it straightforward to identify what was intercepted.

---

## What the Attacker Gains

With a successful MITM position and traffic capture, the attacker can observe:

- All **unencrypted HTTP traffic** — URLs visited, form data, session cookies
- **DNS queries** — every domain the victim resolves, revealing browsing patterns
- **Plaintext credentials** — any login submitted over HTTP (not HTTPS)
- **Device fingerprinting data** — OS, browser, device type from HTTP User-Agent headers
- **Internal network topology** — IPs, hostnames, MAC addresses visible in captured traffic

In this lab, captured traffic was analyzed via apackets.com and confirmed that full
session visibility was achieved. Raw captures are excluded from this repository.

> **Key insight:** HTTPS encrypts the payload, but DNS queries, SNI fields in TLS
> handshakes, and traffic metadata (destination IPs, timing, volume) remain visible
> even over encrypted connections — a MITM position still leaks significant information.

---

## Detection

### ARP Cache Anomalies

The most reliable indicator is a duplicate MAC address in the ARP table — the attacker's
MAC appears for multiple IPs (both the victim and the gateway, or both the gateway and
a host).

Check on Windows:
```
arp -a
```
Check on Linux:
```
ip neigh show
```

A healthy ARP table has one unique MAC per IP. If the gateway IP and another host IP
share the same MAC, ARP spoofing is likely in progress.

### Network-Level IOCs

| Indicator | What It Looks Like |
|-----------|-------------------|
| Gratuitous ARP flood | High volume of ARP replies not preceded by ARP requests |
| Duplicate MAC in ARP table | Same MAC address resolves two different IPs |
| ARP reply without request | Broadcast ARP replies appearing spontaneously |
| Traffic latency spike | Extra hop through attacker adds measurable delay |

### Wireshark Detection Filter

To identify ARP spoofing in a packet capture:
```
arp.duplicate-address-detected
```
or manually flag suspicious ARP activity:
```
arp.opcode == 2 && arp.src.hw_mac != <expected_gateway_mac>
```

### SIEM / IDS Rules

- Alert on gratuitous ARP replies (ARP opcode 2 sent without a preceding request)
- Alert when the same MAC address is seen resolving two or more different IP addresses
- Alert on ARP reply rate exceeding baseline for a host

---

## Prevention & Hardening

### Dynamic ARP Inspection (DAI)

On managed switches, DAI validates ARP packets against a DHCP snooping binding table.
Only ARP replies matching a known IP/MAC/port binding are forwarded — forged replies
are dropped at the switch level. This is the most effective network-layer control.

### Static ARP Entries

For critical devices (gateway, DNS server, domain controller), configure static ARP
entries on endpoints. Static entries cannot be overwritten by spoofed ARP replies.

```bash
# Linux — set static ARP entry for gateway
sudo arp -s <gateway_ip> <gateway_mac>

# Windows
netsh interface ip add neighbors "Ethernet" <gateway_ip> <gateway_mac>
```

Note: This does not scale to large networks but is practical for critical hosts.

### Encrypted Protocols

ARP spoofing gives the attacker traffic visibility — not decryption capability.
Enforcing encrypted protocols limits what they can read:

- **HTTPS everywhere** — use HSTS to prevent downgrade attacks
- **DNS over HTTPS (DoH) / DNS over TLS (DoT)** — encrypt DNS queries
- **VPN / WireGuard** — encrypts all traffic end-to-end, rendering MITM capture useless

### Network Segmentation

Isolate sensitive devices into separate VLANs. ARP spoofing is constrained to the
broadcast domain — an attacker on the guest VLAN cannot poison ARP caches on the
corporate or IoT VLAN.

### ARP Monitoring Tools

- **XArp** — Windows/Linux tool that monitors ARP traffic and alerts on spoofing
- **arpwatch** — Linux daemon that logs ARP activity and emails on anomalies
- **Snort / Suricata** — IDS rules available for ARP flood and gratuitous ARP detection

---

## References

- [MITRE ATT&CK T1557.002](https://attack.mitre.org/techniques/T1557/002/)
- [RFC 826 — An Ethernet Address Resolution Protocol](https://datatracker.ietf.org/doc/html/rfc826)
- [Ettercap Documentation](https://www.ettercap-project.org/documentation.html)
- [Cisco — Understanding and Configuring Dynamic ARP Inspection](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst6500/ios/12-2SX/configuration/guide/book/dynarp.html)
