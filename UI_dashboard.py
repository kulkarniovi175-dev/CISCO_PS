import streamlit as st
import pandas as pd
import numpy as np
import time

# Page Configuration
st.set_page_config(
    page_title="PacketPilot AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS Customizations
st.markdown("""
<style>
    /* CSS variables & main background */
    :root {
        --cisco-blue: #049FD9;
        --cisco-dark-blue: #025E97;
        --card-bg: rgba(255, 255, 255, 0.05);
        --card-border: rgba(255, 255, 255, 0.1);
        --text-color: #ffffff;
    }
    
    /* Main body background */
    .stApp {
        background-color: #0d1117;
        color: var(--text-color);
    }
    
    /* Custom headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Cisco Theme Accents */
    .cisco-accent {
        color: var(--cisco-blue);
        font-weight: bold;
    }
    
    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.8);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-card {
        background: linear-gradient(135deg, rgba(4, 159, 217, 0.1) 0%, rgba(2, 94, 151, 0.05) 100%);
        border: 1px solid rgba(4, 159, 217, 0.2);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .kpi-val {
        font-size: 2rem;
        font-weight: bold;
        color: var(--cisco-blue);
        margin-top: 5px;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid rgba(48, 54, 61, 0.8) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--cisco-blue) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 20px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: var(--cisco-dark-blue) !important;
        box-shadow: 0 0 10px rgba(4, 159, 217, 0.5) !important;
        transform: translateY(-2px);
    }
    
    /* Syntax Highlighting Console styling */
    .cisco-cli {
        background-color: #000000 !important;
        color: #00ff00 !important;
        font-family: 'Courier New', Courier, monospace !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Custom Title Header with logo placeholder
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #30363d; padding-bottom: 10px; margin-bottom: 25px;">
    <div style="display: flex; align-items: center;">
        <span style="font-size: 2.2rem; margin-right: 10px;">✈️</span>
        <div>
            <h1 style="margin: 0; line-height: 1.1;">PacketPilot <span style="color:#049FD9;">AI</span></h1>
            <small style="color: #8b949e;">Next-Gen Cisco Lab Network Troubleshooting Assistant</small>
        </div>
    </div>
    <div style="text-align: right;">
        <span class="cisco-accent">● NOC System Status: Active</span><br/>
        <small style="color: #8b949e;">Human-in-the-Loop Verification Enabled</small>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Navigation</h2>", unsafe_allow_html=True)
    menu_selection = st.radio(
        label="Select a Workspace Page",
        options=[
            "🏠 Home",
            "📊 Dashboard",
            "🤖 AI Diagnosis",
            "🛠 Rule Checker",
            "👨 Human Review",
            "📜 Responsible AI Log",
            "📂 Case Dataset",
            "⚙ Settings",
            "ℹ About"
        ],
        label_visibility="collapsed"
    )

# ----------------- PAGE 1: HOME -----------------
if menu_selection == "🏠 Home":
    st.markdown("""
    <div style="text-align: center; padding: 50px 20px; background: radial-gradient(circle, rgba(4,159,217,0.1) 0%, rgba(13,17,23,0) 70%); border-radius: 20px;">
        <h1 style="font-size: 3rem; margin-bottom: 15px;">AI-Powered Cisco Network Troubleshooting Assistant</h1>
        <p style="font-size: 1.3rem; color: #8b949e; max-width: 800px; margin: 0 auto 30px auto;">
            Diagnose Cisco Packet Tracer network issues using advanced AI with structured diagnostics and safety-first human verification.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card" style="height: 250px; text-align: center;">
            <span style="font-size: 3rem;">🤖</span>
            <h3>AI Diagnosis</h3>
            <p style="color: #8b949e; font-size: 0.95rem;">Upload symptoms, topology notes, and terminal outputs to generate evidence-backed solutions instantly.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Diagnosis ➡️", key="btn_diag"):
            st.toast("Navigating to AI Diagnosis...")
            # Note: Navigation trigger requires streamlit session state, we will implement this.
            
    with col2:
        st.markdown("""
        <div class="glass-card" style="height: 250px; text-align: center;">
            <span style="font-size: 3rem;">🛠</span>
            <h3>Rule Checker</h3>
            <p style="color: #8b949e; font-size: 0.95rem;">Run deterministic code checks against configurations for duplicate IPs, missing trunk lines, and wrong subnets.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("Run Checker ➡️", key="btn_check")
        
    with col3:
        st.markdown("""
        <div class="glass-card" style="height: 250px; text-align: center;">
            <span style="font-size: 3rem;">📊</span>
            <h3>Live Analytics</h3>
            <p style="color: #8b949e; font-size: 0.95rem;">Inspect problem frequency, severity distributions, and human-to-AI agreement logs.</p>
        </div>
        """, unsafe_allow_html=True)
        st.button("View Analytics ➡️", key="btn_dash")

# ----------------- PAGE 2: DASHBOARD -----------------
elif menu_selection == "📊 Dashboard":
    st.subheader("Network Troubleshooting Analytics")
    
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Total Cases</div><div class="kpi-val">30</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Critical Issues</div><div class="kpi-val">8</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="kpi-card"><div class="kpi-label">AI Accuracy</div><div class="kpi-val">83.3%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Human Approval</div><div class="kpi-val">90.0%</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="kpi-card"><div class="kpi-label">Pending Reviews</div><div class="kpi-val">0</div></div>', unsafe_allow_html=True)
        
    st.write(" ")
    
    # Placeholder for Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card"><h4>Network Issue Types</h4><p style="color: #8b949e;">Chart placeholder: VLAN, Routing, DHCP, DNS, ACL, NAT</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card"><h4>Severity Distribution</h4><p style="color: #8b949e;">Chart placeholder: Low, Medium, High, Critical</p></div>', unsafe_allow_html=True)

# ----------------- PAGE 3: AI DIAGNOSIS -----------------
elif menu_selection == "🤖 AI Diagnosis":
    st.subheader("Cisco Network Fault Diagnoser")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### Input Symptoms & Show-Command Evidence")
        symptom_in = st.text_input("Symptom", placeholder="e.g., PC1 cannot ping internal server")
        topology_in = st.text_area("Topology Notes", placeholder="e.g., VLAN 10 Subnet 192.168.10.0/24")
        show_in = st.text_area("Show-Command Outputs", placeholder="Paste 'show ip int brief', 'show ip route', etc. here...", height=200)
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            analyze_btn = st.button("Run AI Diagnosis 🚀")
        with c_btn2:
            reset_btn = st.button("Reset Inputs 🔄")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("### AI Diagnostic Output")
        if analyze_btn:
            with st.spinner("Analyzing command evidence & generating structural fix..."):
                time.sleep(1.5)
                st.success("Analysis Complete!")
                st.markdown("""
                **Root Cause:** Sub-interface encapsulation missing.
                
                **OSI Layer:** Layer 3 (Network)
                
                **Confidence Score:** **88%**
                
                **Citations / Evidence:**
                `GigabitEthernet0/0.20  192.168.20.1    YES manual up    up`
                but sub-interface encapsulation dot1q was omitted in run-config.
                
                **Next Recommended CLI Commands:**
                ```cisco
                R1# show running-config interface GigabitEthernet0/0.20
                ```
                
                **Evidence-Backed Fix Steps:**
                ```cisco
                R1(config)# interface GigabitEthernet0/0.20
                R1(config-subif)# encapsulation dot1Q 20
                R1(config-subif)# ip address 192.168.20.1 255.255.255.0
                ```
                """)
        else:
            st.info("Provide diagnostic evidence on the left panel and click 'Run AI Diagnosis' to see recommendations.")
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PAGE 4: RULE CHECKER -----------------
elif menu_selection == "🛠 Rule Checker":
    st.subheader("Deterministic Configuration Checking")
    st.write("Before sending traffic logs to the AI, run this deterministic script validator to catch standard mistakes.")
    
    st.markdown("""
    <div class="glass-card">
        <h3>🔍 Rule Engine Status Checklist</h3>
        <hr style="border-color: #30363d;"/>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>🟢 <b>Duplicate IP Detection:</b> No duplicate IP leases found in the show command output.</span>
            <span style="color:#00ff00;">PASS</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>🟢 <b>Gateway Subnet Mask Mismatch:</b> Hosts and sub-interfaces share correct IP block bounds.</span>
            <span style="color:#00ff00;">PASS</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>🔴 <b>Interface Status Check:</b> <code>GigabitEthernet0/1</code> is administratively down.</span>
            <span style="color:#ff3333;">FAIL</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span>🟡 <b>Missing VLAN:</b> Switchport access VLAN 20 is configured but VLAN 20 is absent in database.</span>
            <span style="color:#ffff33;">WARN</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- PAGE 5: HUMAN REVIEW -----------------
elif menu_selection == "👨 Human Review":
    st.subheader("Human-in-the-Loop Review Queue")
    st.write("All diagnoses must be verified, corrected, or rejected before implementation.")
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("#### Reviewing Diagnostic Case: `CASE_001`")
    st.markdown("""
    **Symptom:** PC gets IP but cannot reach server in VLAN 30; gateway ping works.
    
    **AI Suggested Fix:** Interface Gig0/0.30 trunk encapsulation mismatch.
    
    **AI Confidence:** 85%
    """)
    
    verdict = st.radio("Review Verdict", ["Accept AI Fix", "Edit AI Fix", "Reject Diagnosis"])
    notes = st.text_area("Reviewer Corrections / Notes", placeholder="Provide rationale for edits or rejections...")
    
    if st.button("Submit Verdict"):
        st.success("Review verdict logged successfully!")
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PAGE 6: RESPONSIBLE AI LOG -----------------
elif menu_selection == "📜 Responsible AI Log":
    st.subheader("Responsible AI & Human Correction Journal")
    st.write("Documentation of edge cases where deterministic rules or human eyes caught AI errors.")
    
    st.markdown("""
    <div class="glass-card">
        <h3>🚨 Case Study 1: Wildcard Mask Mismatch</h3>
        <p><b>Original AI Prediction:</b> Layer 3 Route missing on Router R2.</p>
        <p><b>Human Correction:</b> The route was present, but OSPF configuration had a wrong wildcard mask <code>0.0.0.255</code> instead of <code>0.0.0.3</code>, which exposed local management interfaces instead of network bounds.</p>
        <p><b>Lessons Learned:</b> Deterministic checker should cross-reference OSPF network wildcard bounds against active subnet size.</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- PAGE 7: CASE DATASET -----------------
elif menu_selection == "📂 Case Dataset":
    st.subheader("Troubleshooting Case Catalog")
    st.write("Upload, preview, and select troubleshooting cases to feed into the diagnostic dashboard.")
    
    uploaded_file = st.file_uploader("Upload cases.csv dataset", type=["csv"])
    
    # Mock data display
    mock_df = pd.DataFrame({
        "Case ID": [f"CASE_00{i}" for i in range(1, 6)],
        "Symptom": [
            "PC1 cannot reach internet gateway",
            "VLAN 10 clients do not receive DHCP address",
            "DNS lookups fail from client workstation",
            "OSPF adjacency fails to establish between R1 and R2",
            "Internal server inaccessible via WAN IP"
        ],
        "OSI Layer": ["Layer 3", "Layer 2", "Layer 7", "Layer 3", "Layer 4"],
        "Concept Tag": ["Subnetting", "DHCP", "DNS", "OSPF", "NAT"],
        "Severity": ["High", "Critical", "Medium", "High", "High"]
    })
    st.dataframe(mock_df, use_container_width=True)

# ----------------- PAGE 8: SETTINGS -----------------
elif menu_selection == "⚙ Settings":
    st.subheader("System Settings")
    st.write("Configure model endpoints, API keys, and validation parameters.")
    
    st.text_input("Gemini API Key", type="password")
    st.text_input("OpenAI API Key", type="password")
    st.slider("AI Temperature", 0.0, 1.0, 0.2)

# ----------------- PAGE 9: ABOUT -----------------
elif menu_selection == "ℹ About":
    st.subheader("About PacketPilot AI")
    st.markdown("""
    **Objective:** Help junior network engineers bridge the gap between running terminal commands and identifying real root causes.
    
    **Key Capabilities:**
    - Cisco CLI outputs pattern matching using regex rules.
    - AI-assisted diagnostic logic using custom prompts.
    - Mandatory review loop protecting networks from false AI advice.
    
    **Workflow:**
    Network Problem -> Symptom -> Rule Checker (Deterministic) -> AI Diagnostic -> Reviewer Action -> Verified Solution.
    """)



