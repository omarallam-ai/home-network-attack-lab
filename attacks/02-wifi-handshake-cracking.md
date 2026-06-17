# 02. WiFi Handshake Capture & Cracking

**Category:** Wireless  
**Tools:** airmon-ng, airodump-ng, aireplay-ng, aircrack-ng, hashcat  
**Status:** ✅ Completed  
**MITRE ATT&CK:** [T1040 — Network Sniffing](https://attack.mitre.org/techniques/T1040/), [T1110.002 — Password Cracking](https://attack.mitre.org/techniques/T1110/002/)

---

## Overview

WPA2-Personal authenticates clients using a 4-way handshake. This handshake does not
transmit the password directly — instead, both sides prove knowledge of the Pre-Shared
Key (PSK) by deriving a session key (PTK) from it. The handshake itself can be captured
passively from the air by any device in monitor mode within radio range.

Once captured, the handshake can be taken fully offline and attacked at arbitrary speed
using wordlists or brute force — no further interaction with the network required. The
weakness is not in WPA2's cryptography; it is in the human tendency to choose weak or
common passwords that appear in wordlists.

---

## How It Works

### Phase 1 — Monitor Mode

The USB WiFi adapter is placed into monitor mode, which allows it to capture raw 802.11
frames from all nearby networks rather than associating with a specific AP.

### Phase 2 — Handshake Capture

The attacker targets a specific BSSID (AP MAC address) and channel with airodump-ng,
which records all frames on that channel. A valid 4-way handshake occurs naturally when
a client connects or reconnects to the network.

To speed this up, aireplay-ng sends deauthentication frames to a connected client,
forcing it to disconnect and automatically reconnect — triggering a new handshake
within seconds.

### Phase 3 — Offline Cracking

The captured handshake (`.cap` file) is taken offline. The attacker computes candidate
PTKs by hashing guessed passwords through the WPA2 key derivation function (PBKDF2-SHA1
with the SSID as salt, 4096 iterations), comparing the result against values in the
captured handshake. A match means the guessed password is the real PSK.

---

## Attack Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Set adapter to monitor mode                       │
│  airmon-ng start wlan0  →  wlan0mon                         │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  Phase 2: Target network and capture handshake              │
│  airodump-ng --bssid <AP_MAC> --channel <CH> wlan0mon       │
│                                                             │
│  (optional deauth to force reconnection)                    │
│  aireplay-ng --deauth 5 -a <AP_MAC> wlan0mon                │
│                                                             │
│  ★ WPA handshake captured  →  capture.cap                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  Phase 3A: Wordlist attack (aircrack-ng)                    │
│  aircrack-ng -w wordlist.txt -b <AP_MAC> capture.cap        │
│                                                             │
│  Result: KEY NOT FOUND — wordlist exhausted                 │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│  Phase 3B: Brute force (hashcat — GPU accelerated)          │
│  Convert: hccapx format required for hashcat                │
│  hashcat -m 2500 capture.hccapx ?a?a?a?a?a?a?a?a           │
│                                                             │
│  (Not executed — password strength already confirmed)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Tools Used

### airmon-ng
Manages wireless adapter modes. Kills conflicting processes (NetworkManager, wpa_supplicant)
and switches the adapter into monitor mode, creating a `wlan0mon` virtual interface that
receives raw 802.11 frames.

### airodump-ng
Passive wireless frame capture. Tuned to a specific BSSID and channel, it records all
802.11 frames including the 4-way handshake when a client authenticates.

### aireplay-ng
Injects deauthentication frames. Sending a deauth to a connected client forces it off
the network, and its automatic reconnection triggers a new handshake — reducing capture
time from "wait for natural reconnection" to seconds.

### aircrack-ng
Dictionary-based WPA2 cracking. Reads a captured `.cap` file and tests candidate
passwords from a wordlist by recomputing the handshake HMAC values. CPU-based;
fast for common passwords, slow for complex ones.

**Result in this lab:** Wordlist exhausted without a match — the real network password
was not present in the wordlist used.

### hashcat (studied, not executed)
GPU-accelerated cracking engine. Hashcat with `-m 22000` (WPA2) can test billions of
candidates per second using a GPU. The password was not subjected to hashcat because
the wordlist failure already confirmed the password's strength — running a full brute
force was unnecessary given the known outcome.

Understanding hashcat's capability is the important takeaway: a weak password
(even one not in a wordlist, but short or low-complexity) will fall to mask attacks
in minutes on consumer GPU hardware.

---

## What the Attacker Gains

A captured WPA2 handshake gives the attacker:

- **The PSK** (if crackable) — full WiFi network access, equivalent to any connected device
- **Network access** — ability to join the network, reach LAN devices, and potentially
  pivot to internal services
- **Passive traffic visibility** — once on the network, the attacker can perform further
  attacks (ARP spoofing, DNS poisoning) against other connected devices

> **Key insight:** The handshake can be captured in seconds without ever connecting
> to the network, and cracking happens entirely offline. The AP is never alerted.
> There is no failed login counter, no lockout, no notification to the network owner.

---

## Detection

Detecting handshake capture is difficult because it is a **passive attack** — the
attacker is only listening during capture. The deauthentication injection phase, however,
is detectable.

### Deauthentication Attack IOCs

| Indicator | What It Looks Like |
|-----------|-------------------|
| Deauth frame flood | High volume of 802.11 deauthentication frames (subtype 0x0C) |
| Client disconnection spike | Multiple devices disconnecting and reconnecting in short succession |
| Unassociated deauth source | Deauth frames from a MAC not associated to the AP |
| Monitor mode probe | Nearby device sending probe requests without attempting association |

### Wireless IDS Detection

Dedicated wireless IDS solutions (Kismet, WIDS built into enterprise APs) can detect:

- Deauthentication floods from unknown source MACs
- Clients in monitor mode (detectable via probe behavior)
- Passive sniffers near the network (some chipsets leak identifiable frames)

Most consumer routers do not log or alert on deauthentication events — this is a
significant gap in home network visibility.

### SIEM / Log Indicators

On enterprise wireless infrastructure:

- Alert on excessive client disconnection events within a short window
- Alert on deauthentication frames from MACs not in the AP's client table
- Alert on repeated authentication attempts (post-crack reconnection)

---

## Prevention & Hardening

### Use WPA3

WPA3-Personal replaces the PSK exchange with SAE (Simultaneous Authentication of Equals),
which is resistant to offline dictionary attacks. Even if the 4-way handshake equivalent
is captured, SAE does not expose a value that can be cracked offline.

If all devices support it, migrate to WPA3. Mixed WPA2/WPA3 transition mode is available
on most modern routers.

### Strong Passphrase

If WPA3 is not available, the only defense against offline cracking is passphrase
complexity. Wordlists cover common passwords, names, dates, and dictionary words.
A password that is long, random, and not dictionary-based is not crackable in any
practical timeframe.

Recommendation: 20+ character random passphrase (e.g., generated by a password manager).

At WPA2 cracking rates on a modern GPU (~1–4 billion candidates/second), a truly random
12-character mixed-case alphanumeric password has a keyspace that would take thousands
of years to exhaust.

### Disable WPS

WPS (WiFi Protected Setup) contains a PIN vulnerability (Reaver attack) that can recover
the WPA2 PSK in hours regardless of passphrase strength. Disable WPS in the router admin panel.

### Network Segmentation

Even if an attacker cracks the WiFi password, VLAN segmentation limits what they can
reach. IoT devices, guest networks, and critical devices should be on separate VLANs
with firewall rules between them.

### Monitor Client Connections

Enable logging on the router (if supported) to detect unexpected device connections.
A new unknown MAC address connecting after an extended offline cracking period is an
indicator of compromise.

---

## References

- [MITRE ATT&CK T1040](https://attack.mitre.org/techniques/T1040/)
- [MITRE ATT&CK T1110.002](https://attack.mitre.org/techniques/T1110/002/)
- [Aircrack-ng Documentation](https://www.aircrack-ng.org/documentation.html)
- [Hashcat WPA2 Wiki](https://hashcat.net/wiki/doku.php?id=hashcat)
- [WPA3 Specification — Wi-Fi Alliance](https://www.wi-fi.org/discover-wi-fi/security)
- [RFC 4764 — WPA2 Key Hierarchy](https://datatracker.ietf.org/doc/html/rfc4764)
