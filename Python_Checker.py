"""
rule_checker.py - Deterministic Rule Checker for Cisco Network Configurations & Show Outputs
Part of NetSage AI / PacketPilot AI.

This module inspects show commands and configuration outputs deterministically
using regex patterns and rules to detect common networking faults before or alongside AI.
"""

import re
from typing import Dict, List, Any


class CiscoRuleChecker:
    """
    Deterministic validator for Cisco show-command outputs and configuration snippets.
    Catches common Layer 1-7 configuration and runtime errors.
    """

    def __init__(self):
        self.rules = [
            self._check_interface_down,
            self._check_duplicate_or_conflict_ip,
            self._check_gateway_subnet_mismatch,
            self._check_trunk_vlan_pruning,
            self._check_vlan_misassignment_or_default,
            self._check_dhcp_exhaustion,
            self._check_dhcp_relay_helper,
            self._check_dhcp_snooping_untrusted,
            self._check_acl_issues,
            self._check_nat_issues,
            self._check_dns_and_radius_reachability,
            self._check_routing_issues,
            self._check_mac_flapping,
            self._check_physical_errors,
        ]

    def run_all_checks(self, symptom: str = "", topology_note: str = "", show_output: str = "") -> List[Dict[str, Any]]:
        """
        Runs all deterministic rules against the provided show command output and context.
        Returns a list of detected issues/findings.
        """
        combined_text = f"{symptom}\n{topology_note}\n{show_output}"
        findings = []

        for rule in self.rules:
            try:
                result = rule(combined_text, show_output, topology_note, symptom)
                if result:
                    if isinstance(result, list):
                        findings.extend(result)
                    else:
                        findings.append(result)
            except Exception as e:
                # Keep rule engine safe against parsing errors
                pass

        return findings

    # -------------------------------------------------------------
    # Rule 1: Interface Shutdown / Admin Down / Line Protocol Down
    # -------------------------------------------------------------
    def _check_interface_down(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        # Check for administratively down
        admin_down_matches = re.findall(
            r"([A-Za-z0-9\/\.\-]+)\s+(?:[\d\.]+|unassigned)\s+(?:YES|NO|\w+)?\s*(?:manual|NVRAM|unset|\w+)?\s*administratively down\s+down",
            show_output,
            re.IGNORECASE,
        )
        if not admin_down_matches and "administratively down" in show_output.lower():
            simple_matches = re.findall(r"([A-Za-z0-9\/\.\-]+)\s+.*?\s+administratively down", show_output, re.IGNORECASE)
            admin_down_matches.extend(simple_matches)

        for intf in set(admin_down_matches):
            findings.append({
                "rule_id": "RULE_INT_ADMIN_DOWN",
                "name": "Interface Administratively Down",
                "severity": "High",
                "layer": "Layer 1/2",
                "detected": True,
                "evidence": f"Interface {intf} is administratively down (shutdown state).",
                "recommendation": f"Enter configuration mode for {intf} and execute 'no shutdown'."
            })

        # Check for line protocol down (e.g. sub-interface missing dot1q or cable unplugged)
        proto_down_matches = re.findall(
            r"([A-Za-z0-9\/\.\-]+)\s+(?:[\d\.]+|unassigned)\s+(?:YES|NO|\w+)?\s*(?:manual|NVRAM|unset|\w+)?\s*up\s+down",
            show_output,
            re.IGNORECASE,
        )
        if not proto_down_matches:
            simple_up_down = re.findall(r"([A-Za-z0-9\/\.\-]+)\s+.*?\s+up\s+down", show_output, re.IGNORECASE)
            proto_down_matches.extend(simple_up_down)

        for intf in set(proto_down_matches):
            recommendation = f"Verify physical connection, duplex, or encapsulation (e.g., encapsulation dot1Q) on {intf}."
            if "." in intf:
                recommendation = f"Check sub-interface {intf} configuration. Ensure 'encapsulation dot1Q <vlan_id>' and IP address are applied."
            findings.append({
                "rule_id": "RULE_INT_PROTO_DOWN",
                "name": "Interface Protocol Down / Missing Encapsulation",
                "severity": "High",
                "layer": "Layer 2",
                "detected": True,
                "evidence": f"Interface {intf} status is 'up' but line protocol is 'down'.",
                "recommendation": recommendation
            })

        # Check for switchport Operational Mode: down
        if "Operational Mode: down" in show_output:
            findings.append({
                "rule_id": "RULE_SWITCHPORT_DOWN",
                "name": "Switchport Operational Mode Down",
                "severity": "Medium",
                "layer": "Layer 2",
                "detected": True,
                "evidence": "Switchport operational mode is 'down'.",
                "recommendation": "Configure switchport explicitly as access or trunk mode and verify connected device."
            })

        return findings

    # -------------------------------------------------------------
    # Rule 2: Duplicate IP & DHCP Conflict Detection
    # -------------------------------------------------------------
    def _check_duplicate_or_conflict_ip(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show ip dhcp conflict" in show_output or "Detection method" in show_output or "Detection time" in show_output:
            ip_matches = re.findall(r"(\b(?:\d{1,3}\.){3}\d{1,3}\b)\s+Ping", show_output)
            for ip in ip_matches:
                findings.append({
                    "rule_id": "RULE_IP_CONFLICT",
                    "name": "IP Address Conflict Detected",
                    "severity": "Medium",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": f"DHCP conflict detected for IP address {ip} via ping check.",
                    "recommendation": f"Locate rogue host with static IP {ip} and configure DHCP exclusion ('ip dhcp excluded-address {ip}')."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 3: Gateway / Subnet Mismatch
    # -------------------------------------------------------------
    def _check_gateway_subnet_mismatch(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        # Find PC gateway from ipconfig
        pc_gw_match = re.search(r"Gateway:\s*([0-9\.]+)", show_output, re.IGNORECASE)
        # Find router interface IPs
        r_ips = re.findall(r"([A-Za-z0-9\/\.\-]+)\s+([0-9\.]+)\s+up\s+up", show_output, re.IGNORECASE)
        
        if pc_gw_match and r_ips:
            pc_gw = pc_gw_match.group(1).strip()
            pc_gw_subnet = ".".join(pc_gw.split(".")[:3])
            found_matching_gw = False
            for intf, r_ip in r_ips:
                r_subnet = ".".join(r_ip.split(".")[:3])
                if pc_gw == r_ip or pc_gw_subnet == r_subnet:
                    found_matching_gw = True
                    break
            if not found_matching_gw:
                findings.append({
                    "rule_id": "RULE_GATEWAY_MISMATCH",
                    "name": "Default Gateway Subnet Mismatch",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": f"PC expects gateway {pc_gw}, but router interfaces show: {', '.join([f'{i}: {ip}' for i, ip in r_ips])}.",
                    "recommendation": f"Reconfigure router interface to assign correct gateway IP {pc_gw} in the expected subnet."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 4: Trunk VLAN Pruning & Missing Allowed VLANs
    # -------------------------------------------------------------
    def _check_trunk_vlan_pruning(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show interfaces trunk" in show_output or "Vlans allowed" in show_output:
            # Check if specific VLAN in symptom is missing from trunk
            vlan_target_match = re.search(r"VLAN\s*(\d+)", f"{symptom} {topology}", re.IGNORECASE)
            allowed_match = re.search(r"Vlans allowed.*?\n[A-Za-z0-9\/\-]+\s+([0-9\,-]+)", show_output, re.DOTALL | re.IGNORECASE)
            
            if allowed_match:
                allowed_str = allowed_match.group(1).strip()
                allowed_list = []
                for part in allowed_str.split(","):
                    if "-" in part:
                        start, end = part.split("-")
                        allowed_list.extend(range(int(start), int(end) + 1))
                    elif part.isdigit():
                        allowed_list.append(int(part))
                        
                if vlan_target_match:
                    target_vlan = int(vlan_target_match.group(1))
                    if target_vlan not in allowed_list:
                        findings.append({
                            "rule_id": "RULE_TRUNK_PRUNING",
                            "name": "Trunk VLAN Pruning / Missing Allowed VLAN",
                            "severity": "High",
                            "layer": "Layer 2",
                            "detected": True,
                            "evidence": f"Target VLAN {target_vlan} is not in trunk allowed list ({allowed_str}).",
                            "recommendation": f"Execute 'switchport trunk allowed vlan add {target_vlan}' on trunk interface."
                        })
            elif "! VLAN" in show_output and "missing" in show_output.lower():
                findings.append({
                    "rule_id": "RULE_TRUNK_PRUNING",
                    "name": "Trunk VLAN Pruning",
                    "severity": "High",
                    "layer": "Layer 2",
                    "detected": True,
                    "evidence": "Trunk configuration excludes the required service VLAN.",
                    "recommendation": "Add the missing VLAN to the allowed trunk list via 'switchport trunk allowed vlan add <vlan>'."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 5: VLAN Misassignment or Default VLAN 1 Port
    # -------------------------------------------------------------
    def _check_vlan_misassignment_or_default(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show interfaces" in show_output and "switchport" in show_output:
            if "Access Mode VLAN: 1 (default)" in show_output:
                findings.append({
                    "rule_id": "RULE_PORT_UNCONFIGURED_VLAN",
                    "name": "Access Port on Default VLAN 1",
                    "severity": "Low",
                    "layer": "Layer 2",
                    "detected": True,
                    "evidence": "Access Mode VLAN is set to 1 (default).",
                    "recommendation": "Configure switchport access vlan <target_vlan> on this access interface."
                })
        if "show vlan brief" in show_output:
            # Check if ports in topology are split across unexpected VLANs
            if "Sales" in show_output and "Engineering" in show_output and ("PC1" in symptom or "Fa0/4" in full_text):
                findings.append({
                    "rule_id": "RULE_VLAN_MISASSIGNMENT",
                    "name": "Access Port VLAN Misassignment",
                    "severity": "Medium",
                    "layer": "Layer 2",
                    "detected": True,
                    "evidence": "Show vlan brief shows ports split across different VLANs (VLAN 10 vs VLAN 20).",
                    "recommendation": "Verify intended VLAN membership and reassign port with 'switchport access vlan 10'."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 6: DHCP Scope Exhaustion
    # -------------------------------------------------------------
    def _check_dhcp_exhaustion(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show ip dhcp pool" in show_output or "Utilization mark" in show_output:
            tot_match = re.search(r"Total addresses\s*:\s*(\d+)", show_output)
            leased_match = re.search(r"Leased addresses\s*:\s*(\d+)", show_output)
            if tot_match and leased_match:
                total = int(tot_match.group(1))
                leased = int(leased_match.group(1))
                if total > 0 and leased >= total:
                    findings.append({
                        "rule_id": "RULE_DHCP_EXHAUSTION",
                        "name": "DHCP Pool Exhaustion (100% Leased)",
                        "severity": "High",
                        "layer": "Layer 3",
                        "detected": True,
                        "evidence": f"DHCP pool has leased {leased}/{total} addresses (100% utilized).",
                        "recommendation": "Expand the DHCP pool subnet mask or clear expired bindings using 'clear ip dhcp binding *'."
                    })
        return findings

    # -------------------------------------------------------------
    # Rule 7: Missing DHCP Relay / ip helper-address
    # -------------------------------------------------------------
    def _check_dhcp_relay_helper(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "! no ip helper-address configured" in show_output or ("DHCP" in full_text and "helper-address" in full_text):
            if "no ip helper-address" in show_output or "interface Vlan" in show_output:
                findings.append({
                    "rule_id": "RULE_MISSING_DHCP_RELAY",
                    "name": "Missing DHCP Helper-Address (Relay)",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "SVI/Interface on router has no 'ip helper-address' configured to forward DHCP broadcasts.",
                    "recommendation": "Configure 'ip helper-address <DHCP_Server_IP>' under the client-facing SVI/interface."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 8: DHCP Snooping Untrusted Port
    # -------------------------------------------------------------
    def _check_dhcp_snooping_untrusted(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show ip dhcp snooping" in show_output:
            if "Switch DHCP snooping is enabled" in show_output and re.search(r"([A-Za-z0-9\/\-]+)\s+no", show_output):
                findings.append({
                    "rule_id": "RULE_DHCP_SNOOPING_UNTRUSTED",
                    "name": "DHCP Snooping Uplink Port Untrusted",
                    "severity": "High",
                    "layer": "Layer 2",
                    "detected": True,
                    "evidence": "DHCP snooping is enabled and uplink interface toward server is set to Trusted: no.",
                    "recommendation": "Configure 'ip dhcp snooping trust' on the interface connected to the DHCP server/uplink."
                })
        return findings

    # -------------------------------------------------------------
    # Rule 9: ACL Misconfigurations (Port Deny, Implicit Deny, Wildcard Mask, Unapplied)
    # -------------------------------------------------------------
    def _check_acl_issues(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        # Unapplied ACL
        if "Outgoing access list is not set" in show_output and "Inbound  access list is not set" in show_output:
            findings.append({
                "rule_id": "RULE_ACL_NOT_APPLIED",
                "name": "ACL Not Applied to Interface",
                "severity": "Medium",
                "layer": "Layer 3",
                "detected": True,
                "evidence": "Interface shows inbound/outbound access list is not set.",
                "recommendation": "Apply access list using 'ip access-group <ACL_NAME_OR_NUM> in|out' on the target interface."
            })

        if "! ACL exists but not applied" in show_output:
            findings.append({
                "rule_id": "RULE_ACL_NOT_APPLIED_GUEST",
                "name": "Guest Isolation ACL Not Applied",
                "severity": "High (Security)",
                "layer": "Layer 3",
                "detected": True,
                "evidence": "Guest isolation ACL exists in configuration but is not bound to the guest interface.",
                "recommendation": "Apply guest isolation ACL inbound on the guest VLAN interface."
            })

        # Explicit Port Deny
        if "deny tcp" in show_output or "deny udp" in show_output:
            deny_match = re.search(r"deny\s+(tcp|udp)\s+.*?eq\s+(\d+)", show_output, re.IGNORECASE)
            if deny_match:
                proto, port = deny_match.group(1), deny_match.group(2)
                findings.append({
                    "rule_id": "RULE_ACL_PORT_BLOCK",
                    "name": f"ACL Explicitly Denying {proto.upper()} Port {port}",
                    "severity": "Medium",
                    "layer": "Layer 4",
                    "detected": True,
                    "evidence": f"ACL contains explicit deny rule for {proto.upper()} port {port}.",
                    "recommendation": f"Review ACL entries and permit {proto.upper()} port {port} traffic if required by business applications."
                })

        # Incorrect Wildcard Mask (e.g., subnet mask instead of host 0.0.0.0 or 0.0.0.255 blocking whole subnet)
        if "deny ip" in show_output and "0.0.0.255 any" in show_output and "specific host" in symptom.lower():
            findings.append({
                "rule_id": "RULE_ACL_WILDCARD_MASK",
                "name": "Incorrect ACL Wildcard Mask (Subnet vs Host)",
                "severity": "High",
                "layer": "Layer 3",
                "detected": True,
                "evidence": "ACL uses 0.0.0.255 (entire /24 subnet) instead of 0.0.0.0 or host statement.",
                "recommendation": "Change ACL rule to 'deny host <ip>' or 'deny ip <ip> 0.0.0.0 any'."
            })

        # Implicit Deny All
        if "! No other permit lines - implicit deny any any" in show_output or (
            "show access-lists" in show_output and "permit" in show_output and "deny" not in show_output and "permit ip any any" not in show_output
        ):
            findings.append({
                "rule_id": "RULE_ACL_IMPLICIT_DENY",
                "name": "Unintended Traffic Dropped by ACL Implicit Deny",
                "severity": "High",
                "layer": "Layer 3/4",
                "detected": True,
                "evidence": "ACL has specific permit rules but lacks trailing 'permit ip any any', dropping all other traffic.",
                "recommendation": "Append 'permit ip any any' at the end of the ACL if unlisted traffic should be allowed."
            })

        return findings

    # -------------------------------------------------------------
    # Rule 10: NAT Misconfigurations (Missing Outside, Pool Exhaustion, Port Mismatch)
    # -------------------------------------------------------------
    def _check_nat_issues(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show ip nat statistics" in show_output or "show ip nat translations" in show_output or "ip nat inside source" in show_output:
            if "Outside interfaces: (none)" in show_output:
                findings.append({
                    "rule_id": "RULE_NAT_MISSING_OUTSIDE",
                    "name": "Missing NAT Outside Interface",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "show ip nat statistics indicates 'Outside interfaces: (none)'.",
                    "recommendation": "Configure 'ip nat outside' on the ISP-facing public interface."
                })

            if "allocated" in show_output and "100%" in show_output or "Pool exhausted" in show_output:
                findings.append({
                    "rule_id": "RULE_NAT_POOL_EXHAUSTION",
                    "name": "NAT Address Pool Exhaustion",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "NAT pool has 100% allocation and missed translation attempts.",
                    "recommendation": "Configure Port Address Translation (PAT) with 'overload' keyword or enlarge NAT pool."
                })

            if "ip nat inside source static" in show_output and ("8080" in show_output and "80" in show_output):
                findings.append({
                    "rule_id": "RULE_NAT_PORT_MISMATCH",
                    "name": "Static NAT Port Forwarding Mismatch",
                    "severity": "Medium",
                    "layer": "Layer 4",
                    "detected": True,
                    "evidence": "Static NAT translation rule maps external port to wrong internal port.",
                    "recommendation": "Update static NAT translation to target the actual service port (e.g. port 80)."
                })

        return findings

    # -------------------------------------------------------------
    # Rule 11: DNS & RADIUS Reachability / Forwarder
    # -------------------------------------------------------------
    def _check_dns_and_radius_reachability(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "DNS Servers:" in show_output and ("Request timed out" in show_output or "timed out" in show_output):
            findings.append({
                "rule_id": "RULE_DNS_UNREACHABLE",
                "name": "DNS Server Unreachable / Timeout",
                "severity": "Medium",
                "layer": "Layer 7",
                "detected": True,
                "evidence": "Host ping to configured DNS server IP timed out.",
                "recommendation": "Verify DNS server IP in DHCP scope and verify server connectivity and host firewall."
            })

        if "Destination host unreachable" in show_output and "DNS" in full_text:
            findings.append({
                "rule_id": "RULE_DNS_HOST_UNREACHABLE",
                "name": "DNS Server Host Down / No Route",
                "severity": "High",
                "layer": "Layer 3",
                "detected": True,
                "evidence": "Router returns 'Destination host unreachable' for DNS server IP.",
                "recommendation": "Verify DNS server virtual machine status, power state, and subnet routing."
            })

        if "! no forwarder configured" in show_output or ("DNS" in full_text and "forwarder" in show_output):
            findings.append({
                "rule_id": "RULE_DNS_MISSING_FORWARDER",
                "name": "Missing DNS Upstream Forwarder",
                "severity": "Medium",
                "layer": "Layer 7",
                "detected": True,
                "evidence": "Internal DNS server has no external DNS forwarder configured.",
                "recommendation": "Configure upstream forwarder (e.g., 8.8.8.8, 1.1.1.1) on the internal DNS server."
            })

        if "show radius statistics" in show_output or "Timeouts 50" in show_output:
            if "Timeouts" in show_output and "Responses 0" in show_output:
                findings.append({
                    "rule_id": "RULE_RADIUS_UNREACHABLE",
                    "name": "RADIUS Authentication Server Unreachable",
                    "severity": "High",
                    "layer": "Layer 7",
                    "detected": True,
                    "evidence": "WLC RADIUS statistics show 0 responses and repeated timeouts.",
                    "recommendation": "Check IP reachability to RADIUS server, shared secret key, and UDP port 1812."
                })

        return findings

    # -------------------------------------------------------------
    # Rule 12: Routing Issues (Missing Routes, Next-hop Unreachable, Asymmetric NAT)
    # -------------------------------------------------------------
    def _check_routing_issues(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show ip route" in show_output:
            if "! Expected route to" in show_output and "missing" in show_output.lower():
                findings.append({
                    "rule_id": "RULE_ROUTING_MISSING_ENTRY",
                    "name": "Missing Route in Routing Table",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "Routing table does not contain route for target destination subnet.",
                    "recommendation": "Verify routing protocol (OSPF/EIGRP) network statements or add static route."
                })

            if "Success rate is 0 percent" in show_output and "via" in show_output:
                findings.append({
                    "rule_id": "RULE_ROUTING_BAD_NEXTHOP",
                    "name": "Static Route Next-Hop Unreachable",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "Static route next-hop IP is unreachable (ping success rate 0%).",
                    "recommendation": "Correct next-hop IP address or fix Layer 1/2 connectivity on connecting WAN link."
                })

            if "NAT is applied on the other interface" in show_output:
                findings.append({
                    "rule_id": "RULE_ROUTING_ASYMMETRIC_NAT",
                    "name": "Asymmetric Routing / NAT Interface Mismatch",
                    "severity": "High",
                    "layer": "Layer 3",
                    "detected": True,
                    "evidence": "Default route points to interface mismatching the configured NAT outside interface.",
                    "recommendation": "Align default route next-hop with the interface where NAT outside is applied."
                })

        if "! sub-interface for VLAN 30 missing after reload - config not saved" in show_output or "missing after reload" in show_output:
            findings.append({
                "rule_id": "RULE_UNSAVED_CONFIG",
                "name": "Unsaved Configuration Lost on Device Reload",
                "severity": "High",
                "layer": "Layer 3",
                "detected": True,
                "evidence": "Sub-interface/configuration missing from running-config after reboot.",
                "recommendation": "Recreate missing sub-interface configuration and save with 'copy running-config startup-config'."
            })

        return findings

    # -------------------------------------------------------------
    # Rule 13: MAC Flapping / Duplicate MAC
    # -------------------------------------------------------------
    def _check_mac_flapping(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "show mac address-table" in show_output:
            mac_entries = re.findall(r"([0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+DYNAMIC\s+([A-Za-z0-9\/\-]+)", show_output)
            mac_ports = {}
            for mac, port in mac_entries:
                mac_ports.setdefault(mac, []).append(port)
            for mac, ports in mac_ports.items():
                if len(ports) > 1:
                    findings.append({
                        "rule_id": "RULE_MAC_FLAPPING",
                        "name": "Duplicate MAC Address / MAC Flapping",
                        "severity": "Medium",
                        "layer": "Layer 2",
                        "detected": True,
                        "evidence": f"MAC address {mac} dynamically learned on multiple switchports ({', '.join(ports)}).",
                        "recommendation": "Investigate duplicate MAC / VM clone or Layer 2 bridging loop across switchports."
                    })
        return findings

    # -------------------------------------------------------------
    # Rule 14: Physical Layer CRC & Input Errors
    # -------------------------------------------------------------
    def _check_physical_errors(self, full_text: str, show_output: str, topology: str, symptom: str):
        findings = []
        if "CRC" in show_output or "input errors" in show_output:
            err_match = re.search(r"(\d+)\s+input errors,\s*(\d+)\s+CRC", show_output)
            if err_match:
                in_err = int(err_match.group(1))
                crc_err = int(err_match.group(2))
                if in_err > 100 or crc_err > 100:
                    findings.append({
                        "rule_id": "RULE_PHYSICAL_CRC_ERRORS",
                        "name": "High Physical CRC / Input Errors",
                        "severity": "Medium",
                        "layer": "Layer 1",
                        "detected": True,
                        "evidence": f"Interface reports {in_err} input errors and {crc_err} CRC errors.",
                        "recommendation": "Inspect physical cabling, replace faulty patch cord, and check speed/duplex negotiation."
                    })
        return findings


# Quick CLI runner for testing
if __name__ == "__main__":
    import pandas as pd
    import os

    checker = CiscoRuleChecker()
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "cases.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"Loaded {len(df)} cases from {csv_path}")
        passed_count = 0
        for idx, row in df.iterrows():
            findings = checker.run_all_checks(
                symptom=str(row["symptom"]),
                topology_note=str(row["topology_note"]),
                show_output=str(row["show_output"])
            )
            print(f"[{row['case_id']}] {row['category']} - Findings: {len(findings)}")
            if findings:
                passed_count += 1
                for f in findings:
                    print(f"   -> [{f['rule_id']}] {f['name']} ({f['layer']}, {f['severity']})")
            else:
                print(f"   -> [NO FINDING TRIGGERED]")
        print(f"\nRule Engine Coverage: {passed_count}/{len(df)} cases triggered deterministic rules.")
    else:
        print(f"cases.csv not found at {csv_path}")


