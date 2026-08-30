# Responsible AI Log — NetSage AI

**Total cases reviewed:** 30
**Accepted:** 22
**Edited:** 3
**Rejected:** 5
**Total corrected by human reviewer:** 8 (requirement: at least 5)

---

## Cases Where the AI Was Corrected

### Case V3 — VLAN — **Rejected**

**AI's diagnosis:** DHCP server pool for VLAN 10 is exhausted, so the new PC on Fa0/6 cannot obtain an address (confidence: medium)

**Actual root cause:** Fa0/6 is still on default VLAN 1, never configured for VLAN 10

**Why the AI was wrong / needed correction:**
AI jumped to a DHCP exhaustion guess without checking the port's VLAN assignment first. The actual show interfaces Fa0/6 switchport output clearly showed Access Mode VLAN: 1 (default) - the port was never moved to VLAN 10 at all, so it was never even requesting from the right DHCP scope. AI ignored the port-level evidence it wasn't given yet and guessed based on symptom alone.

---

### Case G4 — Gateway — **Edited**

**AI's diagnosis:** The network cable connecting the PC is physically damaged and needs replacement (confidence: medium)

**Actual root cause:** High CRC/input errors suggest a duplex mismatch, not necessarily a bad cable

**Why the AI was wrong / needed correction:**
AI's evidence use was too vague ('high error count') and it also skipped past duplex mismatch as a possibility, jumping straight to 'bad cable'. In Packet Tracer / real Cisco gear, a duplex mismatch produces the exact same CRC/input error signature as a bad cable, so the AI's confidence should have been lower and its next_command should have been 'show interfaces Fa0/8 | include duplex' before recommending a physical fix. Reviewer added duplex-check as an intermediate step before cable replacement.

---

### Case D4 — DHCP — **Edited**

**AI's diagnosis:** A rogue device is spoofing an existing IP address to intentionally disrupt network traffic (confidence: medium)

**Actual root cause:** A statically assigned PC is using an address inside the active DHCP pool range - not malicious, just misconfiguration

**Why the AI was wrong / needed correction:**
AI over-escalated a simple misconfiguration into a security incident ('rogue device', 'malicious intent') without evidence supporting intent. show ip dhcp conflict only proves an address conflict exists, not who or why. The far more common and boring explanation - someone manually set a static IP inside the DHCP pool's range - fits the evidence just as well and should have been the primary hypothesis, with malicious activity only escalated to if further evidence (e.g. repeated conflicts, unknown MAC vendor) showed up. Reviewer downgraded the framing to a config issue and kept the same fix intent (find and reassign the conflicting device).

---

### Case N6 — DNS — **Rejected**

**AI's diagnosis:** The DNS server for the Guest VLAN is down or misconfigured, causing resolution failures only from that VLAN (confidence: medium)

**Actual root cause:** ACL explicitly blocks UDP port 53 (DNS) from the Guest subnet - not a DNS server issue at all

**Why the AI was wrong / needed correction:**
AI never checked for an ACL even though the topology note explicitly mentioned an ACL was recently applied to the Guest VLAN. The actual evidence (show access-lists GUEST_ACL) clearly shows 'deny udp 192.168.40.0 0.0.0.255 any eq 53' - a direct block of DNS traffic. The AI defaulted to blaming the DNS server itself, which contradicts the fact that DNS works fine from every other VLAN. This is a case where the AI didn't use all the evidence available to it (the topology note) before answering.

---

### Case R5 — Routing — **Rejected**

**AI's diagnosis:** A firewall on the return path is blocking inbound traffic back to the internal PCs (confidence: medium)

**Actual root cause:** Default route and NAT outside interface are mismatched (two different ISP links), causing asymmetric routing - not a firewall issue

**Why the AI was wrong / needed correction:**
AI assumed a firewall without any ACL evidence being shown, when the actual show ip route and NAT config directly showed the real cause: the default route pointed out one ISP interface while NAT/PAT was applied to a different interface entirely. This is a classic asymmetric routing problem, not a firewall block - a firewall would typically show explicit deny log entries, which weren't present. The AI reached for a plausible-sounding but unsupported explanation instead of using the specific routing/NAT evidence given.

---

### Case A3 — ACL — **Edited**

**AI's diagnosis:** ACL 103 is correctly blocking a specific problematic host as intended by the administrator (confidence: low)

**Actual root cause:** Wildcard mask denies the entire /24 subnet (0.0.0.255) instead of a single host - this is a misconfiguration, not intended behavior

**Why the AI was wrong / needed correction:**
AI's own evidence field actually shows the exact wildcard mask that proves the mistake (0.0.0.255 = whole subnet, not a single host), but the AI's root_cause and fix contradicted its own evidence by assuming this was intentional. Low confidence was appropriate given the ambiguity, but the AI should have flagged the wildcard math itself as suspicious rather than deferring entirely to 'ask the admin.' Reviewer corrected the root_cause to identify the wildcard mask error directly, since the math is unambiguous even without additional context.

---

### Case T3 — NAT — **Rejected**

**AI's diagnosis:** Port forwarding was never configured for the web server at all, so external requests have nowhere to go (confidence: medium)

**Actual root cause:** A port forward rule already exists but maps to the wrong internal port (8080 instead of 80) - not missing entirely

**Why the AI was wrong / needed correction:**
The AI's own next_command output would have shown an existing static NAT rule ('ip nat inside source static tcp 192.168.10.100 8080 203.0.113.5 80'), but the AI's root_cause claimed no rule existed at all - it didn't actually check before answering. The real issue is a port mismatch (internal port 8080 vs the server's actual port 80), a much smaller fix than recreating the whole rule from scratch. This is a case where the AI skipped verifying evidence before committing to a root cause.

---

### Case W4 — Wireless — **Rejected**

**AI's diagnosis:** Wireless clients are entering an incorrect Wi-Fi password, so authentication is failing on the client side (confidence: low)

**Actual root cause:** RADIUS server is unreachable - show radius statistics shows 50 requests, 50 timeouts, 0 responses, so authentication never actually completes regardless of password correctness

**Why the AI was wrong / needed correction:**
AI took the client-facing error message ('incorrect password') at face value instead of checking server-side evidence. The show radius statistics output - which the AI should have requested and checked before answering - shows 100% timeouts with zero responses, meaning the RADIUS server itself isn't answering at all. No password would work in this state, correct or not. This is a case where the AI's low confidence was actually a good signal that it should have looked for more evidence (i.e., its own suggested next_command) before committing to a root cause, rather than defaulting to the most user-blame-friendly explanation.

---
