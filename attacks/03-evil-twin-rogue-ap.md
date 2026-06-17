# 03. Evil Twin / Rogue AP

**Category:** Wireless  
**Tools:** Fluxion (studied), hostapd, dnsmasq  
**Status:** 🔬 Partial — requires 2 WiFi adapters; studied Fluxion's full attack chain  
**MITRE ATT&CK:** [T1557 — Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/), [T1566 — Phishing](https://attack.mitre.org/techniques/T1566/)

---

## Overview

An Evil Twin attack creates a rogue WiFi access point that impersonates a legitimate
network. The attacker clones the target AP's SSID (and optionally its BSSID/MAC address),
then forces clients off the real network using deauthentication frames. Clients
automatically reconnect to the strongest signal — if the rogue AP is closer or stronger,
they connect to the attacker's network instead.

Unlike passive handshake capture, this attack is interactive: the attacker hosts a
captive portal that mimics the router's login page and harvests the WPA2 password directly
from the user, bypassing the need for offline cracking entirely.

This attack requires **two WiFi adapters** — one to host the rogue AP and one to
simultaneously jam/deauthenticate the legitimate AP. With only one adapter available,
the attack was studied through Fluxion's source and documentation rather than fully
executed. The attack chain, tool internals, and defenses are documented here from
that research.

---

## How It Works

### Phase 1 — Recon

The attacker scans for nearby networks, identifying the target's SSID, BSSID (MAC),
operating channel, and connected clients. This is identical to the first phase of
handshake capture.

### Phase 2 — Clone the AP

A rogue AP is created with the same SSID as the target. Optionally, MAC address
spoofing makes the BSSID match too, making the clone indistinguishable to clients.
The rogue AP runs with no WPA2 password — it is an open network — but clients
are presented with a captive portal before getting any access.

### Phase 3 — Deauthenticate the Legitimate AP

Using the second WiFi adapter, the attacker continuously sends 802.11 deauthentication
frames to all clients associated with the real AP. This keeps legitimate clients
disconnected from the real network.

### Phase 4 — Client Connects to Rogue AP

With the legitimate AP effectively jammed, clients automatically probe for and connect
to the strongest available network with the same SSID. Because the rogue AP broadcasts
at full power nearby, clients connect to it.

### Phase 5 — Captive Portal Credential Harvest

When the client connects, all DNS queries are intercepted (DNS hijacking via dnsmasq)
and redirected to the attacker's web server. The client is presented with a page that
looks identical to the router's admin login — claiming a firmware update or
reconnection is required, and prompting for the WiFi password.

Fluxion validates submitted passwords in real time against the previously captured
WPA2 handshake — it only accepts the submission if the password matches the real hash.
This eliminates false positives and gives the attacker a confirmed valid credential.

### Phase 6 — Attack Ends

Once the correct password is submitted, Fluxion terminates the deauthentication attack,
the rogue AP comes down, and the victim reconnects to the real network — often unaware
anything happened.

---

## Attack Flow

```
  Adapter 1 (rogue AP)          Adapter 2 (deauth jammer)
        │                                  │
        ▼                                  ▼
  hostapd: broadcast            aireplay-ng: continuous
  clone of target SSID          deauth to all clients
  (open, no password)           on real AP
        │                                  │
        └──────────────┬───────────────────┘
                       │
              [Client disconnects
               from real AP]
                       │
              [Client probes for
               known SSIDs]
                       │
              [Client connects to
               rogue AP — strongest signal]
                       │
               dnsmasq intercepts
               all DNS queries
                       │
               Attacker web server
               serves fake router
               login portal
                       │
              [User enters WiFi password]
                       │
               Fluxion validates
               against captured
               handshake hash
                       │
              ✓ Password confirmed
               → Attack terminates
               → Client reconnects
                 to real AP
```

---

## Fluxion Internals (What I Learned)

Fluxion orchestrates multiple components that would otherwise require manual coordination:

**hostapd** — creates and manages the rogue AP interface, handling client associations
and 802.11 management frames.

**dnsmasq** — acts as a DHCP server (assigning IPs to connecting clients) and a DNS
server that redirects all queries to the attacker's local web server IP.

**iptables** — routes all HTTP/HTTPS traffic from connected clients to the local web
server, regardless of destination. This is what makes the captive portal intercept
all traffic rather than just specific domains.

**Python web server** — serves the phishing portal. Fluxion ships templates for common
router brands; the correct template is selected automatically based on the captured
target's network characteristics.

**WPA validator** — runs aircrack-ng in real time against each password submission.
The rogue AP stays alive until a matching credential is received.

The two-adapter requirement exists because a single adapter cannot simultaneously
broadcast as an AP and inject deauthentication frames on a different channel or in
a different mode — the hardware radio can only be in one state at a time.

---

## What the Attacker Gains

- **Plaintext WPA2 password** — obtained directly without offline cracking
- **Full network access** — equivalent to any authorized device
- **No cracking time dependency** — password strength is irrelevant; the user types it in
- **Stealth after attack** — the rogue AP disappears, leaving minimal forensic trace

> **Key insight:** This attack bypasses WPA2's cryptographic strength entirely. A
> 30-character random password falls just as easily as a weak one — the attack
> targets the human, not the cipher.

---

## Detection

### Rogue AP Detection

| Indicator | What It Looks Like |
|-----------|-------------------|
| Duplicate SSID with different BSSID | Same network name broadcasting from two MACs |
| Open network with same SSID as known network | Legitimate networks rarely drop to open auth |
| Deauth flood from non-AP MAC | Deauthentication frames not originating from the real AP |
| Sudden client disconnections | All or most clients dropping from AP simultaneously |
| Captive portal on known SSID | Browser redirected to login page on a "known" trusted network |

### Client-Side Indicators

- Being prompted for a WiFi password on a network the device previously auto-connected to
- Captive portal appearing on a home or known network (legitimate home routers do not do this)
- Browser security warnings on the portal page

### Wireless IDS

Enterprise WIDS solutions (Cisco Adaptive wIPS, Zebra AirDefense) detect:

- Rogue APs broadcasting known SSIDs from unknown BSSIDs
- Deauthentication floods
- AP impersonation (SSID + BSSID clone attempts)

---

## Prevention & Hardening

### WPA3 (Partial Mitigation)

WPA3 introduces Management Frame Protection (MFP / 802.11w), which cryptographically
signs management frames — including deauthentication frames. This makes the deauth
flood phase of the attack ineffective on WPA3-enabled networks, as clients reject
unsigned deauth frames from unknown sources.

Note: WPA3 does not prevent a rogue AP from existing, but it prevents forced
disconnection from the legitimate AP, which is required for the attack to succeed.

### Enable 802.11w (Management Frame Protection)

On WPA2 networks, enable PMF (Protected Management Frames) in the router's wireless
settings. This is available on most modern routers and provides the deauth protection
benefit without requiring full WPA3.

### User Awareness

The attack's final step depends entirely on a user submitting their password to a portal.
Key indicators to teach:

- A home router will never ask for the WiFi password via a browser popup
- Being disconnected from WiFi and immediately prompted to re-enter a password in the browser is a red flag
- Check the URL of any unexpected login page — it will be an IP address, not a domain

### Wireless Monitoring

- Periodically run `sudo iwlist scan` or use an app like WiFi Analyzer to check for
  duplicate SSIDs in your area
- Enterprise environments: deploy WIDS with rogue AP detection policies

### VPN

A VPN encrypts all traffic between the device and the VPN server, rendering the rogue
AP's position useless for traffic interception — even if the user connects, the
attacker sees only encrypted tunnel traffic.

---

## Why I Couldn't Complete This

The attack requires two WiFi adapters simultaneously:

- Adapter 1 in AP mode (hosting the rogue network via hostapd)
- Adapter 2 in monitor/injection mode (running the deauth flood)

With a single adapter, it is not possible to maintain both roles simultaneously —
the same radio cannot broadcast as an AP and inject raw 802.11 frames on another channel
at the same time. Fluxion refuses to proceed without confirming two available interfaces.

This constraint is worth noting: in a real attack scenario, both adapters are inexpensive
(~$15–30 each) and the hardware barrier is low. The gap in execution does not diminish
the relevance of the defensive guidance above.

---

## References

- [MITRE ATT&CK T1557](https://attack.mitre.org/techniques/T1557/)
- [Fluxion GitHub Repository](https://github.com/FluxionNetwork/fluxion)
- [IEEE 802.11w — Protected Management Frames](https://ieeexplore.ieee.org/document/5278657)
- [hostapd Documentation](https://w1.fi/hostapd/)
- [Wi-Fi Alliance — WPA3 Security Considerations](https://www.wi-fi.org/discover-wi-fi/security)
