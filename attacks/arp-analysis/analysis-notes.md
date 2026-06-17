# ARP Spoofing — Traffic Analysis Notes

**Tool:** apackets.com (pcap analysis)  
**Capture method:** Wireshark on attacker interface during active MITM session  
**Raw capture:** Excluded from repository (home network privacy)

---

## What This Documents

After establishing the MITM position with Ettercap, I captured the redirected traffic
in Wireshark and uploaded the pcap to apackets.com for structured analysis. These are
my observations from that output — written the way I'd document findings in a SOC context.

---

## Protocol Distribution

The protocol breakdown confirmed the MITM position was fully established — traffic from
the victim device was visibly flowing through the attacker machine before reaching the
gateway.

The capture showed a realistic mix of modern home network traffic:

- **DNS** queries made up a significant share of the early capture — device resolving
  domains before any HTTP connection was established. This alone reveals browsing intent
  even before a single webpage loads.
- **HTTP** traffic was present and fully readable in plaintext. Any site not enforcing
  HTTPS exposed its full request/response cycle.
- **TCP** connection setup (SYN/SYN-ACK/ACK) was visible for each session, showing
  destination IPs and ports before any application-layer data appeared.
- Encrypted traffic (TLS) was also present — confirming that HTTPS protects payload
  content, but destination metadata (IP, SNI, timing) remains visible even through
  an established MITM.

---

## DNS Observation

DNS queries were the most revealing category. Before any HTTP request is made, the
victim device issues a DNS query for the destination domain — and since DNS is
unencrypted by default, every domain the victim attempted to reach appeared in plaintext
in the capture.

This is significant from a detection standpoint: even if all subsequent traffic is
encrypted, a passive MITM position on DNS alone creates a near-complete browsing profile
of the victim.

**Defensive implication:** DNS over HTTPS (DoH) or DNS over TLS (DoT) would have
encrypted these queries, eliminating this visibility entirely.

---

## HTTP Traffic Observation

HTTP requests appeared in full — including request headers, User-Agent strings, and
the URLs being accessed. The User-Agent header alone revealed the victim device's
operating system and browser version without any active fingerprinting.

For any service not enforcing HTTPS, full request bodies would also be exposed —
including form submissions and session tokens passed via URL parameters.

**Defensive implication:** HSTS (HTTP Strict Transport Security) and HTTPS enforcement
at the application level are the correct controls here. The MITM position itself is
neutralised if the payload is encrypted, though metadata exposure remains.

---

## Key Takeaway

The capture validated the theoretical attack model: a MITM position on a LAN gives the
attacker passive visibility into DNS and unencrypted HTTP traffic with zero interaction
from the victim. The victim device behaved completely normally throughout — no alerts,
no connection errors, no indication of interception.

From a SOC perspective, the only way to detect this after the fact is through ARP cache
anomalies or network-level monitoring — the traffic itself gives no signal to the victim.
