"""
BEHAVIORAL-BASED AUTHENTICATION  v9.0  — REAL KEYSTROKE MEASUREMENT
Two-Factor: Password + Keystroke Dynamics

KEY FIX: The behavioral layer now uses REAL measured keystrokes.
  - JS widget captures actual keydown/keyup timestamps as you type
  - Features are computed from YOUR actual timing, not a simulation
  - Features stored in st.session_state via a text_input that JS fills
  - Registration samples = your real typing
  - Authentication = your real typing compared to your enrolled samples
  - If someone else types (even with correct password) → different rhythm → DENIED

IIIT Raichur | Roll: AD23B1021
"""

import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import hashlib
import time
import json
import warnings
warnings.filterwarnings("ignore")

from ml_model import BehavioralAuthModel
from data_manager import DataManager

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BehaviorAuth | 2FA Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

TARGET = "the quick brown fox jumps"

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{ font-family:'Inter',sans-serif !important; }
.stApp { background:linear-gradient(135deg,#0a0a0f 0%,#0d1117 40%,#0a0e1a 100%) !important; }
#MainMenu,footer,header { visibility:hidden; }
.block-container { padding:1.5rem 2rem 3rem !important; max-width:1300px; }
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1117 0%,#0a0e1a 100%) !important;border-right:1px solid rgba(99,102,241,0.2) !important;}
.stButton>button{font-family:'Inter',sans-serif !important;font-weight:500 !important;font-size:0.85rem !important;border-radius:10px !important;transition:all 0.2s ease !important;width:100%;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;border:none !important;color:white !important;box-shadow:0 4px 15px rgba(99,102,241,0.35) !important;}
.stButton>button[kind="primary"]:hover{box-shadow:0 6px 25px rgba(99,102,241,0.55) !important;transform:translateY(-1px) !important;}
.stButton>button[kind="secondary"]{background:rgba(255,255,255,0.04) !important;border:1px solid rgba(255,255,255,0.1) !important;color:rgba(255,255,255,0.75) !important;}
.stButton>button[kind="secondary"]:hover{background:rgba(99,102,241,0.12) !important;border-color:rgba(99,102,241,0.4) !important;color:white !important;}
.stButton>button:disabled{opacity:0.4 !important;cursor:not-allowed !important;transform:none !important;}
.stTextInput>div>div>input{background:rgba(255,255,255,0.05) !important;border:1px solid rgba(99,102,241,0.3) !important;border-radius:10px !important;color:white !important;padding:0.6rem 0.9rem !important;}
.stTextInput>div>div>input:focus{border-color:rgba(99,102,241,0.7) !important;box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important;}
[data-testid="stMetric"]{background:rgba(255,255,255,0.03) !important;border:1px solid rgba(255,255,255,0.07) !important;border-radius:14px !important;padding:1rem 1.2rem !important;}
[data-testid="stMetricValue"]{color:#a78bfa !important;font-weight:700 !important;}
[data-testid="stMetricLabel"]{color:rgba(255,255,255,0.5) !important;font-size:0.75rem !important;}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#6366f1,#a78bfa) !important;border-radius:99px !important;}
.stSlider>div>div>div>div{background:linear-gradient(90deg,#6366f1,#a78bfa) !important;}
.stTabs [data-baseweb="tab-list"]{gap:4px;background:rgba(255,255,255,0.03);border-radius:12px;padding:4px;border:1px solid rgba(255,255,255,0.06);}
.stTabs [data-baseweb="tab"]{border-radius:9px !important;color:rgba(255,255,255,0.55) !important;font-weight:500 !important;font-size:0.82rem !important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#6366f1,#8b5cf6) !important;color:white !important;}
hr{border-color:rgba(255,255,255,0.07) !important;margin:1.5rem 0 !important;}
.hero{background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1),rgba(6,182,212,0.08));border:1px solid rgba(99,102,241,0.25);border-radius:20px;padding:2rem;text-align:center;margin-bottom:2rem;}
.hero h1{font-size:2.4rem !important;font-weight:800 !important;background:linear-gradient(135deg,#ffffff,#a78bfa,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2 !important;margin:0 0 0.5rem 0 !important;}
.hero p{color:rgba(255,255,255,0.55);font-size:0.95rem;margin:0;}
.glass{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:1.4rem 1.5rem;margin-bottom:1rem;}
.stat-card{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:1.4rem;text-align:center;transition:all 0.2s;}
.stat-card:hover{border-color:rgba(99,102,241,0.35);background:rgba(99,102,241,0.06);transform:translateY(-2px);}
.stat-num{font-size:2rem;font-weight:800;line-height:1;margin-bottom:0.35rem;}
.stat-lbl{font-size:0.7rem;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.1em;font-weight:600;}
.result-ok{background:linear-gradient(135deg,rgba(16,185,129,0.12),rgba(6,182,212,0.08));border:1.5px solid rgba(16,185,129,0.5);border-radius:16px;padding:1.8rem;text-align:center;margin:1rem 0;}
.result-fail{background:linear-gradient(135deg,rgba(239,68,68,0.12),rgba(245,158,11,0.06));border:1.5px solid rgba(239,68,68,0.5);border-radius:16px;padding:1.8rem;text-align:center;margin:1rem 0;}
.step-badge{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);font-size:0.75rem;font-weight:700;color:white;margin-right:0.5rem;}
.info-box{background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:12px;padding:0.85rem 1.1rem;font-size:0.85rem;color:rgba(180,180,255,0.9);margin:0.5rem 0;line-height:1.6;}
.warn-box{background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:12px;padding:0.85rem 1.1rem;font-size:0.85rem;color:rgba(255,220,150,0.9);margin:0.5rem 0;}
.success-box{background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:12px;padding:0.85rem 1.1rem;font-size:0.85rem;color:rgba(110,231,183,0.9);margin:0.5rem 0;}
.section-title{font-size:1.05rem;font-weight:700;color:white;margin:1.2rem 0 0.7rem;}
.user-item{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:0.55rem 0.9rem;margin:0.3rem 0;font-size:0.82rem;color:rgba(255,255,255,0.7);display:flex;justify-content:space-between;align-items:center;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# KEYSTROKE WIDGET — JS captures real timing, sends JSON via URL param
# This is the correct, working approach
# ══════════════════════════════════════════════════════════════════════════

def keystroke_widget(session_key: str) -> dict | None:
    """
    Renders a JS typing widget that captures real keystroke timing.
    Returns a dict of 13 features if user has finished typing, else None.

    Communication: JS writes feature JSON to URL ?ks_json=... param.
    Python reads it on next rerun via st.query_params.
    Shadow key stores the result so it survives reruns.
    """
    shadow = session_key + "_feat"

    # Read from URL params if JS just wrote something
    try:
        params  = st.query_params
        ks_key  = params.get("ks_key", "")
        ks_json = params.get("ks_json", "")
        if ks_json and ks_key == session_key:
            import urllib.parse
            decoded = urllib.parse.unquote(str(ks_json))
            feat    = json.loads(decoded)
            if feat.get("n_keys", 0) >= 8:
                st.session_state[shadow] = feat
            st.query_params.clear()
    except Exception:
        pass

    feat_ready = st.session_state.get(shadow)

    widget_html = f"""<!DOCTYPE html><html><head>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:'Inter','Segoe UI',sans-serif;padding:4px}}
.wrap{{background:rgba(99,102,241,.07);border:1.5px dashed rgba(99,102,241,.4);border-radius:14px;padding:16px 18px}}
.lbl{{font-size:11px;color:rgba(180,180,255,.5);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;text-align:center}}
.phrase{{font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:600;color:#a78bfa;text-align:center;background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.2);border-radius:8px;padding:9px 14px;margin-bottom:12px;letter-spacing:.04em}}
.ch-ok{{color:#6ee7b7}}.ch-bad{{color:#fca5a5}}.ch-cur{{color:white;border-bottom:2px solid #a78bfa}}.ch-dim{{color:rgba(255,255,255,.25)}}
#inp{{width:100%;background:rgba(255,255,255,.06);border:1px solid rgba(99,102,241,.35);border-radius:10px;padding:10px 13px;color:white;font-size:15px;font-family:'JetBrains Mono',monospace;outline:none;transition:border-color .2s}}
#inp:focus{{border-color:rgba(99,102,241,.75);box-shadow:0 0 0 3px rgba(99,102,241,.12)}}
.stats{{display:flex;gap:8px;margin-top:10px}}
.sp{{flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.09);border-radius:8px;padding:7px 8px;text-align:center}}
.sv{{font-size:15px;font-weight:700;color:#a78bfa}}.sl{{font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.07em;margin-top:1px}}
#btn{{width:100%;margin-top:12px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border:none;border-radius:10px;color:white;font-size:13px;font-weight:600;padding:10px;cursor:pointer;transition:all .2s;opacity:.4;pointer-events:none}}
#btn.ready{{opacity:1;pointer-events:all}}
#btn.ready:hover{{opacity:.9;transform:translateY(-1px)}}
#btn.done{{background:#065f46;opacity:1;pointer-events:none}}
#msg{{font-size:12px;text-align:center;margin-top:8px;color:rgba(255,255,255,.4);min-height:18px}}
.ok{{color:#6ee7b7}}.err{{color:#fca5a5}}.warn{{color:#fcd34d}}
</style></head><body>
<div class="wrap">
  <div class="lbl">Type this phrase exactly</div>
  <div class="phrase" id="ph"></div>
  <input id="inp" type="text" placeholder="Click here and start typing..." autocomplete="off" autocorrect="off" spellcheck="false"/>
  <div class="stats">
    <div class="sp"><div class="sv" id="sk">0</div><div class="sl">Keys</div></div>
    <div class="sp"><div class="sv" id="sw">—</div><div class="sl">WPM</div></div>
    <div class="sp"><div class="sv" id="sd">—</div><div class="sl">Dwell ms</div></div>
    <div class="sp"><div class="sv" id="sr">—</div><div class="sl">Rhythm</div></div>
  </div>
  <button id="btn" onclick="analyse()">🔬 Analyse My Typing Pattern</button>
  <div id="msg">Click the input box above and start typing</div>
</div>
<script>
const TGT="{TARGET}";
const WORDS=TGT.trim().split(" ").filter(w=>w.length>0).length;
const SK="{session_key}";
let kd={{}},lu=null,t0=null,ev=[],go=false;
const ph=document.getElementById("ph");

function render(v){{
  let h="";
  for(let i=0;i<TGT.length;i++){{
    const c=TGT[i]===" "?"&nbsp;":TGT[i];
    if(i<v.length) h+=`<span class="${{v[i]===TGT[i]?"ch-ok":"ch-bad"}}">${{c}}</span>`;
    else if(i===v.length) h+=`<span class="ch-cur">${{c}}</span>`;
    else h+=`<span class="ch-dim">${{c}}</span>`;
  }}
  ph.innerHTML=h;
}}
render("");

const inp=document.getElementById("inp");
const btn=document.getElementById("btn");
const msg=document.getElementById("msg");

inp.addEventListener("focus",()=>{{
  if(!go){{go=true;ev=[];kd={{}};lu=null;t0=performance.now();msg.textContent="Capturing keystrokes...";msg.className="";}}
}});
inp.addEventListener("keydown",e=>{{if(!go)return;kd[e.code]=performance.now();}});
inp.addEventListener("keyup",e=>{{
  if(!go)return;
  const now=performance.now();
  const dw=kd[e.code]!==undefined?now-kd[e.code]:null;
  const fl=lu!==null?now-lu:null;
  if(dw!==null&&dw>0) ev.push({{dwell:Math.round(dw*10)/10,flight:fl!==null?Math.round(fl*10)/10:null}});
  lu=now;
  const vl=ev.filter(e=>e.dwell>0);
  document.getElementById("sk").textContent=vl.length;
  if(vl.length>=3){{
    const dws=vl.map(e=>e.dwell);
    const avg=a=>a.reduce((x,y)=>x+y,0)/a.length;
    document.getElementById("sd").textContent=Math.round(avg(dws))+"ms";
    const fls=ev.filter(e=>e.flight!==null&&e.flight>0).map(e=>e.flight);
    if(fls.length>=2){{
      const mf=avg(fls);
      const sf=Math.sqrt(fls.map(f=>(f-mf)**2).reduce((x,y)=>x+y,0)/fls.length);
      document.getElementById("sr").textContent=(1/(1+sf/Math.max(mf,1))).toFixed(2);
    }}
    if(t0) document.getElementById("sw").textContent=Math.min(Math.round(WORDS/Math.max((performance.now()-t0)/60000,.001)),350);
  }}
}});
inp.addEventListener("input",()=>{{
  const v=inp.value; render(v);
  const done=v===TGT;
  btn.classList.toggle("ready",done);
  if(done) {{msg.textContent="✅ Phrase complete! Click Analyse.";msg.className="ok";}}
  else if(v.length>0) {{
    const pct=Math.round(v.length/TGT.length*100);
    msg.textContent=pct+"% — keep typing...";msg.className="warn";
  }}
}});

function avg(a){{return a.reduce((x,y)=>x+y,0)/a.length;}}
function std(a){{const m=avg(a);return Math.sqrt(a.map(v=>(v-m)**2).reduce((x,y)=>x+y,0)/a.length);}}
function med(a){{const s=[...a].sort((x,y)=>x-y);return s[Math.floor(s.length/2)];}}

function analyse(){{
  const vl=ev.filter(e=>e.dwell!==null&&e.dwell>5&&e.dwell<2000);
  const fls=ev.filter(e=>e.flight!==null&&e.flight>5&&e.flight<3000).map(e=>e.flight);
  if(vl.length<8){{msg.textContent="Not enough data — retype the phrase.";msg.className="err";return;}}
  const dw=vl.map(e=>e.dwell);
  const mD=avg(dw),mF=fls.length>0?avg(fls):mD*1.2,sF=fls.length>1?std(fls):mF*0.3;
  const tot=t0?performance.now()-t0:3000;
  const wpm=Math.min(Math.round(WORDS/Math.max(tot/60000,.001)),350);
  const feat={{
    mean_dwell:Math.round(mD*10)/10,
    std_dwell:Math.round(std(dw)*10)/10,
    median_dwell:Math.round(med(dw)*10)/10,
    max_dwell:Math.round(Math.max(...dw)*10)/10,
    mean_flight:Math.round(mF*10)/10,
    std_flight:Math.round(sF*10)/10,
    median_flight:fls.length>0?Math.round(med(fls)*10)/10:Math.round(mF*10)/10,
    min_flight:fls.length>0?Math.round(Math.min(...fls)*10)/10:20,
    typing_speed_wpm:wpm,
    dwell_flight_ratio:Math.round(mD/Math.max(mF,1)*1000)/1000,
    rhythm_consistency:Math.round(1/(1+sF/Math.max(mF,1))*1000)/1000,
    total_time_ms:Math.round(tot),
    n_keys:vl.length
  }};
  const json=JSON.stringify(feat);
  // Send to Python via URL query param
  try{{
    const url=new URL(window.parent.location.href);
    url.searchParams.set("ks_key",SK);
    url.searchParams.set("ks_json",encodeURIComponent(json));
    window.parent.history.replaceState(null,"",url.toString());
  }}catch(e){{console.warn(e);}}
  btn.textContent="✅ Done — click Save/Verify above";
  btn.classList.remove("ready");
  btn.classList.add("done");
  msg.textContent="✅ Keystroke data captured! Use the button above in Streamlit.";
  msg.className="ok";
}}
</script></body></html>"""

    components.html(widget_html, height=310, scrolling=False)

    if feat_ready:
        f = feat_ready
        st.success(f"✅ Keystroke data captured!  Dwell: {f['mean_dwell']:.0f} ms  ·  Flight: {f['mean_flight']:.0f} ms  ·  WPM: {f['typing_speed_wpm']:.0f}  ·  Rhythm: {f['rhythm_consistency']:.2f}")

    return feat_ready


def clear_widget(session_key: str):
    """Clear captured keystroke data for a widget."""
    k = session_key + "_feat"
    if k in st.session_state:
        del st.session_state[k]


# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════
def hash_password(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def verify_password(stored: str, entered: str) -> bool:
    return stored == hash_password(entered)


# ══════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════
def _init():
    for k, v in {
        "page":         "home",
        "dm":           DataManager(),
        "model":        BehavioralAuthModel(),
        "reg_user":     None,
        "auth_result":  None,
        "auth_history": [],
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()
dm    = st.session_state.dm
model = st.session_state.model
QUAL  = ["#6366f1","#06b6d4","#10b981","#f59e0b","#ef4444","#ec4899","#8b5cf6","#14b8a6"]

def dark_layout(fig, h=380, m=None):
    m = m or dict(l=20,r=20,t=30,b=20)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,17,23,0.6)",
        font=dict(family="Inter,sans-serif", color="rgba(255,255,255,0.65)", size=11),
        height=h, margin=m,
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:.5rem 0 1rem'>
        <div style='font-size:2rem'>🛡️</div>
        <div style='font-size:1.1rem;font-weight:800;background:linear-gradient(135deg,#a78bfa,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>BehaviorAuth</div>
        <div style='font-size:.62rem;color:rgba(255,255,255,.3);letter-spacing:.08em;text-transform:uppercase'>Password + Keystroke 2FA</div>
    </div>""", unsafe_allow_html=True)

    for icon, label, pid in [
        ("🏠","Home","home"), ("👤","Register User","register"),
        ("🎓","Train Model","train"), ("🔑","Authenticate","authenticate"),
        ("⚔️","Attack Test","attack"), ("📊","Analytics","dashboard"),
        ("📖","How It Works","howto"),
    ]:
        t = "primary" if st.session_state.page == pid else "secondary"
        if st.button(f"{icon}  {label}", use_container_width=True, type=t, key=f"nav_{pid}"):
            st.session_state.page = pid
            st.session_state.auth_result = None
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    ul = dm.get_all_users()
    ca,cb = st.columns(2)
    ca.markdown(f"<div style='text-align:center'><div style='font-size:1.3rem;font-weight:800;color:#a78bfa'>{len(ul)}</div><div style='font-size:.62rem;color:rgba(255,255,255,.4);text-transform:uppercase'>Users</div></div>", unsafe_allow_html=True)
    ts = sum(dm.get_sample_count(u) for u in ul)
    cb.markdown(f"<div style='text-align:center'><div style='font-size:1.3rem;font-weight:800;color:#06b6d4'>{ts}</div><div style='font-size:.62rem;color:rgba(255,255,255,.4);text-transform:uppercase'>Samples</div></div>", unsafe_allow_html=True)
    for u in ul:
        cnt=dm.get_sample_count(u); dot="🟢" if cnt>=5 else "🟡"
        st.markdown(f"<div class='user-item'><span>● {u}</span><span style='color:#6366f1;font-size:.78rem;font-weight:600'>{cnt} {dot}</span></div>", unsafe_allow_html=True)
    if model.is_trained:
        st.markdown(f"<div style='margin-top:.8rem;background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);border-radius:10px;padding:.6rem;text-align:center'><div style='font-size:.62rem;color:rgba(255,255,255,.4);text-transform:uppercase'>Model Accuracy</div><div style='font-size:1.4rem;font-weight:800;color:#10b981'>{model.accuracy*100:.1f}%</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:1.2rem;font-size:.6rem;color:rgba(255,255,255,.2);text-align:center'>IIIT Raichur · AD23B1021</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div class='hero'>
        <h1>🛡️ Two-Factor Behavioral Authentication</h1>
        <p>Layer 1: Password &nbsp;+&nbsp; Layer 2: Real Keystroke Dynamics &nbsp;→&nbsp; Both required</p>
    </div>""", unsafe_allow_html=True)

    ul=dm.get_all_users(); total=sum(dm.get_sample_count(u) for u in ul)
    acc=f"{model.accuracy*100:.1f}%" if model.is_trained else "—"
    c1,c2,c3,c4=st.columns(4)
    for col,val,lbl,color in [(c1,str(len(ul)),"Users","#a78bfa"),(c2,str(total),"Samples","#06b6d4"),(c3,acc,"Accuracy","#10b981"),(c4,"Real JS","Capture","#f59e0b")]:
        col.markdown(f"<div class='stat-card'><div class='stat-num' style='color:{color};font-size:1.6rem'>{val}</div><div class='stat-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    cl,cr=st.columns([3,2])
    with cl:
        st.markdown("<div class='section-title'>How the 2FA system works</div>", unsafe_allow_html=True)
        for icon,bg,title,desc in [
            ("🔑","rgba(6,182,212,.15)","Layer 1 — Password","SHA-256 hashed. Must match stored hash exactly."),
            ("⌨️","rgba(99,102,241,.15)","Layer 2 — Real keystroke timing","JS measures actual keydown/keyup ms. Features compared to enrolled profile."),
            ("🧠","rgba(16,185,129,.15)","ML classification","13 features → RF+SVM ensemble → probability per user."),
            ("🔐","rgba(245,158,11,.15)","Both must pass","Wrong password OR wrong rhythm → DENIED automatically."),
        ]:
            st.markdown(f"<div style='display:flex;gap:1rem;margin-bottom:1rem;align-items:flex-start'><div style='width:40px;height:40px;border-radius:12px;background:{bg};display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0'>{icon}</div><div><div style='font-size:.9rem;font-weight:600;color:white'>{title}</div><div style='font-size:.78rem;color:rgba(255,255,255,.45);margin-top:.15rem;line-height:1.5'>{desc}</div></div></div>", unsafe_allow_html=True)
    with cr:
        st.markdown("<div class='section-title'>Why real keystroke capture?</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='glass' style='font-size:.82rem;color:rgba(255,255,255,.7);line-height:1.8'>
            Previous versions <b style='color:#fca5a5'>simulated</b> typing features based on the username — which meant anyone with the correct password could get in.<br><br>
            This version uses <b style='color:#6ee7b7'>real JavaScript</b> to measure your actual keydown/keyup timestamps. The model compares <em>how you actually typed</em> against your enrolled samples.<br><br>
            An impostor with your password but different typing rhythm will be <b style='color:#fca5a5'>denied by Layer 2</b>.
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    qa,qb,qc=st.columns(3)
    for col,lbl,pid in [(qa,"👤 Register","register"),(qb,"🎓 Train","train"),(qc,"🔑 Authenticate","authenticate")]:
        with col:
            if st.button(lbl, use_container_width=True, type="primary"):
                st.session_state.page=pid; st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# PAGE: REGISTER
# ══════════════════════════════════════════════════════════════════════════
def page_register():
    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>👤 Register New User</h1><p>Set your password and enroll your real typing pattern</p></div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3,2])

    with col_l:
        # Account creation
        st.markdown("<div class='section-title'>Step 1 — Create account</div>", unsafe_allow_html=True)
        with st.form("reg_form", clear_on_submit=True):
            new_user = st.text_input("Username", placeholder="e.g. Harsh (no spaces)")
            new_pwd  = st.text_input("Password", type="password", placeholder="Min 4 characters")
            cfm_pwd  = st.text_input("Confirm Password", type="password", placeholder="Retype password")
            create   = st.form_submit_button("✅ Create Account", type="primary", use_container_width=True)

        if create:
            if not new_user.strip():
                st.error("Enter a username.")
            elif " " in new_user.strip():
                st.error("Username cannot have spaces.")
            elif len(new_pwd) < 4:
                st.error("Password must be at least 4 characters.")
            elif new_pwd != cfm_pwd:
                st.error("Passwords do not match.")
            elif new_user.strip() in dm.get_all_users():
                st.warning(f"'{new_user.strip()}' already exists. Select below to add samples.")
            else:
                dm.register_user(new_user.strip())
                dm.store_password(new_user.strip(), hash_password(new_pwd))
                st.session_state.reg_user = new_user.strip()
                st.success(f"✅ Account created for **{new_user.strip()}**!")

        # Select existing
        st.markdown("<div class='section-title'>Or select existing user</div>", unsafe_allow_html=True)
        all_users = dm.get_all_users()
        if all_users:
            sel = st.selectbox("Select:", ["— select —"] + all_users, key="reg_sel")
            if sel != "— select —":
                st.session_state.reg_user = sel

        # Sample collection
        user = st.session_state.reg_user
        if user and user in dm.get_all_users():
            count = dm.get_sample_count(user)
            st.markdown(f"<div class='section-title'>Step 2 — Capture a sample for <span style='color:#a78bfa'>{user}</span></div>", unsafe_allow_html=True)
            st.progress(min(count/10,1.0), text=f"{count}/10 samples collected")

            st.markdown(f"""
            <div class='info-box'>
                Type <b>'{TARGET}'</b> in the box below. JS measures every keystroke.
                When you finish, click <b>Analyse My Typing Pattern</b>.
                Then click <b>✅ Save This Sample</b>.
            </div>""", unsafe_allow_html=True)

            # Real keystroke capture
            wkey = f"reg_{user}_{count}"
            feat = keystroke_widget(wkey)

            if feat:
                if st.button("✅ Save This Sample", type="primary", use_container_width=True, key=f"save_{count}"):
                    dm.add_sample(user, TARGET, feat)
                    clear_widget(wkey)
                    new_count = dm.get_sample_count(user)
                    st.success(f"✅ Sample {new_count}/10 saved!")
                    time.sleep(0.3)
                    st.rerun()
            else:
                st.button("✅ Save This Sample", disabled=True,
                          use_container_width=True, key=f"save_dis_{count}",
                          help="Type the phrase and click Analyse first")
                st.caption("Save button enables after you analyse your typing above.")

            if count >= 10:
                st.markdown("<div class='success-box'>✅ Profile complete! Go to Train Model.</div>", unsafe_allow_html=True)
                if st.button("🎓 Train Model Now →", use_container_width=True, type="primary"):
                    st.session_state.page="train"; st.rerun()

    with col_r:
        st.markdown("<div class='section-title'>Registration guide</div>", unsafe_allow_html=True)
        for n,t,d in [
            ("1","Create account","Username + password. Password hashed with SHA-256."),
            ("2","Click the typing box","JS starts capturing your keystrokes immediately."),
            ("3","Type the phrase naturally","Don't rush — your natural rhythm is what matters."),
            ("4","Click Analyse","Features computed from your real timing."),
            ("5","Click Save Sample","Sample stored. Repeat 10 times."),
            ("6","Train the model","ML learns YOUR typing pattern."),
        ]:
            st.markdown(f"<div style='display:flex;gap:.8rem;margin-bottom:.9rem;align-items:flex-start'><div class='step-badge'>{n}</div><div><div style='font-size:.88rem;font-weight:600;color:white'>{t}</div><div style='font-size:.76rem;color:rgba(255,255,255,.4);margin-top:.1rem'>{d}</div></div></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title' style='margin-top:1rem'>All profiles</div>", unsafe_allow_html=True)
        for u in dm.get_all_users():
            cnt=dm.get_sample_count(u); pct=min(cnt/10,1.0)
            clr="#10b981" if cnt>=10 else "#f59e0b" if cnt>=5 else "#ef4444"
            st.markdown(f"<div class='glass' style='padding:.8rem 1rem;margin-bottom:.5rem'><div style='display:flex;justify-content:space-between;margin-bottom:.35rem'><span style='font-weight:600;font-size:.85rem;color:white'>{u}</span><span style='font-size:.75rem;color:{clr};font-weight:600'>{cnt}/10</span></div><div style='background:rgba(255,255,255,.06);border-radius:99px;height:4px'><div style='width:{pct*100:.0f}%;height:100%;background:{clr};border-radius:99px'></div></div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE: TRAIN
# ══════════════════════════════════════════════════════════════════════════
def page_train():
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        HP=True
    except ImportError:
        HP=False

    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>🎓 Train ML Model</h1><p>Train RF+SVM ensemble on your real enrolled typing samples</p></div>", unsafe_allow_html=True)
    users=dm.get_all_users()
    if len(users)<2:
        st.markdown("<div class='warn-box'>⚠️ Need at least 2 users with 5+ samples each.</div>", unsafe_allow_html=True); return

    cl,cr=st.columns([2,3])
    with cl:
        st.markdown("<div class='section-title'>Configuration</div>", unsafe_allow_html=True)
        n_trees=st.slider("🌳 RF Trees",50,300,100,50)
        test_size=st.slider("🔬 Test ratio",0.10,0.40,0.20,0.05)
        st.markdown("<div class='glass' style='font-size:.82rem;color:rgba(255,255,255,.7);line-height:1.8'><b style='color:#a78bfa'>Random Forest</b> — 100 trees, majority vote<br><b style='color:#06b6d4'>SVM RBF</b> — optimal class boundaries<br><b style='color:#10b981'>Ensemble</b> — 60% RF + 40% SVM<br><b style='color:#f59e0b'>Threshold</b> — 45% min confidence</div>", unsafe_allow_html=True)
    with cr:
        st.markdown("<div class='section-title'>Sample readiness</div>", unsafe_allow_html=True)
        for u in users:
            cnt=dm.get_sample_count(u); pct=min(cnt/10,1.0)
            clr="#10b981" if cnt>=10 else "#f59e0b" if cnt>=5 else "#ef4444"
            ok="✅ Ready" if cnt>=5 else "⚠️ Need more"
            st.markdown(f"<div class='glass' style='padding:.8rem 1rem;margin-bottom:.5rem'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem'><span style='font-weight:600;color:white'>{u}</span><span style='font-size:.75rem;color:{clr};font-weight:600'>{ok} · {cnt}</span></div><div style='background:rgba(255,255,255,.06);border-radius:99px;height:5px'><div style='width:{pct*100:.0f}%;height:100%;background:linear-gradient(90deg,{clr},{clr}88);border-radius:99px'></div></div></div>", unsafe_allow_html=True)

    if len([u for u in users if dm.get_sample_count(u)>=5])<2:
        st.markdown("<div class='warn-box'>⚠️ At least 2 users need 5+ samples.</div>", unsafe_allow_html=True); return

    if st.button("🚀 Train Model Now", type="primary", use_container_width=True):
        pb=st.progress(0,"Preparing..."); time.sleep(0.3)
        X,y=dm.build_dataset()
        pb.progress(35,"Training Random Forest..."); time.sleep(0.4)
        results=model.train(X,y,n_estimators=n_trees,test_size=test_size)
        pb.progress(80,"Training SVM..."); time.sleep(0.3)
        pb.progress(100,"Complete!"); time.sleep(0.2); pb.empty()

        acc=results['accuracy']*100
        st.markdown(f"<div style='background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(6,182,212,.08));border:1.5px solid rgba(16,185,129,.4);border-radius:16px;padding:1.4rem;text-align:center;margin:1rem 0'><div style='font-size:3rem;font-weight:800;color:#10b981;line-height:1'>{acc:.1f}%</div><div style='color:rgba(255,255,255,.55);font-size:.88rem;margin-top:.3rem'>Ensemble Accuracy (RF+SVM)</div></div>", unsafe_allow_html=True)
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Train",results['n_train']); m2.metric("Test",results['n_test'])
        m3.metric("Features",results['n_features']); m4.metric("RF/SVM",f"{results['rf_accuracy']*100:.0f}%/{results['svm_accuracy']*100:.0f}%")

        if HP:
            t1,t2,t3=st.tabs(["📊 Feature Importance","🔲 Confusion Matrix","🔵 Clusters"])
            with t1:
                fi=results['feature_importance']
                fig=go.Figure(go.Bar(x=list(fi.values()),y=list(fi.keys()),orientation='h',
                    marker=dict(color=list(fi.values()),colorscale=[[0,"#1e1344"],[0.5,"#6366f1"],[1,"#a78bfa"]],showscale=False,line=dict(width=0)),
                    text=[f"{v:.3f}" for v in fi.values()],textposition='outside',textfont=dict(color="rgba(255,255,255,.5)",size=10)))
                dark_layout(fig,400); st.plotly_chart(fig,use_container_width=True)
            with t2:
                cm=results['confusion_matrix']; lb=results['class_labels']
                fig2=go.Figure(go.Heatmap(z=cm,x=lb,y=lb,colorscale=[[0,"#0d1117"],[0.5,"#312e81"],[1,"#a78bfa"]],text=cm,texttemplate="%{text}",showscale=True))
                fig2.update_layout(xaxis_title="Predicted",yaxis_title="Actual",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,.6)",font=dict(color="rgba(255,255,255,.65)"),height=380,margin=dict(l=60,r=20,t=20,b=60))
                st.plotly_chart(fig2,use_container_width=True)
            with t3:
                import pandas as pd
                af=[]
                for u in users:
                    for s in dm.get_samples(u): r=s['features'].copy(); r['user']=u; af.append(r)
                if af:
                    df=pd.DataFrame(af)
                    fig3=px.scatter(df,x='mean_dwell',y='mean_flight',color='user',size='typing_speed_wpm',color_discrete_sequence=QUAL,title="User clusters — real typing data")
                    dark_layout(fig3,380); st.plotly_chart(fig3,use_container_width=True)
        st.balloons()


# ══════════════════════════════════════════════════════════════════════════
# PAGE: AUTHENTICATE — Real keystroke + Password
# ══════════════════════════════════════════════════════════════════════════
def page_authenticate():
    try:
        import plotly.graph_objects as go
        HP=True
    except ImportError:
        HP=False

    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>🔑 Two-Factor Authentication</h1><p>Password + your actual typing rhythm — both must match</p></div>", unsafe_allow_html=True)

    if not model.is_trained:
        st.markdown("<div class='warn-box'>⚠️ Model not trained. Go to Train Model first.</div>", unsafe_allow_html=True); return

    users=dm.get_all_users()
    col_in, col_out=st.columns([2,3])

    with col_in:
        st.markdown("<div class='section-title'>Your credentials</div>", unsafe_allow_html=True)
        claimed=st.selectbox("Username:", users, key="auth_sel")
        password=st.text_input("🔑 Password:", type="password", placeholder="Enter your password", key="auth_pwd")

        st.markdown("<div class='section-title'>Capture typing pattern (Layer 2)</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
            Type the phrase below. JS captures your real keystroke timing.
            Click <b>Analyse</b> when done, then click <b>Verify Identity</b>.
        </div>""", unsafe_allow_html=True)

        feat = keystroke_widget("auth_capture")

        # Verify button — active only when password entered + keystroke captured
        ready = bool(password) and (feat is not None)
        if st.button(
            "🔐 Verify My Identity" if ready else ("Enter password + type phrase first" if not feat else "Enter your password first"),
            type="primary" if ready else "secondary",
            disabled=not ready,
            use_container_width=True,
            key="verify_btn"
        ):
            with st.spinner("Verifying both factors..."):
                time.sleep(0.5)

                # Layer 1: Password
                stored = dm.get_password(claimed)
                pwd_ok = verify_password(stored, password) if stored else False

                # Layer 2: Behavioral — using REAL captured features
                result  = model.predict(feat, claimed)
                beh_ok  = result['authenticated']
                conf    = result['confidence']
                pred    = result['predicted_user']
                granted = pwd_ok and beh_ok

                st.session_state.auth_result = {
                    "granted":  granted,
                    "pwd_ok":   pwd_ok,
                    "beh_ok":   beh_ok,
                    "conf":     conf,
                    "pred":     pred,
                    "claimed":  claimed,
                    "probs":    result['all_probabilities'],
                    "feat":     feat,
                    "ts":       time.strftime("%H:%M:%S"),
                }
                st.session_state.auth_history.append({
                    "user":    claimed, "granted": granted,
                    "pwd_ok":  pwd_ok,  "beh_ok":  beh_ok,
                    "conf":    conf,    "pred":    pred,
                    "time":    time.strftime("%H:%M:%S"),
                })
                clear_widget("auth_capture")
            st.rerun()

        if not password and feat:
            st.caption("✅ Typing captured. Now enter your password above.")
        elif password and not feat:
            st.caption("✅ Password entered. Now type the phrase above and click Analyse.")

        # History
        if st.session_state.auth_history:
            st.markdown("<div class='section-title' style='margin-top:1rem'>History</div>", unsafe_allow_html=True)
            for h in reversed(st.session_state.auth_history[-5:]):
                icon="✅" if h['granted'] else "❌"; color="#10b981" if h['granted'] else "#ef4444"
                p1="🔑✓" if h['pwd_ok'] else "🔑✗"; p2="⌨️✓" if h['beh_ok'] else "⌨️✗"
                st.markdown(f"<div class='glass' style='padding:.5rem .9rem;margin-bottom:.35rem'><div style='display:flex;justify-content:space-between;align-items:center'><span style='font-size:.82rem;color:white;font-weight:500'>{icon} {h['user']}</span><span style='font-size:.7rem;color:{color};font-weight:600'>{p1} {p2} · {h['time']}</span></div></div>", unsafe_allow_html=True)

    with col_out:
        result=st.session_state.auth_result
        if not result:
            st.markdown("""
            <div class='glass' style='text-align:center;padding:3rem 2rem;margin-top:1.5rem'>
                <div style='font-size:3rem;margin-bottom:1rem'>🔒</div>
                <div style='font-weight:600;color:rgba(255,255,255,.5)'>Awaiting authentication</div>
                <div style='color:rgba(255,255,255,.3);font-size:.82rem;margin-top:.4rem'>
                    Enter password → type phrase → click Verify
                </div>
            </div>""", unsafe_allow_html=True); return

        granted=result['granted']; pwd_ok=result['pwd_ok']; beh_ok=result['beh_ok']
        conf=result['conf']*100; pred=result['pred']; claimed_u=result['claimed']

        if granted:
            st.markdown(f"<div class='result-ok'><div style='font-size:2.5rem;margin-bottom:.5rem'>✅</div><div style='font-size:1.6rem;font-weight:800;color:#6ee7b7'>ACCESS GRANTED</div><div style='font-size:1rem;color:#10b981;margin:.3rem 0'>Welcome, <b>{claimed_u}</b>!</div><div style='font-size:.85rem;color:rgba(255,255,255,.55);margin-top:.3rem'>Both factors verified ✓</div></div>", unsafe_allow_html=True)
        else:
            reason=[]
            if not pwd_ok: reason.append("wrong password")
            if not beh_ok: reason.append(f"typing matched '{pred}' not '{claimed_u}'")
            st.markdown(f"<div class='result-fail'><div style='font-size:2.5rem;margin-bottom:.5rem'>🚫</div><div style='font-size:1.6rem;font-weight:800;color:#fca5a5'>ACCESS DENIED</div><div style='font-size:.9rem;color:#ef4444;margin:.4rem 0'>Reason: {' + '.join(reason)}</div></div>", unsafe_allow_html=True)

        # Factor breakdown
        st.markdown("<div class='section-title'>Factor breakdown</div>", unsafe_allow_html=True)
        fc1,fc2=st.columns(2)
        for col,(ok,lbl) in [(fc1,(pwd_ok,"Layer 1: Password")),(fc2,(beh_ok,"Layer 2: Typing Rhythm"))]:
            c="#10b981" if ok else "#ef4444"; ic="✅" if ok else "❌"; tx="Passed" if ok else "Failed"
            col.markdown(f"<div class='glass' style='text-align:center;padding:1rem;border-color:{c}44'><div style='font-size:1.5rem'>{ic}</div><div style='font-size:.9rem;font-weight:700;color:{c};margin-top:.3rem'>{lbl}</div><div style='font-size:.8rem;color:rgba(255,255,255,.55);margin-top:.2rem'>{tx}</div></div>", unsafe_allow_html=True)

        # Probability chart
        probs=result['probs']
        if HP:
            colors=['rgba(16,185,129,.85)' if k==claimed_u else 'rgba(99,102,241,.6)' for k in probs]
            fig=go.Figure(go.Bar(x=list(probs.values()),y=list(probs.keys()),orientation='h',marker_color=colors,marker_line_width=0,text=[f"{v*100:.1f}%" for v in probs.values()],textposition='outside',textfont=dict(color="rgba(255,255,255,.7)",size=11)))
            dark_layout(fig,max(180,55*len(probs)),dict(l=10,r=60,t=10,b=20))
            st.plotly_chart(fig,use_container_width=True)

        if result.get('feat'):
            f=result['feat']
            st.markdown("<div class='section-title'>Your keystroke features (real measured)</div>", unsafe_allow_html=True)
            r1,r2,r3=st.columns(3)
            r1.metric("Mean Dwell",f"{f['mean_dwell']:.1f} ms")
            r2.metric("Mean Flight",f"{f['mean_flight']:.1f} ms")
            r3.metric("WPM",f"{f['typing_speed_wpm']:.0f}")
            r1.metric("Rhythm",f"{f['rhythm_consistency']:.3f}")
            r2.metric("Dwell/Flight",f"{f['dwell_flight_ratio']:.2f}")
            r3.metric("Keys",str(f['n_keys']))


# ══════════════════════════════════════════════════════════════════════════
# PAGE: ATTACK TEST
# ══════════════════════════════════════════════════════════════════════════
def page_attack():
    try:
        import plotly.graph_objects as go
        HP=True
    except ImportError:
        HP=False

    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>⚔️ Attack Simulator</h1><p>Test how many simulated impostor attacks bypass 2FA</p></div>", unsafe_allow_html=True)
    if not model.is_trained:
        st.markdown("<div class='warn-box'>⚠️ Train the model first.</div>", unsafe_allow_html=True); return

    users=dm.get_all_users()
    cl,cr=st.columns([2,3])
    with cl:
        atype=st.selectbox("Attack type",["Brute Force — random timing","Impostor — different user rhythm","Replay — slight copy","Mimicry — deliberate copy"])
        target=st.selectbox("Target user",users)
        n_att=st.slider("Attempts",10,100,50)
        run=st.button("🚨 Launch Attack",type="primary",use_container_width=True)

    with cr:
        if not run:
            st.markdown("<div class='glass' style='text-align:center;padding:2.5rem'><div style='font-size:2rem;margin-bottom:.6rem'>⚔️</div><div style='color:rgba(255,255,255,.4)'>Configure and launch</div></div>", unsafe_allow_html=True); return

        def sim_persona(user, seed=0):
            """Simulate features for a known persona (for attack simulation only)."""
            P={"Alice":dict(b_d=68,b_f=52,n=7,w=92),"Bob":dict(b_d=162,b_f=145,n=32,w=38),"Charlie":dict(b_d=108,b_f=205,n=11,w=53),"Diana":dict(b_d=93,b_f=68,n=5,w=78)}
            p=P.get(user,dict(b_d=120,b_f=100,n=20,w=60))
            rng=np.random.RandomState(sum(ord(c) for c in user)+seed); n=25
            dw=np.clip(rng.normal(p["b_d"],p["n"],n),30,400)
            fl=np.clip(rng.normal(p["b_f"],p["n"]*1.5,n),20,500)
            ms=float(np.sum(dw)+np.sum(fl)); wpm=float(np.clip(p["w"]+rng.normal(0,4),10,200))
            return {"mean_dwell":float(np.mean(dw)),"std_dwell":float(np.std(dw)),"median_dwell":float(np.median(dw)),"max_dwell":float(np.max(dw)),"mean_flight":float(np.mean(fl)),"std_flight":float(np.std(fl)),"median_flight":float(np.median(fl)),"min_flight":float(np.min(fl)),"typing_speed_wpm":wpm,"dwell_flight_ratio":float(np.mean(dw)/max(np.mean(fl),1)),"rhythm_consistency":float(1/(1+np.std(fl)/max(np.mean(fl),1))),"total_time_ms":ms,"n_keys":n}

        with st.spinner(f"Running {n_att} attacks..."):
            time.sleep(0.4); res_list=[]; others=[u for u in users if u!=target]
            for i in range(n_att):
                rng=np.random.RandomState(i*31+7)
                if "Brute" in atype:
                    feat={"mean_dwell":float(rng.uniform(50,250)),"std_dwell":float(rng.uniform(5,60)),"median_dwell":float(rng.uniform(50,250)),"max_dwell":float(rng.uniform(100,400)),"mean_flight":float(rng.uniform(40,300)),"std_flight":float(rng.uniform(5,80)),"median_flight":float(rng.uniform(40,300)),"min_flight":float(rng.uniform(20,100)),"typing_speed_wpm":float(rng.uniform(20,150)),"dwell_flight_ratio":float(rng.uniform(0.3,3.0)),"rhythm_consistency":float(rng.uniform(0.2,0.95)),"total_time_ms":float(rng.uniform(2000,15000)),"n_keys":25}
                elif "Impostor" in atype and others:
                    feat=sim_persona(others[i%len(others)],seed=i*13)
                elif "Replay" in atype:
                    feat=sim_persona(target,seed=i*7)
                    for k in ["mean_dwell","mean_flight"]: feat[k]=float(np.clip(feat[k]+rng.uniform(-5,5),1,500))
                else:
                    feat=sim_persona(target,seed=i*3)
                    for k in ["mean_dwell","mean_flight","std_dwell","std_flight"]: feat[k]=float(np.clip(feat[k]+rng.uniform(-20,20),1,500))
                r=model.predict(feat,target)
                res_list.append({"attempt":i+1,"granted":r['authenticated'],"confidence":r['confidence']})

        granted_n=sum(1 for r in res_list if r['granted']); denied_n=n_att-granted_n
        far=granted_n/n_att*100; avg_c=np.mean([r['confidence'] for r in res_list])*100
        sc="🟢 SECURE" if far<5 else "🟡 MODERATE" if far<20 else "🔴 CRITICAL"
        sc_col="#10b981" if far<5 else "#f59e0b" if far<20 else "#ef4444"
        st.markdown(f"<div style='background:rgba(239,68,68,.1);border:1.5px solid rgba(239,68,68,.3);border-radius:16px;padding:1.2rem;text-align:center;margin-bottom:1rem'><div style='font-size:1.5rem;font-weight:800;color:{sc_col}'>{sc}</div><div style='font-size:.82rem;color:rgba(255,255,255,.5);margin-top:.2rem'>FAR: <b style='color:{sc_col}'>{far:.1f}%</b></div></div>", unsafe_allow_html=True)
        s1,s2,s3,s4=st.columns(4)
        s1.metric("Attacks",n_att); s2.metric("🔴 Breached",granted_n); s3.metric("🟢 Blocked",denied_n); s4.metric("Avg Conf",f"{avg_c:.1f}%")
        if HP:
            cb=['rgba(239,68,68,.8)' if r['granted'] else 'rgba(99,102,241,.5)' for r in res_list]
            fig=go.Figure(); fig.add_trace(go.Bar(x=[r['attempt'] for r in res_list],y=[r['confidence']*100 for r in res_list],marker_color=cb,marker_line_width=0,name="Confidence"))
            fig.add_hline(y=45,line_dash="dash",line_color="rgba(245,158,11,.8)",annotation_text="45% threshold",annotation_font_color="rgba(245,158,11,.9)")
            dark_layout(fig,280,dict(l=40,r=20,t=30,b=40)); st.plotly_chart(fig,use_container_width=True)
            fig2=go.Figure(go.Pie(labels=["Blocked","Breached"],values=[denied_n,granted_n],marker_colors=["rgba(99,102,241,.8)","rgba(239,68,68,.8)"],hole=0.55,textinfo='percent+label',textfont_size=11))
            dark_layout(fig2,220,dict(l=10,r=10,t=10,b=10)); st.plotly_chart(fig2,use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════
def page_dashboard():
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd
        HP=True
    except ImportError:
        import pandas as pd; HP=False

    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>📊 Analytics</h1></div>", unsafe_allow_html=True)
    users=dm.get_all_users()
    if not users: st.info("No users yet."); return
    import pandas as pd
    af=[]
    for u in users:
        for s in dm.get_samples(u): r=s['features'].copy(); r['user']=u; af.append(r)
    if not af: st.info("No samples yet."); return
    df=pd.DataFrame(af)

    kpis=[("Samples",str(len(df)),"#a78bfa"),("Users",str(df['user'].nunique()),"#06b6d4"),("Avg Dwell",f"{df['mean_dwell'].mean():.0f} ms","#10b981"),("Avg WPM",f"{df['typing_speed_wpm'].mean():.0f}","#f59e0b")]
    kpi_cols=st.columns(4)
    for col,kpi in zip(kpi_cols,kpis):
        lbl,val,color=kpi
        col.markdown(f"<div class='stat-card'><div class='stat-num' style='color:{color};font-size:1.4rem'>{val}</div><div class='stat-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    if not HP: st.info("pip install plotly for charts"); st.dataframe(df,use_container_width=True); return
    st.markdown("<hr>", unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["🔵 Clusters","📦 Distributions","🔥 Correlation","📋 Data"])
    with t1:
        c1,c2=st.columns(2)
        with c1:
            fig=px.scatter(df,x='mean_dwell',y='mean_flight',color='user',size='typing_speed_wpm',color_discrete_sequence=QUAL,title="Dwell vs Flight — user clusters")
            dark_layout(fig,380); st.plotly_chart(fig,use_container_width=True)
        with c2:
            fig2=px.scatter(df,x='typing_speed_wpm',y='rhythm_consistency',color='user',size='std_dwell',color_discrete_sequence=QUAL,title="Speed vs Rhythm")
            dark_layout(fig2,380); st.plotly_chart(fig2,use_container_width=True)
    with t2:
        sel=st.selectbox("Feature:",["mean_dwell","mean_flight","typing_speed_wpm","rhythm_consistency","std_dwell","std_flight"])
        c1,c2=st.columns(2)
        with c1:
            fig3=px.box(df,x='user',y=sel,color='user',color_discrete_sequence=QUAL,title=f"Box: {sel}")
            dark_layout(fig3,360); st.plotly_chart(fig3,use_container_width=True)
        with c2:
            fig4=px.violin(df,x='user',y=sel,color='user',color_discrete_sequence=QUAL,box=True,title=f"Violin: {sel}")
            dark_layout(fig4,360); st.plotly_chart(fig4,use_container_width=True)
    with t3:
        nc=["mean_dwell","std_dwell","mean_flight","std_flight","typing_speed_wpm","dwell_flight_ratio","rhythm_consistency"]
        corr=df[nc].corr()
        fig5=go.Figure(go.Heatmap(z=corr.values,x=corr.columns,y=corr.index,colorscale=[[0,"#0a0014"],[0.5,"#312e81"],[1,"#a78bfa"]],text=[[f"{v:.2f}" for v in row] for row in corr.values],texttemplate="%{text}",showscale=True,zmin=-1,zmax=1))
        fig5.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(13,17,23,.6)",font=dict(color="rgba(255,255,255,.65)",size=10),height=440,margin=dict(l=60,r=20,t=20,b=60))
        st.plotly_chart(fig5,use_container_width=True)
    with t4:
        dc=['user','mean_dwell','mean_flight','typing_speed_wpm','rhythm_consistency','dwell_flight_ratio']
        st.dataframe(df[dc].round(2),use_container_width=True,height=380)


# ══════════════════════════════════════════════════════════════════════════
# PAGE: HOW IT WORKS
# ══════════════════════════════════════════════════════════════════════════
def page_howto():
    st.markdown("<div class='hero' style='padding:1.5rem'><h1 style='font-size:1.9rem'>📖 How It Works</h1></div>", unsafe_allow_html=True)
    t1,t2,t3,t4=st.tabs(["🧬 Concept","📐 Features","🤖 ML Pipeline","📚 References"])
    with t1:
        st.markdown(f"""
### Two-Factor Authentication: Password + Keystroke Dynamics

**Factor 1 — Password (what you know)**
SHA-256 hashed. At login, `SHA256(entered) == stored_hash` must be true.

**Factor 2 — Keystroke Dynamics (who you are)**
JavaScript captures real `keydown`/`keyup` browser events with `performance.now()`.
13 features are computed from actual timing. The ML model compares YOUR timing
against samples you enrolled during registration.

**Why an impostor fails even with your password:**
Their finger movements, natural pauses, and typing speed are different.
The ML model detects this and Layer 2 fails → access denied.

**Target phrase:** `{TARGET}`

### Authentication flow
```
Enter username + password + type phrase
         ↓
Layer 1: SHA256(password) == stored hash?
         ↓ YES                    ↓ NO
Layer 2: ML predict(            DENIED
  real_features, claimed)
  confidence >= 45%?
  AND predicted == claimed?
         ↓ YES       ↓ NO
      GRANTED      DENIED
```
""")
    with t2:
        st.markdown("""
### 13 Features from Real Keystroke Events

| Feature | What it measures |
|---|---|
| `mean_dwell` | Average key hold time (ms) |
| `std_dwell` | Consistency of hold times |
| `median_dwell` | Robust median hold |
| `max_dwell` | Longest single hold |
| `mean_flight` | Average gap between keys (ms) — strongest signal |
| `std_flight` | Consistency of gaps |
| `median_flight` | Robust median gap |
| `min_flight` | Fastest transition |
| `typing_speed_wpm` | Words per minute |
| `dwell_flight_ratio` | Hold/gap ratio — unique per person |
| `rhythm_consistency` | 1/(1+std_flight/mean_flight) |
| `total_time_ms` | Total phrase time |
| `n_keys` | Keystrokes captured |
""")
    with t3:
        st.markdown("""
### ML Pipeline
```
Real keydown/keyup events → 13 features
        ↓
StandardScaler (fit on train only)
        ↓
RandomForest(100 trees) + SVM(RBF, C=10)
        ↓
0.6×RF + 0.4×SVM weighted ensemble
        ↓
argmax probability → predicted user
confidence≥45% AND predicted==claimed → GRANTED
```
""")
    with t4:
        st.markdown("""
### References
1. Monrose & Rubin (2000) — *Keystroke Dynamics as a Biometric*
2. Killourhy & Maxion (2009) — *CMU Keystroke Benchmark*
3. Breiman (2001) — *Random Forests*
4. Cortes & Vapnik (1995) — *Support Vector Networks*

---
*IIIT Raichur · AD23B1021*
""")


# ══════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════
PAGE_MAP={
    "home":page_home,"register":page_register,"train":page_train,
    "authenticate":page_authenticate,"attack":page_attack,
    "dashboard":page_dashboard,"howto":page_howto,
}
PAGE_MAP.get(st.session_state.page,page_home)()
