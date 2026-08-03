"""
PLC Troubleshooter — Streamlit Frontend
Two tabs: Troubleshooter | Data Governance
"""

import streamlit as st
import requests
from datetime import datetime
import pandas as pd

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="PLC Troubleshooter",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0d1117; color: #c9d1d9; }

section[data-testid="stSidebar"] { background: #111827; border-right: 1px solid #1f2937; }

/* sidebar */
.sb-brand { padding: 24px 18px 18px; border-bottom: 1px solid #1f2937; }
.sb-icon  { font-size: 32px; margin-bottom: 8px; }
.sb-title { color: #f0f6fc; font-size: 16px; font-weight: 700; margin: 0 0 3px; }
.sb-sub   { color: #4b5e78; font-size: 11px; letter-spacing: 0.4px; margin: 0; }
.sb-sec   { padding: 14px 18px; border-bottom: 1px solid #1f2937; }
.sb-lbl   { color: #00b4b4; font-size: 10px; font-weight: 700; letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 10px; }
.sb-row   { display: flex; justify-content: space-between; padding: 5px 0; font-size: 12px; border-bottom: 1px solid #1f293730; }
.sb-row:last-child { border-bottom: none; }
.sb-key   { color: #4b5e78; }
.sb-val   { color: #e2e8f0; font-weight: 600; }
.sb-badge { background: #00b4b415; border: 1px solid #00b4b440; color: #00d4d4; padding: 1px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
.sb-grid  { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.sb-stat  { background: #0d1117; border: 1px solid #1f2937; border-radius: 8px; padding: 10px; text-align: center; }
.sb-stat .n { color: #00b4b4; font-size: 20px; font-weight: 700; line-height: 1; }
.sb-stat .d { color: #4b5e78; font-size: 10px; margin-top: 3px; letter-spacing: 0.5px; }
.sb-stat.g .n { color: #10b981; }
.sb-stat.a .n { color: #f59e0b; }
.sb-tip { background: #0d1117; border: 1px solid #1f2937; border-left: 3px solid #00b4b4; border-radius: 8px; padding: 12px 14px; font-size: 12px; color: #6b7c9e; line-height: 1.75; }
.sb-tip code { background: #1f2937; color: #00d4d4; padding: 1px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-size: 11px; }

/* header */
.hdr { background: linear-gradient(135deg, #0a1628, #0d2137, #0a1e30); border: 1px solid #1f3a52; border-radius: 14px; padding: 24px 28px; margin-bottom: 20px; position: relative; overflow: hidden; }
.hdr::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #00b4b4, #0284c7, #00b4b4); }
.hdr-row  { display: flex; align-items: center; gap: 14px; }
.hdr-box  { width: 48px; height: 48px; background: #00b4b415; border: 1px solid #00b4b440; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.hdr-t    { color: #f0f6fc; font-size: 20px; font-weight: 700; margin: 0 0 3px; }
.hdr-s    { color: #4b7a9e; font-size: 12px; margin: 0; }
.hdr-chips{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.chip     { background: #0d1117; border: 1px solid #1f3a52; color: #4b7a9e; border-radius: 99px; padding: 3px 12px; font-size: 11px; }
.chip span{ color: #00b4b4; margin-right: 5px; }

/* metric strip */
.metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }
.mtile   { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 14px 16px; position: relative; overflow: hidden; }
.mtile::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px; border-radius: 0 0 12px 12px; }
.mtile.bl::after { background: #0284c7; }
.mtile.tl::after { background: #00b4b4; }
.mtile.gn::after { background: #10b981; }
.mtile.am::after { background: #f59e0b; }
.ml { color: #4b5e78; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
.mv { color: #f0f6fc; font-size: 24px; font-weight: 700; line-height: 1; }
.ms { color: #2d3f52; font-size: 11px; margin-top: 4px; }

/* input */
.icard { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px 22px; margin-bottom: 20px; }
.ilbl  { color: #4b5e78; font-size: 11px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px; }
.stTextArea textarea { background: #0d1117 !important; border: 1.5px solid #1f2937 !important; border-radius: 9px !important; color: #e2e8f0 !important; font-size: 14px !important; padding: 11px 13px !important; }
.stTextArea textarea:focus { border-color: #00b4b4 !important; box-shadow: 0 0 0 3px #00b4b418 !important; }
.stTextArea textarea::placeholder { color: #2d3f52 !important; }
.stButton > button { background: linear-gradient(135deg, #007a7a, #005f5f) !important; color: #fff !important; border: 1px solid #00b4b440 !important; border-radius: 9px !important; padding: 11px 24px !important; font-size: 14px !important; font-weight: 600 !important; width: 100% !important; transition: all 0.2s !important; }
.stButton > button:hover { background: linear-gradient(135deg, #009595, #007a7a) !important; border-color: #00b4b4 !important; box-shadow: 0 4px 16px #00b4b428 !important; transform: translateY(-1px) !important; }

/* bubbles */
.ubub { display: flex; gap: 11px; background: #111827; border: 1px solid #1f2937; border-left: 3px solid #0284c7; border-radius: 9px; padding: 12px 15px; margin: 18px 0 8px; font-size: 14px; color: #c9d1d9; }
.umeta{ color: #2d3f52; font-size: 11px; margin-top: 3px; }

/* result card */
.rcard { background: #111827; border: 1px solid #1f2937; border-radius: 12px; overflow: hidden; margin-bottom: 6px; }
.rtop  { background: #0a1628; border-bottom: 1px solid #1f2937; padding: 12px 18px; display: flex; align-items: center; gap: 9px; }
.rlbl  { color: #00b4b4; font-weight: 700; font-size: 13px; }
.rtime { color: #2d3f52; font-size: 11px; margin-left: auto; }
.rbody { padding: 0 18px; }
.rfield{ display: grid; grid-template-columns: 130px 1fr; gap: 12px; padding: 12px 0; border-bottom: 1px solid #1f293750; align-items: start; }
.rfield:last-of-type { border-bottom: none; }
.rkey  { color: #2d3f52; font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; padding-top: 2px; }
.rval  { color: #c9d1d9; font-size: 14px; line-height: 1.65; }
.ecbdg { display: inline-block; background: #00b4b415; border: 1px solid #00b4b440; color: #00d4d4; border-radius: 6px; padding: 2px 11px; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 600; }
.mtbdg { display: inline-block; border-radius: 4px; padding: 1px 7px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-left: 8px; }
.mtbdg.exact   { background: #10b98120; color: #10b981; border: 1px solid #10b98140; }
.mtbdg.partial { background: #0284c720; color: #60b4ff; border: 1px solid #0284c740; }
.mtbdg.semantic{ background: #00b4b420; color: #00d4d4; border: 1px solid #00b4b440; }

/* confidence */
.cwrap { padding: 12px 18px 14px; border-top: 1px solid #1f2937; display: flex; align-items: center; gap: 11px; }
.clbl  { color: #2d3f52; font-size: 11px; font-weight: 600; white-space: nowrap; }
.ctrk  { flex: 1; background: #0d1117; border-radius: 99px; height: 5px; border: 1px solid #1f2937; overflow: hidden; }
.cfil  { height: 100%; border-radius: 99px; }
.cpct  { font-size: 12px; font-weight: 700; white-space: nowrap; font-family: 'JetBrains Mono', monospace; }

/* no match */
.nmcard { background: #1c120050; border: 1px solid #f59e0b40; border-left: 3px solid #f59e0b; border-radius: 9px; padding: 14px 18px; margin-bottom: 6px; }
.nmtitle{ color: #f59e0b; font-weight: 700; font-size: 13px; margin-bottom: 4px; }
.nmbody { color: #a07c30; font-size: 13px; line-height: 1.6; }

/* empty */
.empty { text-align: center; padding: 48px 20px; color: #1f2937; }
.empty-icon { font-size: 44px; margin-bottom: 12px; }

/* dg tab */
.dg-card { background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 20px 22px; margin-bottom: 14px; }
.dg-title{ color: #00b4b4; font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #1f2937; }
.dg-kpi  { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.dg-k    { background: #0d1117; border: 1px solid #1f2937; border-radius: 9px; padding: 14px; text-align: center; }
.dg-kn   { color: #00b4b4; font-size: 22px; font-weight: 700; }
.dg-kd   { color: #2d3f52; font-size: 11px; margin-top: 3px; }
.tag     { display: inline-block; background: #1f2937; color: #6b7c9e; border-radius: 5px; padding: 2px 9px; font-size: 11px; margin: 3px; }

/* footer */
.pgfoot { text-align: center; color: #1f2937; font-size: 11px; padding: 20px 0 6px; border-top: 1px solid #1f2937; margin-top: 28px; letter-spacing: 0.3px; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

total     = len(st.session_state.history)
matched   = sum(1 for h in st.session_state.history if h["matched"])
unmatched = total - matched
avg_conf  = (sum(h["confidence"] for h in st.session_state.history) / total) if total else 0

# ── Fetch backend stats ───────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_stats():
    try:
        return requests.get(f"{API}/stats", timeout=5).json()
    except:
        return None

@st.cache_data(ttl=10)
def get_log():
    try:
        return requests.get(f"{API}/query-log?limit=100", timeout=5).json()
    except:
        return []

stats = get_stats()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-icon">⚙️</div>
        <div class="sb-title">PLC Troubleshooter</div>
        <div class="sb-sub">MHA SOLUTIONS INC. · AI CO-OP 2025</div>
    </div>
    """, unsafe_allow_html=True)

    db = stats["dataset"] if stats else {}
    st.markdown(f"""
    <div class="sb-sec">
        <div class="sb-lbl">Dataset</div>
        <div class="sb-row"><span class="sb-key">Records</span><span class="sb-val">{db.get('total_records','—')}</span></div>
        <div class="sb-row"><span class="sb-key">Unique Codes</span><span class="sb-val">{db.get('unique_codes','—')}</span></div>
        <div class="sb-row"><span class="sb-key">Categories</span><span class="sb-val">{db.get('categories','—')}</span></div>
        <div class="sb-row"><span class="sb-key">Sources</span><span class="sb-val">Modbus · PtP · USS</span></div>
        <div class="sb-row"><span class="sb-key">Vendor</span><span class="sb-badge">Siemens</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-sec">
        <div class="sb-lbl">This Session</div>
        <div class="sb-grid">
            <div class="sb-stat"><div class="n">{total}</div><div class="d">QUERIES</div></div>
            <div class="sb-stat g"><div class="n">{matched}</div><div class="d">MATCHED</div></div>
            <div class="sb-stat a"><div class="n">{unmatched}</div><div class="d">NO MATCH</div></div>
            <div class="sb-stat"><div class="n">{avg_conf:.0%}</div><div class="d">AVG CONF</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-sec">
        <div class="sb-lbl">How to Query</div>
        <div class="sb-tip">
            By error code:<br>
            <code>16#8182</code> &nbsp;·&nbsp; <code>8182</code><br><br>
            By description:<br>
            <em style="color:#4b5e78">invalid station address modbus</em><br><br>
            Answers are strictly from validated Siemens documentation.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:14px 18px;'>", unsafe_allow_html=True)
    if st.button("🗑️  Clear History"):
        st.session_state.history = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Parse LLM response ────────────────────────────────────────────────────────
def parse(text):
    fields = {"Error Code": "", "Description": "", "Remedy": ""}
    for key in fields:
        for line in text.splitlines():
            if key.lower() in line.lower() and ":" in line:
                val = line.split(":", 1)[-1].strip().strip("*").strip()
                if val and "extract from" not in val.lower() and "retrieved data" not in val.lower():
                    fields[key] = val
                    break
    return fields

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["⚙️  Troubleshooter", "📊  Data Governance"])

# ════════════════════════════════════════════════════════════
# TAB 1 — TROUBLESHOOTER
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="hdr">
        <div class="hdr-row">
            <div class="hdr-box">⚙️</div>
            <div>
                <p class="hdr-t">Siemens PLC Error Code Troubleshooter</p>
                <p class="hdr-s">AI-powered diagnostics · Strictly grounded in validated Siemens documentation</p>
            </div>
        </div>
        <div class="hdr-chips">
            <div class="chip"><span>◈</span>FAISS Semantic Search</div>
            <div class="chip"><span>◈</span>Google Gemini 1.5 Flash</div>
            <div class="chip"><span>◈</span>RAG Architecture</div>
            <div class="chip"><span>◈</span>Exact + Semantic Match</div>
            <div class="chip"><span>◈</span>Zero Hallucination Mode</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Metric strip
    qstats = stats["queries"] if stats else {}
    all_matched   = qstats.get("matched", 0)
    all_total     = qstats.get("total", 0)
    all_avg       = qstats.get("avg_confidence", 0)
    all_unmatched = qstats.get("unmatched", 0)

    st.markdown(f"""
    <div class="metrics">
        <div class="mtile bl"><div class="ml">Total Queries</div><div class="mv">{all_total}</div><div class="ms">All time</div></div>
        <div class="mtile gn"><div class="ml">Matched</div><div class="mv">{all_matched}</div><div class="ms">Reliable results</div></div>
        <div class="mtile am"><div class="ml">No Match</div><div class="mv">{all_unmatched}</div><div class="ms">Low confidence</div></div>
        <div class="mtile tl"><div class="ml">Avg Confidence</div><div class="mv">{all_avg:.0%}</div><div class="ms">All time</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Input
    st.markdown('<div class="icard"><div class="ilbl">🔍 Enter PLC error code or describe the fault</div>', unsafe_allow_html=True)
    with st.form("qform", clear_on_submit=True):
        query = st.text_area(
            label="q", label_visibility="collapsed",
            placeholder="e.g.  16#8182   or   'invalid station address on Modbus'",
            height=80
        )
        submitted = st.form_submit_button("⚡  Get Troubleshooting Solution")
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if query.strip():
            with st.spinner("Searching database..."):
                try:
                    res = requests.get(f"{API}/chat", params={"query": query.strip()}, timeout=25)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.history.append({
                            "query":      query.strip(),
                            "response":   data.get("response", ""),
                            "confidence": data.get("confidence", 0.0),
                            "matched":    data.get("matched", False),
                            "match_type": data.get("match_type", "semantic"),
                            "time":       datetime.now().strftime("%H:%M"),
                        })
                        get_stats.clear()
                        st.rerun()
                    else:
                        st.error(f"Backend error {res.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out.")
        else:
            st.warning("Please enter an error code or describe the issue.")

    # History
    if not st.session_state.history:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">🔧</div>
            <div style="font-size:14px;">Enter a Siemens PLC error code above to get started</div>
        </div>
        """, unsafe_allow_html=True)

    for item in reversed(st.session_state.history):
        st.markdown(f"""
        <div class="ubub">
            <div style="font-size:16px;opacity:0.6;">👤</div>
            <div><div>{item['query']}</div><div class="umeta">{item['time']}</div></div>
        </div>
        """, unsafe_allow_html=True)

        if not item["matched"]:
            st.markdown(f"""
            <div class="nmcard">
                <div class="nmtitle">⚠️ No Reliable Match Found</div>
                <div class="nmbody">Confidence {item['confidence']:.0%} is below the threshold.
                Please verify the error code format or rephrase the query.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            f       = parse(item["response"])
            ec      = f["Error Code"]  or "—"
            desc    = f["Description"] or item["response"]
            rem     = f["Remedy"]      or "See description above."
            conf    = item["confidence"]
            color   = "#10b981" if conf >= 0.7 else "#f59e0b"
            bar_pct = int(conf * 100)
            mt      = item.get("match_type", "semantic")

            st.markdown(f"""
            <div class="rcard">
                <div class="rtop">
                    <span style="font-size:16px;">🤖</span>
                    <span class="rlbl">Troubleshooting Result</span>
                    <span class="mtbdg {mt}">{mt}</span>
                    <span class="rtime">{item['time']}</span>
                </div>
                <div class="rbody">
                    <div class="rfield">
                        <div class="rkey">Error Code</div>
                        <div class="rval"><span class="ecbdg">{ec}</span></div>
                    </div>
                    <div class="rfield">
                        <div class="rkey">Description</div>
                        <div class="rval">{desc}</div>
                    </div>
                    <div class="rfield">
                        <div class="rkey">Remedy</div>
                        <div class="rval">{rem}</div>
                    </div>
                </div>
                <div class="cwrap">
                    <div class="clbl">Match Confidence</div>
                    <div class="ctrk"><div class="cfil" style="width:{bar_pct}%;background:{color};"></div></div>
                    <div class="cpct" style="color:{color};">{conf:.0%}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — DATA GOVERNANCE
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="hdr">
        <div class="hdr-row">
            <div class="hdr-box">📊</div>
            <div>
                <p class="hdr-t">Data Governance Dashboard</p>
                <p class="hdr-s">Dataset health · Query audit trail · Coverage & confidence analytics</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not stats:
        st.warning("Cannot connect to backend. Start FastAPI on port 8000.")
    else:
        db = stats["dataset"]
        qs = stats["queries"]

        # Dataset health
        st.markdown("""<div class="dg-card"><div class="dg-title">📁 Dataset Health</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="dg-kpi">
            <div class="dg-k"><div class="dg-kn">{db['total_records']}</div><div class="dg-kd">Total Records</div></div>
            <div class="dg-k"><div class="dg-kn">{db['unique_codes']}</div><div class="dg-kd">Unique Error Codes</div></div>
            <div class="dg-k"><div class="dg-kn">{db['categories']}</div><div class="dg-kd">Categories</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br><div style='font-size:11px;color:#2d3f52;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;'>Error Types</div>", unsafe_allow_html=True)
        tags = "".join(f'<span class="tag">{t}</span>' for t in db.get("error_types", []))
        st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)

        st.markdown("<br><div style='font-size:11px;color:#2d3f52;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;'>Source Files</div>", unsafe_allow_html=True)
        srcs = "".join(f'<span class="tag">{s}</span>' for s in db.get("source_files", []))
        st.markdown(f"<div>{srcs}</div></div>", unsafe_allow_html=True)

        # Query analytics
        st.markdown("""<div class="dg-card"><div class="dg-title">🔍 Query Analytics</div>""", unsafe_allow_html=True)
        match_rate = (qs['matched'] / qs['total'] * 100) if qs['total'] else 0
        st.markdown(f"""
        <div class="dg-kpi">
            <div class="dg-k"><div class="dg-kn">{qs['total']}</div><div class="dg-kd">Total Queries</div></div>
            <div class="dg-k"><div class="dg-kn" style="color:#10b981">{match_rate:.1f}%</div><div class="dg-kd">Match Rate</div></div>
            <div class="dg-k"><div class="dg-kn">{qs['avg_confidence']:.0%}</div><div class="dg-kd">Avg Confidence</div></div>
        </div>
        """, unsafe_allow_html=True)

        mt = qs.get("match_types", {})
        if mt:
            st.markdown("<br><div style='font-size:11px;color:#2d3f52;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;'>Match Types</div>", unsafe_allow_html=True)
            mt_tags = "".join(f'<span class="tag">{k}: {v}</span>' for k, v in mt.items())
            st.markdown(f"<div>{mt_tags}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Audit log
        st.markdown("""<div class="dg-card"><div class="dg-title">📋 Query Audit Log</div>""", unsafe_allow_html=True)
        log_data = get_log()
        if log_data:
            log_df = pd.DataFrame(log_data)
            log_df = log_df[["timestamp", "query", "matched", "confidence", "match_type"]].copy()
            log_df["confidence"] = log_df["confidence"].apply(lambda x: f"{float(x):.0%}")
            log_df["matched"]    = log_df["matched"].apply(lambda x: "✅" if str(x).lower() in ("true","1") else "❌")
            log_df.columns       = ["Timestamp", "Query", "Matched", "Confidence", "Match Type"]
            st.dataframe(log_df, use_container_width=True, hide_index=True)

            csv = pd.DataFrame(log_data).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️  Export Audit Log (CSV)", csv, "query_audit_log.csv", "text/csv")
        else:
            st.markdown("<div style='color:#2d3f52;font-size:13px;padding:10px 0;'>No queries logged yet.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="pgfoot">
    Siemens PLC Troubleshooter · MHA Solutions Inc. · AI Co-op 2025 ·
    Powered by FastAPI, FAISS, Gemini &amp; Streamlit
</div>
""", unsafe_allow_html=True)
