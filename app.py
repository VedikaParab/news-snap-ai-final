import os
import json
import datetime
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from newspaper import Article
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from prompts import SUPPORTED_LANGUAGES, ENUM_FIELDS_NOTE, lang_instruction
import textwrap
import io
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

load_dotenv()
groq_api_key   = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

st.set_page_config(page_title="NewsSnap AI", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink:#0d0d0f;--ink-2:#3a3a44;--ink-3:#7a7a88;
    --paper:#fafaf8;--paper-2:#f2f2ee;--paper-3:#e8e8e2;
    --accent:#c8392b;--accent-2:#e8b84b;
    --positive:#1a7a4a;--negative:#c8392b;--neutral:#3a6ea8;
    --card-bg:#ffffff;--border:#e0e0d8;
    --shadow:0 2px 20px rgba(0,0,0,0.07);--shadow-lg:0 8px 40px rgba(0,0,0,0.12);
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{max-width:98vw!important;padding:0 2.5rem 4rem!important;}
section[data-testid="stSidebar"]{display:none!important;}

body::before{content:'';position:fixed;inset:0;background-color:#fafaf8;background-image:radial-gradient(circle,#c8c8c0 1px,transparent 1px);background-size:22px 22px;z-index:-2;pointer-events:none;}
body::after{content:'';position:fixed;inset:0;background:linear-gradient(180deg,rgba(250,250,248,0) 0%,rgba(250,250,248,0.4) 40%,rgba(250,250,248,0.85) 100%);z-index:-1;pointer-events:none;}

@keyframes ticker-scroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ticker-wrap{background:var(--ink);overflow:hidden;white-space:nowrap;padding:5px 0;border-bottom:2px solid var(--accent);}
.ticker-inner{display:inline-block;animation:ticker-scroll 38s linear infinite;}
.ticker-item{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:0.67rem;color:rgba(255,255,255,0.75);padding:0 2.5rem;letter-spacing:0.06em;}
.ticker-item strong{color:var(--accent-2);font-weight:500;}
.ticker-sep{color:var(--accent);opacity:0.6;}

.masthead{border-bottom:3px solid var(--ink);padding:1.6rem 0 1.2rem;margin-bottom:2.5rem;display:flex;align-items:baseline;justify-content:space-between;gap:1rem;}
.masthead-left{display:flex;align-items:baseline;gap:1rem;}
.masthead-logo{font-family:'Playfair Display',serif;font-size:2.8rem;font-weight:900;color:var(--ink);line-height:1;letter-spacing:-1.5px;}
.masthead-logo span{color:var(--accent);}
.masthead-tagline{font-size:0.72rem;color:var(--ink-3);font-weight:400;letter-spacing:0.08em;text-transform:uppercase;border-left:1px solid var(--border);padding-left:1rem;line-height:1.5;}
.masthead-date{font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:var(--ink-3);text-align:right;line-height:1.8;}
.masthead-date strong{color:var(--ink);font-weight:500;}

@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.reveal-1{animation:fadeUp 0.5s ease both 0.05s;}
.reveal-2{animation:fadeUp 0.5s ease both 0.15s;}
.reveal-3{animation:fadeUp 0.5s ease both 0.25s;}
.reveal-4{animation:fadeUp 0.5s ease both 0.35s;}
.reveal-5{animation:fadeUp 0.5s ease both 0.45s;}
.reveal-6{animation:fadeUp 0.5s ease both 0.55s;}

.input-zone{background:var(--card-bg);border:1.5px solid var(--border);border-radius:4px;padding:1.2rem 1.8rem 0.5rem;margin-bottom:1rem;box-shadow:var(--shadow);}
.input-label{font-size:0.72rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink-3);margin-bottom:0.3rem;}
.stTextInput>div>div>input{font-family:'JetBrains Mono',monospace!important;font-size:0.82rem!important;background:var(--paper-2)!important;border:1.5px solid var(--border)!important;border-radius:3px!important;color:var(--ink)!important;padding:0.6rem 1rem!important;}
.stTextInput>div>div>input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 3px rgba(200,57,43,0.1)!important;}
.stButton>button{font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:0.82rem!important;letter-spacing:0.06em!important;text-transform:uppercase!important;border-radius:3px!important;transition:all 0.15s ease!important;}
.stButton:first-child>button{background:var(--ink)!important;color:white!important;border:2px solid var(--ink)!important;}
.stButton:first-child>button:hover{background:var(--accent)!important;border-color:var(--accent)!important;}
.stButton:last-child>button{background:transparent!important;color:var(--ink-2)!important;border:2px solid var(--border)!important;}

.section-header{display:flex;align-items:center;gap:0.6rem;margin:2.2rem 0 1rem;}
.section-header-rule{flex:1;height:1px;background:var(--border);}
.section-title{font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--ink);letter-spacing:-0.3px;}
.section-kicker{font-size:0.68rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--accent);background:rgba(200,57,43,0.07);padding:2px 8px;border-radius:2px;}

.context-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1rem;}
.context-card{background:var(--card-bg);border:1.5px solid var(--border);border-top:3px solid var(--accent);border-radius:4px;padding:1.2rem 1.4rem;box-shadow:var(--shadow);}
.context-card-number{font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:var(--accent);font-weight:500;margin-bottom:0.5rem;letter-spacing:0.06em;}
.context-card-term{font-family:'Playfair Display',serif;font-size:1.15rem;color:var(--ink);margin-bottom:0.4rem;line-height:1.2;}
.context-card-oneliner{font-size:0.8rem;font-weight:600;color:var(--ink-2);margin-bottom:0.6rem;line-height:1.4;padding-bottom:0.6rem;border-bottom:1px solid var(--border);}
.context-card-body{font-size:0.8rem;color:var(--ink-3);line-height:1.65;}

.summary-block{background:var(--ink);color:white;padding:1.8rem 2rem;border-radius:4px;margin-bottom:1rem;position:relative;overflow:hidden;width:100%;box-sizing:border-box;display:block;}
[data-testid="stMarkdownContainer"]:has(.summary-block){width:100%!important;}
.summary-block::before{content:'\201C';position:absolute;top:-0.5rem;left:1.2rem;font-family:'Playfair Display',serif;font-size:7rem;color:rgba(255,255,255,0.07);line-height:1;pointer-events:none;}
.summary-block p{font-family:'Playfair Display',serif;font-size:1.15rem;line-height:1.75;color:rgba(255,255,255,0.92);margin:0;position:relative;z-index:1;}

.meta-chip{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:0.72rem;padding:3px 10px;border-radius:2px;border:1px solid var(--border);color:var(--ink-3);background:var(--paper-2);}
.meta-chip.positive{color:var(--positive);border-color:rgba(26,122,74,0.3);background:rgba(26,122,74,0.06);}
.meta-chip.negative{color:var(--negative);border-color:rgba(200,57,43,0.3);background:rgba(200,57,43,0.06);}
.meta-chip.neutral{color:var(--neutral);border-color:rgba(58,110,168,0.3);background:rgba(58,110,168,0.06);}

.bullets-list{list-style:none;padding:0;margin:0;}
.bullet-item{display:flex;gap:0.8rem;padding:0.8rem 0;border-bottom:1px solid var(--border);align-items:flex-start;font-size:0.9rem;line-height:1.6;color:var(--ink-2);}
.bullet-item:last-child{border-bottom:none;}
.bullet-num{font-family:'JetBrains Mono',monospace;font-size:0.65rem;font-weight:500;color:var(--accent);background:rgba(200,57,43,0.08);padding:2px 6px;border-radius:2px;flex-shrink:0;margin-top:3px;}

.question-item{background:var(--card-bg);border:1.5px solid var(--border);border-left:3px solid var(--accent-2);border-radius:3px;padding:1rem 1.2rem;margin-bottom:0.7rem;font-size:0.88rem;color:var(--ink-2);line-height:1.6;}
.question-num{font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--accent-2);font-weight:600;letter-spacing:0.06em;margin-bottom:0.3rem;}

.stats-bar{display:flex;background:var(--card-bg);border-radius:4px;border:1.5px solid var(--border);margin-bottom:1.5rem;overflow:hidden;box-shadow:var(--shadow);}
.stat-item{text-align:center;padding:0.9rem 1.4rem;flex:1;}
.stat-val{font-family:'Playfair Display',serif;font-size:1.3rem;color:var(--ink);display:block;line-height:1;}
.stat-lbl{font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--ink-3);font-weight:600;}
.stat-divider{width:1px;background:var(--border);margin:0.6rem 0;}

.entities-strip{display:flex;gap:0.55rem;flex-wrap:wrap;margin-bottom:0.5rem;}
.entity-pill{display:flex;align-items:center;gap:0.45rem;background:var(--card-bg);border:1.5px solid var(--border);border-radius:999px;padding:0.38rem 0.9rem 0.38rem 0.45rem;box-shadow:var(--shadow);}
.entity-badge{font-family:'JetBrains Mono',monospace;font-size:0.55rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;padding:2px 6px;border-radius:999px;}
.entity-badge.person{color:#7b3fa0;background:rgba(123,63,160,0.1);}
.entity-badge.org{color:#1a7a4a;background:rgba(26,122,74,0.1);}
.entity-badge.place{color:#3a6ea8;background:rgba(58,110,168,0.1);}
.entity-name-pill{font-size:0.83rem;color:var(--ink);font-weight:500;}
.entity-role-pill{font-size:0.74rem;color:var(--ink-3);}

.footer{border-top:2px solid var(--ink);padding-top:1rem;margin-top:3rem;display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;color:var(--ink-3);letter-spacing:0.04em;}

/* language pill — floats in masthead right corner */
.lang-pill-wrap{display:flex;align-items:center;gap:0.5rem;}
.lang-pill-label{font-size:0.68rem;color:var(--ink-3);letter-spacing:0.06em;text-transform:uppercase;}
.stSelectbox>div>div{font-family:'JetBrains Mono',monospace!important;font-size:0.78rem!important;
  background:var(--paper-2)!important;border:1.5px solid var(--border)!important;
  border-radius:3px!important;padding:0.3rem 0.7rem!important;min-height:0!important;}

/* ── Full-width summary fix ── */
/* Streamlit wraps every st.markdown in stMarkdownContainer which can inherit
   narrow widths from parent flex/column layouts. Force the summary to always
   fill the full block container. */
.summary-block,.summary-fullwidth-wrap{
    width:100%!important;
    min-width:0!important;
    box-sizing:border-box!important;
    display:block!important;
}
/* The Streamlit element div that wraps the summary markdown */
div[data-testid="stMarkdownContainer"]:has(.summary-block){
    width:100%!important;
    min-width:0!important;
    display:block!important;
}
div[data-testid="element-container"]:has(.summary-block){
    width:100%!important;
    min-width:0!important;
    display:block!important;
}
/* Ensure paragraph text fills the dark block */
.summary-block p{
    width:100%!important;
    max-width:100%!important;
    white-space:normal!important;
    word-wrap:break-word!important;
    overflow-wrap:break-word!important;
}

/* ── Footer URL fix ── */
.footer{border-top:2px solid var(--ink)!important;padding-top:1rem!important;
  margin-top:3rem!important;display:flex!important;flex-direction:column!important;gap:0.5rem!important;
  font-size:0.72rem!important;color:var(--ink-3)!important;letter-spacing:0.04em!important;}
.footer-url{word-break:break-all!important;color:var(--accent)!important;}

/* ── Input row: align language dropdown with URL input card ── */
/* Kill the default top padding Streamlit adds to selectbox columns */
div[data-testid="column"]:last-child > div:first-child {
  padding-top: 0 !important;
}
div[data-testid="column"]:last-child .stSelectbox > div > div {
  margin-top: 0.35rem !important;
  background: var(--card-bg) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 4px !important;
  box-shadow: var(--shadow) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.85rem !important;
  min-height: 3.2rem !important;
  padding: 0.6rem 1rem !important;
}

/* ── Kill extra space below summary iframe ── */
iframe:not([title="components.html"]) {
    margin-bottom: 0 !important;
    display: block !important;
}
div[data-testid="element-container"]:has(iframe:not([title="components.html"])) {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}

/* ── Export panel ── */
.export-panel{background:var(--card-bg);border:1.5px solid var(--border);border-radius:4px;
  padding:1.4rem 1.8rem 0.6rem;margin-bottom:1rem;box-shadow:var(--shadow);}
.export-panel-row{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;}
.export-item{display:flex;align-items:flex-start;gap:1rem;}
.export-icon{font-size:1.6rem;line-height:1;padding-top:2px;flex-shrink:0;}
.export-meta{display:flex;flex-direction:column;gap:0.25rem;}
.export-title{font-family:"Playfair Display",serif;font-size:1.05rem;color:var(--ink);font-weight:700;}
.export-desc{font-size:0.76rem;color:var(--ink-3);line-height:1.5;}
</style>
""", unsafe_allow_html=True)

# ── TICKER + MASTHEAD ──
now = datetime.datetime.now()
TICKER = [
    ("⚡", "Paste any news URL — get AI analysis in seconds"),
    ("📰", "Auto-extracts articles via Newspaper3k + BeautifulSoup"),
    ("🧠", "Summaries · Key Points · Timeline · Entities · Context Cards"),
    ("🌐", "12 languages supported — Hindi, Tamil, Arabic, Japanese & more"),
    ("💬", "Research Chatbot powered by live Tavily web search"),
    ("📊", "Sentiment · Category · Reading complexity — auto-detected"),
    ("🖼",  "Shareable PNG cards — one click, ready to post"),
    ("⬇",  "Export full editorial reports as .txt"),
    ("🔥", "Powered by Groq LLaMA 3.1 · Tavily · Streamlit"),
]
ticker_html = '<div class="ticker-wrap"><div class="ticker-inner">' + (
    "".join(f'<span class="ticker-item"><strong>{k}</strong> &nbsp;{v}&nbsp;<span class="ticker-sep"> /// </span></span>'
            for k, v in TICKER) * 4
) + '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)
st.markdown(f"""
<div class="masthead">
  <div class="masthead-left">
    <div class="masthead-logo">News<span>Snap</span>&thinsp;AI</div>
    <div class="masthead-tagline">AI-powered editorial analysis<br>Paste · Read · Understand · Explore</div>
  </div>
  <div class="masthead-date"><strong>{now.strftime('%A, %d %B %Y')}</strong><br>{now.strftime('%H:%M')}</div>
</div>""", unsafe_allow_html=True)

if not groq_api_key:
    st.error("GROQ_API_KEY not found in .env"); st.stop()

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=groq_api_key, temperature=0.2, timeout=60, max_retries=3)

# ── INPUT ROW: URL input + language selector side by side ──
_url_col, _lang_col = st.columns([5, 1])
with _lang_col:
    lang_display = st.selectbox(
        label="language",
        label_visibility="collapsed",
        options=list(SUPPORTED_LANGUAGES.keys()),
        index=0,
        key="selected_language",
        help="Output language for the analysis",
    )

# Resolve to (BCP-47 code, native name)
lang_code, lang_name = SUPPORTED_LANGUAGES[lang_display]

# RTL languages — inject CSS so text renders correctly
RTL_LANGS = {"ar", "he", "fa", "ur"}
if lang_code in RTL_LANGS:
    st.markdown(
        '<style>[data-testid="stMarkdownContainer"] p,'
        '[data-testid="stMarkdownContainer"] li {direction:rtl;text-align:right;}</style>',
        unsafe_allow_html=True,
    )

# ── HELPERS ──
def safe_json(raw):
    """
    Robustly parse JSON from an LLM response.
    Handles: plain JSON, ```json...```, ```...```, prose before/after the JSON,
    and non-English preamble the model sometimes prepends in multilingual mode.
    Raises json.JSONDecodeError with context if all strategies fail.
    """
    import re
    text = raw.strip()

    # Strategy 1 — response is already clean JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2 — strip ```json ... ``` or ``` ... ``` fence
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        try:
            return json.loads(fence.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3 — find the first {...} object in the string
    m = re.search(r"(\{[\s\S]*\})", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 4 — find the first [...] array in the string
    m = re.search(r"(\[[\s\S]*\])", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 5 — partial recovery: LLM truncated mid-array, salvage complete objects
    # Find all complete {...} objects inside what looks like an array
    objects = re.findall(r'\{[^{}]*\}', text)
    recovered = []
    for obj in objects:
        try:
            recovered.append(json.loads(obj))
        except json.JSONDecodeError:
            pass
    if recovered:
        return recovered

    # All strategies failed — raise so the except blocks in callers can log it
    raise json.JSONDecodeError(
        f"safe_json: could not parse — raw[:{min(200,len(text))}]: {text[:200]}", text, 0
    )

def reading_time(t): return max(1, round(len(t.split()) / 200))
def word_count(t):   return len(t.split())
def get_domain(url):
    try:    return urlparse(url).netloc.replace("www.", "")
    except: return "unknown"

# ── EXTRACTION ──
@st.cache_data(show_spinner=False)
def extract_article(url):
    try:
        a = Article(url); a.download(); a.parse()
        if a.text and len(a.text) > 200: return a.text, None
    except: pass
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = " ".join(p.get_text() for p in soup.find_all("p"))
        if len(text) > 200: return text, None
        return None, "No readable content found."
    except requests.exceptions.HTTPError as e: return None, f"HTTP {e.response.status_code}"
    except requests.exceptions.Timeout:        return None, "Request timed out."
    except Exception as e:                     return None, str(e)

# ── LLM CALLS ──
@st.cache_data(show_spinner=False)
def analyze_article(text, lang_code="en", lang_name="English"):
    lang_dir = lang_instruction(lang_code, lang_name)
    enum_note = ENUM_FIELDS_NOTE.format(lang_name=lang_name)
    r = llm.invoke(
        f"""{lang_dir}Analyze this news article. Return ONLY valid JSON, no markdown.
{enum_note}
Keys: "summary"(2-3 sentences),"bullets"(5 strings),"sentiment"("Positive"|"Negative"|"Neutral"),
"category"("Politics"|"Business"|"Technology"|"Science"|"Sports"|"Health"|"World"|"Environment"|"Crime"|"Culture"),
"reading_complexity"("Easy"|"Moderate"|"Complex")
Article:{text[:8000]}"""
    )
    result = safe_json(r.content)
    # If LLM returned a list instead of a dict, try the first dict element
    if isinstance(result, list):
        result = next((x for x in result if isinstance(x, dict)), {})
    if not isinstance(result, dict):
        result = {}
    # Ensure bullets is always a list of strings
    bullets = result.get("bullets", [])
    if not isinstance(bullets, list):
        bullets = []
    result["bullets"] = [str(b) for b in bullets if b]
    return result

@st.cache_data(show_spinner=False)
def generate_context_cards(text, lang_code="en", lang_name="English"):
    lang_dir = lang_instruction(lang_code, lang_name)
    r = llm.invoke(
        f"""{lang_dir}Identify exactly 3 key concepts needed to understand this article.
IMPORTANT: Return ONLY a raw JSON array. No preamble, no markdown fences.
Start with [ and end with ]. Be CONCISE — keep explanations SHORT (max 1 sentence).
Each object (keys in English, values in {lang_name}):
{{"term":str,"one_liner":str(under 10 words),"explanation":str(1 sentence only, max 20 words)}}
Article:{text[:3000]}"""
    )
    result = safe_json(r.content)
    # Unwrap if LLM returned a dict wrapping the array
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                result = v
                break
        else:
            return []
    # Flatten nested arrays e.g. [[{...}]] → [{...}]
    if isinstance(result, list) and result and isinstance(result[0], list):
        result = [item for sublist in result for item in sublist]
    # Keep only valid dicts with a "term" key
    return [c for c in result if isinstance(c, dict) and "term" in c][:3]

@st.cache_data(show_spinner=False)
def generate_timeline(text, lang_code="en", lang_name="English"):
    lang_dir = lang_instruction(lang_code, lang_name)
    r = llm.invoke(
        f"""{lang_dir}You are extracting a chronological timeline from a news article.
TASK: Find ALL dates, times, years, or time references mentioned in the article and pair each with what happened at that time.
- The "when" field must contain the date/time exactly as written in the article (you may translate surrounding words to {lang_name} but keep numbers/years as-is).
- The "event" field must be written in {lang_name}, max 20 words.
- Return 3 to 6 items. If the article has fewer than 3 explicit dates, infer approximate timeframes from context (e.g. "Earlier this year", "Last month").
- NEVER return an empty array []. Always extract at least 2 items even from sparse articles.
- Return ONLY a valid JSON array. No markdown, no explanation.
Format: [{{"when":str,"event":str}}]
Article:{text[:6000]}"""
    )
    result = safe_json(r.content)
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                result = v
                break
        else:
            return []
    if isinstance(result, list) and result and isinstance(result[0], list):
        result = [item for sublist in result for item in sublist]
    return [e for e in result if isinstance(e, dict) and "when" in e and "event" in e]

@st.cache_data(show_spinner=False)
def extract_entities(text, lang_code="en", lang_name="English"):
    lang_dir = lang_instruction(lang_code, lang_name)
    r = llm.invoke(
        f"""{lang_dir}Extract the TOP 5 most important named entities from this article.
IMPORTANT: Return ONLY a raw JSON array — no preamble, no explanation, no markdown fences.
Start your response with [ and end with ].
Keep "name" as written in the article. Write "role" in {lang_name} (under 10 words).
Each object MUST be: {{"name":str,"type":"person"|"org"|"place","role":str}}
Article:{text[:6000]}"""
    )
    result = safe_json(r.content)
    # Unwrap if LLM returned a dict with a key containing the list
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                result = v
                break
        else:
            return []
    # Flatten nested arrays e.g. [[{...}]] → [{...}]
    if isinstance(result, list) and result and isinstance(result[0], list):
        result = [item for sublist in result for item in sublist]
    # Keep only valid dicts with required keys
    valid = [e for e in result if isinstance(e, dict) and "name" in e and "type" in e]
    return valid[:5]

@st.cache_data(show_spinner=False)
def generate_followup_questions(summary, lang_code="en", lang_name="English"):
    lang_dir = lang_instruction(lang_code, lang_name)
    r = llm.invoke(
        f"""{lang_dir}Generate exactly 3 thought-provoking follow-up questions for a curious reader.
Write the questions in {lang_name}.
Format: numbered list (1. 2. 3.) only — no preamble, no extra text.
Summary:{summary}"""
    )
    qs = []
    for line in r.content.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            qs.append(line.split(".", 1)[1].strip())
    return qs[:3]

# ── TAVILY SEARCH ──
def tavily_search(query, max_results=4):
    if not tavily_api_key: return [], ""
    try:
        resp = requests.post("https://api.tavily.com/search", json={
            "api_key": tavily_api_key, "query": query,
            "search_depth": "basic", "max_results": max_results,
            "include_answer": True, "include_raw_content": False,
        }, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", []), data.get("answer", "")
    except: return [], ""

def chat_with_search(question, article_text, article_summary, chat_history,
                     lang_code="en", lang_name="English"):
    search_results, tavily_answer = tavily_search(f"{question} {article_summary[:120]}")
    search_ctx = ""
    sources = []
    if tavily_answer: search_ctx += f"Web summary: {tavily_answer}\n\n"
    for r in search_results:
        search_ctx += f"[{r.get('url','')}]\n{r.get('title','')}\n{r.get('content','')[:350]}\n\n"
        sources.append({"title": r.get("title", ""), "url": r.get("url", "")})

    history_str = "\n".join([
        f"{'User' if m['role']=='user' else 'Assistant'}: {m['content']}"
        for m in chat_history[-6:]
    ])
    lang_dir = lang_instruction(lang_code, lang_name)
    prompt = f"""{lang_dir}You are a sharp news analyst. Answer using BOTH the article AND web search results.
Be direct, concise (3-5 sentences). Cite sources naturally. Highlight new info from web beyond article.
{'Respond entirely in ' + lang_name + '.' if lang_code != 'en' else ''}

ARTICLE:{article_text[:3500]}

WEB SEARCH:{search_ctx}

HISTORY:{history_str}

Question: {question}
Answer:"""
    return llm.invoke(prompt).content, sources


def _pixel_wrap(draw, text, font, max_width):
    """Wrap text by actual rendered pixel width — never by char count."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


# Per-language font paths — DejaVu for Latin, FreeSans for Indic,
# Unifont for Telugu/Arabic, NotoSansCJK for East Asian scripts
_LANG_FONT_MAP = {
    "en": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "hi": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "ta": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "bn": "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "te": "/usr/share/fonts/opentype/unifont/unifont.otf",
    "ar": "/usr/share/fonts/opentype/unifont/unifont.otf",
    "ja": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "zh": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "ko": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "pt": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "es": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "fr": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "de": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}
_LANG_SERIF_MAP = {
    "ja": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "zh": "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
}

def generate_share_card(summary, domain, category, sentiment, url,
                         bullets=None, complexity="", rt=1, wc=0,
                         entities=None, lang_name="English", cards=None,
                         lang_code="en"):
    """Generate a rich shareable PNG with all article info."""
    W = 1200
    bullets  = bullets  or []
    entities = entities or []
    cards    = cards    or []

    INK    = (13,  13,  15)
    PAPER  = (250, 250, 248)
    ACCENT = (200, 57,  43)
    INK2   = (58,  58,  68)
    INK3   = (122, 122, 136)
    BORDER = (224, 224, 216)
    WHITE  = (255, 255, 255)
    SENT_COLORS = {
        "positive": (26,  122, 74),
        "negative": (200, 57,  43),
        "neutral":  (58,  110, 168),
    }

    PAD   = 54
    INNER = W - PAD * 2

    try:
        F = "/usr/share/fonts/truetype/dejavu/"
        # Logo/kicker always use DejaVu (English only, always Latin)
        f_logo  = ImageFont.truetype(F+"DejaVuSerif-Bold.ttf",   44)
        f_mono  = ImageFont.truetype(F+"DejaVuSansMono.ttf",     14)
        f_kick  = ImageFont.truetype(F+"DejaVuSansMono-Bold.ttf",13)
        # Body/small use language-aware font so non-Latin scripts render correctly
        _body_fp  = _LANG_FONT_MAP.get(lang_code, F+"DejaVuSans.ttf")
        f_body  = ImageFont.truetype(_body_fp, 22)
        f_small = ImageFont.truetype(_body_fp, 17)
    except Exception:
        f_logo = f_body = f_small = f_mono = f_kick = ImageFont.load_default()

    # Pixel-accurate wrap: usable width = 1200 - 54*2(PAD) - 20*2(inner pad) = 1052px
    _tmp_img  = Image.new("RGB", (W, 10))
    _tmp_draw = ImageDraw.Draw(_tmp_img)
    SUM_INNER_W  = W - PAD*2 - 40   # 40 = 20px left + 20px right padding inside dark block
    BULLET_MAX_W = INNER - 60        # badge width ~40px + gap 10px + margin
    CARD_TEXT_W  = (INNER - 20) // 3 - 20  # card inner usable width
    sum_lines    = _pixel_wrap(_tmp_draw, summary, f_body, SUM_INNER_W)
    # Use pixel-wrap for bullets so non-Latin scripts aren't over-truncated
    bullet_rows  = [_pixel_wrap(_tmp_draw, str(b), f_small, BULLET_MAX_W)[0]
                    for b in bullets[:4]]
    card_rows    = []
    for c in cards[:3]:
        if isinstance(c, dict) and "term" in c:
            # Use pixel-wrap for one_liner and explanation to handle non-Latin
            exp_raw = c.get("explanation", "")
            card_rows.append((c.get("term", ""), c.get("one_liner", ""), exp_raw))

    H_HEADER  = 110
    H_STATS   = 68
    H_GAP     = 16
    H_SUM_HDR = 26
    # Indic/Arabic/CJK scripts need taller line height than Latin
    _line_h   = 42 if lang_code in {'hi','ta','bn','te','ar'} else 36 if lang_code in {'ja','zh','ko'} else 32
    H_SUM_BLK = len(sum_lines)*_line_h + 36  # 36 = top+bottom padding inside dark block
    H_KP_HDR  = 26
    H_KP      = len(bullet_rows)*(_line_h - 2) + 10
    H_ENT     = 58 if entities else 0
    H_CTX     = (80 + 30) if card_rows else 0
    H_FOOT    = 70  # extra space for full URL potentially wrapping 2 lines

    TOTAL_H = (H_HEADER + H_STATS + H_GAP*2 +
               H_SUM_HDR + H_SUM_BLK + H_GAP +
               H_KP_HDR + H_KP + H_GAP +
               H_ENT + H_CTX + H_FOOT + 30)

    img  = Image.new("RGB", (W, TOTAL_H), PAPER)
    draw = ImageDraw.Draw(img)

    for x in range(0, W, 22):
        for yy in range(0, TOTAL_H, 22):
            draw.ellipse([x-1, yy-1, x+1, yy+1], fill=(200, 200, 192))

    draw.rectangle([0, 0, W, 8], fill=ACCENT)

    # LOGO
    draw.text((PAD, 16), "News", font=f_logo, fill=INK)
    nw = int(draw.textlength("News", font=f_logo))
    draw.text((PAD+nw, 16), "Snap", font=f_logo, fill=ACCENT)
    sw = int(draw.textlength("Snap", font=f_logo))
    draw.text((PAD+nw+sw, 16), " AI", font=f_logo, fill=INK)
    draw.text((PAD, 72), "AI-POWERED EDITORIAL ANALYSIS  ·  PASTE · READ · UNDERSTAND · EXPLORE",
              font=f_mono, fill=INK3)
    draw.rectangle([PAD, 98, W-PAD, 100], fill=INK)

    y = 108

    # STATS BAR
    bh = 62
    draw.rectangle([PAD, y, W-PAD, y+bh], fill=WHITE)
    draw.rectangle([PAD, y, W-PAD, y+bh], outline=BORDER, width=1)
    stats = [
        (f"{rt}", "MIN READ"),
        (f"{wc:,}", "WORDS"),
        (domain[:24], "SOURCE"),
        (category, "CATEGORY"),
        (complexity, "COMPLEXITY"),
        (sentiment.upper(), "SENTIMENT"),
    ]
    if lang_name != "English":
        stats.append((lang_name, "LANGUAGE"))
    ncols = len(stats)
    col_w = INNER // ncols
    for i, (val, lbl) in enumerate(stats):
        cx = PAD + i*col_w + col_w//2
        if i > 0:
            draw.rectangle([PAD+i*col_w, y+8, PAD+i*col_w+1, y+bh-8], fill=BORDER)
        color = SENT_COLORS.get(sentiment.lower(), INK3) if lbl == "SENTIMENT" else INK
        vw = int(draw.textlength(val, font=f_small))
        draw.text((cx-vw//2, y+8), val, font=f_small, fill=color)
        lw = int(draw.textlength(lbl, font=f_mono))
        draw.text((cx-lw//2, y+34), lbl, font=f_mono, fill=INK3)
    y += bh + H_GAP

    # SUMMARY
    draw.rectangle([PAD, y, PAD+70, y+20], fill=ACCENT)
    draw.text((PAD+5, y+3), "TL;DR", font=f_kick, fill=PAPER)
    draw.text((PAD+82, y+3), "Summary", font=f_kick, fill=INK3)
    y += H_SUM_HDR
    draw.rectangle([PAD, y, W-PAD, y+H_SUM_BLK], fill=INK)
    ty = y + 18
    for line in sum_lines:
        draw.text((PAD+20, ty), line, font=f_body, fill=(240, 240, 238))
        ty += _line_h
    y += H_SUM_BLK + H_GAP

    # KEY POINTS
    draw.text((PAD, y), "KEY POINTS", font=f_kick, fill=ACCENT)
    draw.rectangle([PAD+100, y+7, W-PAD, y+8], fill=BORDER)
    y += H_KP_HDR
    for i, b_short in enumerate(bullet_rows, 1):
        badge = f"0{i}"
        bw = int(draw.textlength(badge, font=f_kick)) + 14
        draw.rectangle([PAD, y+1, PAD+bw, y+21], fill=(240, 230, 228))
        draw.text((PAD+4, y+3), badge, font=f_kick, fill=ACCENT)
        draw.text((PAD+bw+10, y+3), b_short, font=f_small, fill=INK2)
        y += _line_h - 2
    y += H_GAP

    # KEY ENTITIES
    # Use f_small (language-aware) for entity names so non-Latin scripts render correctly.
    if entities:
        draw.text((PAD, y), "KEY ENTITIES", font=f_kick, fill=ACCENT)
        draw.rectangle([PAD+112, y+7, W-PAD, y+8], fill=BORDER)
        y += 24
        ex = PAD
        for e in entities[:6]:
            if not isinstance(e, dict): continue
            etype = e.get("type", "").upper()
            name  = e.get("name", "")
            tc = {"PERSON":(123,63,160),"ORG":(26,122,74),"PLACE":(58,110,168)}.get(etype, INK3)
            badge_txt = f" {etype} · "
            bw_badge = int(draw.textlength(badge_txt, font=f_mono))
            nw_name  = int(draw.textlength(name + " ", font=f_small))
            pw = bw_badge + nw_name + 12
            if ex + pw > W - PAD - 40:
                break
            draw.rectangle([ex, y, ex+pw, y+26], fill=BORDER)
            draw.text((ex+4, y+6), badge_txt, font=f_mono, fill=tc)
            draw.text((ex+4+bw_badge, y+5), name, font=f_small, fill=tc)
            ex += pw + 10
        y += 34 + H_GAP

    # BACKGROUND CONTEXT CARDS
    if card_rows:
        draw.text((PAD, y), "BACKGROUND CONTEXT", font=f_kick, fill=ACCENT)
        draw.rectangle([PAD+168, y+7, W-PAD, y+8], fill=BORDER)
        y += 24
        card_w = (INNER - 20) // 3
        _card_inner_w = card_w - 20  # usable text width inside each card
        # Pre-compute wrapped lines using pixel-accurate wrap for each card
        card_wrapped = []
        for term, one_liner, exp in card_rows:
            # Wrap term in f_kick (always ASCII/Latin OK), one_liner and exp in f_small (language-aware)
            term_lines    = _pixel_wrap(_tmp_draw, term,      f_small,  _card_inner_w)
            liner_lines   = _pixel_wrap(_tmp_draw, one_liner, f_small,  _card_inner_w)
            exp_lines     = _pixel_wrap(_tmp_draw, exp,       f_small,  _card_inner_w)[:3]
            card_wrapped.append((term_lines, liner_lines, exp_lines))
        max_card_h = 0
        for term_lines, liner_lines, exp_lines in card_wrapped:
            h = 14 + len(term_lines)*20 + 8 + len(liner_lines)*18 + 8 + len(exp_lines)*18 + 14
            max_card_h = max(max_card_h, h)
        for i, ((term_lines, liner_lines, exp_lines), (term, one_liner, exp)) in enumerate(
                zip(card_wrapped, card_rows)):
            cx = PAD + i*(card_w+10)
            draw.rectangle([cx, y, cx+card_w, y+max_card_h], fill=WHITE)
            draw.rectangle([cx, y, cx+card_w, y+max_card_h], outline=BORDER, width=1)
            draw.rectangle([cx, y, cx+card_w, y+3], fill=ACCENT)
            cy = y + 10
            draw.text((cx+8, cy), f"CONCEPT {i+1:02d}", font=f_mono, fill=ACCENT)
            cy += 18
            for tl in term_lines:
                draw.text((cx+8, cy), tl, font=f_small, fill=INK)
                cy += 20
            for ll in liner_lines:
                draw.text((cx+8, cy), ll, font=f_small, fill=INK2)
                cy += 18
            draw.rectangle([cx+8, cy, cx+card_w-8, cy+1], fill=BORDER)
            cy += 6
            for el in exp_lines:
                draw.text((cx+8, cy), el, font=f_small, fill=INK3)
                cy += 18
        y += max_card_h + H_GAP

    # FOOTER — show FULL URL wrapped across lines if needed
    draw.rectangle([PAD, y, W-PAD, y+1], fill=BORDER)
    y += 8
    date_str = datetime.datetime.now().strftime("%d %b %Y · %H:%M")
    dw = int(draw.textlength(date_str, font=f_mono))
    draw.text((W-PAD-dw, y), date_str, font=f_mono, fill=INK3)
    # Wrap full URL to fit within available width (INNER minus date width minus gap)
    url_max_w = INNER - dw - 30
    url_lines = _pixel_wrap(draw, url, f_mono, url_max_w) or [url]
    url_y = y
    for ul in url_lines:
        draw.text((PAD, url_y), ul, font=f_mono, fill=ACCENT)
        url_y += 18
    y += max(26, len(url_lines) * 18)

    final_h = y + 12
    img = img.crop((0, 0, W, final_h))
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([0, final_h-8, W, final_h], fill=ACCENT)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def build_report(url, domain, result, entities, timeline, text):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = ["="*70,"  NEWSSNAP AI — EDITORIAL ANALYSIS REPORT",f"  Generated: {now_str}","="*70,"",
             f"SOURCE:  {url}",f"DOMAIN:  {domain}",
             f"WORDS:   {word_count(text):,}   |   READ TIME: {reading_time(text)} min",
             f"CATEGORY:{result.get('category','—')}  SENTIMENT:{result.get('sentiment','—')}  COMPLEXITY:{result.get('reading_complexity','—')}",
             "","─"*70,"SUMMARY","─"*70,result.get("summary",""),"","─"*70,"KEY POINTS","─"*70]
    for i, b in enumerate(result.get("bullets", []), 1): lines.append(f"  {i}. {b}")
    lines += ["","─"*70,"TIMELINE","─"*70]
    for evt in (timeline or []): lines.append(f"  [{evt.get('when','')}]  {evt.get('event','')}")
    if not timeline: lines.append("  No clear timeline detected.")
    lines += ["","─"*70,"KEY ENTITIES","─"*70]
    for e in (entities or []): lines.append(f"  [{e.get('type','').upper()}]  {e.get('name','')}  —  {e.get('role','')}")
    lines += ["","="*70,"  Powered by Groq · LLaMA 3.1 · Tavily · NewsSnap AI","="*70]
    return "\n".join(lines)

# ── INPUT ──
with _url_col:
    st.markdown('<div class="reveal-1"><div class="input-zone"><div class="input-label">Paste a news article URL to analyse</div>', unsafe_allow_html=True)
    url = st.text_input(label="url", label_visibility="collapsed", placeholder="https://timesofindia.indiatimes.com/...")
    st.markdown('</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1: generate = st.button("⚡  Analyse Article", use_container_width=True)
with col2:
    if st.button("✕  Clear", use_container_width=True):
        for k in ["article_text","result","cards","timeline","entities","domain","rt","wc",
                  "url_analysed","chat_history","lang_code","lang_name"]:
            st.session_state.pop(k, None)
        st.rerun()

# ── ANALYSIS ──
if generate:
    if not url.strip(): st.warning("Please enter a URL."); st.stop()
    with st.spinner("Fetching article…"):
        text, err = extract_article(url)
    if err: st.error(f"**Could not extract article.** {err}"); st.stop()

    st.session_state.update({"article_text": text, "url_analysed": url, "chat_history": [],
                              "lang_code": lang_code, "lang_name": lang_name})

    with st.spinner("Running AI analysis…"):
        try: result = analyze_article(text, lang_code, lang_name)
        except Exception as e: st.error(f"Analysis failed: {e}"); st.stop()

    with st.spinner("Building context cards…"):
        try:
            cards = generate_context_cards(text, lang_code, lang_name)
        except Exception as e:
            st.warning(f"Context cards unavailable: {e}")
            cards = []

    with st.spinner("Extracting timeline…"):
        try:
            timeline = generate_timeline(text, lang_code, lang_name)
        except Exception as e:
            st.warning(f"Timeline unavailable: {e}")
            timeline = []

    with st.spinner("Extracting key entities…"):
        try:
            entities = extract_entities(text, lang_code, lang_name)
        except Exception as e:
            st.warning(f"Entities unavailable: {e}")
            entities = []

    st.session_state.update({"result": result, "cards": cards, "timeline": timeline, "entities": entities,
                              "domain": get_domain(url), "rt": reading_time(text), "wc": word_count(text)})

# ── RENDER ──
if "result" not in st.session_state: st.stop()

result   = st.session_state["result"]
cards    = st.session_state.get("cards", [])
timeline = st.session_state.get("timeline", [])
entities = st.session_state.get("entities", [])
domain   = st.session_state.get("domain", "")
rt       = st.session_state.get("rt", 1)
wc       = st.session_state.get("wc", 0)
text     = st.session_state.get("article_text", "")
url      = st.session_state.get("url_analysed", "")
# Restore the language that was active when analysis ran — keeps display
# consistent even if the user changes the selector mid-session.
_saved_lang_code = st.session_state.get("lang_code", "en")
_saved_lang_name = st.session_state.get("lang_name", "English")
sent     = result.get("sentiment", "Neutral")
cat      = result.get("category", "—")
complexity = result.get("reading_complexity", "—")
# Native language label for the badge (e.g. "हिंदी", "Español")
_, _lang_native = SUPPORTED_LANGUAGES.get(
    next((k for k, v in SUPPORTED_LANGUAGES.items() if v[0] == _saved_lang_code), "English"),
    ("en", "English"),
)

# STATS BAR — adds language badge when non-English
_lang_badge = (
    f'<div class="stat-divider"></div>'
    f'<div class="stat-item"><span class="stat-val" style="font-size:0.85rem;margin-top:4px">'
    f'{_lang_native}</span><span class="stat-lbl">language</span></div>'
    if _saved_lang_code != "en" else ""
)
st.markdown(f"""<div class="reveal-2"><div class="stats-bar">
  <div class="stat-item"><span class="stat-val">{rt}</span><span class="stat-lbl">min read</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val">{wc:,}</span><span class="stat-lbl">words</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{domain}</span><span class="stat-lbl">source</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{cat}</span><span class="stat-lbl">category</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="stat-val" style="font-size:0.9rem;margin-top:4px">{complexity}</span><span class="stat-lbl">complexity</span></div>
  <div class="stat-divider"></div>
  <div class="stat-item"><span class="meta-chip {sent.lower()}" style="margin-top:6px;display:inline-block">{sent}</span><span class="stat-lbl" style="display:block;margin-top:4px">sentiment</span></div>
  {_lang_badge}
</div></div>""", unsafe_allow_html=True)

# CONTEXT CARDS
if cards:
    st.markdown("""<div class="reveal-3"><div class="section-header"><span class="section-kicker">Before You Read</span><span class="section-title">&nbsp;Background Context</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    ch = '<div class="reveal-3"><div class="context-grid">'
    for i, c in enumerate(cards, 1):
        ch += f'<div class="context-card"><div class="context-card-number">CONCEPT {i:02d}</div><div class="context-card-term">{c.get("term","")}</div><div class="context-card-oneliner">{c.get("one_liner","")}</div><div class="context-card-body">{c.get("explanation","")}</div></div>'
    ch += '</div></div>'
    st.markdown(ch, unsafe_allow_html=True)

# SUMMARY — rendered via components.html so Streamlit cannot constrain its width
st.markdown("""<div class="reveal-3"><div class="section-header"><span class="section-kicker">TL;DR</span><span class="section-title">&nbsp;Summary</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
_summary_text = result.get("summary", "").replace('"', '&quot;').replace("'", "&#39;").replace('<', '&lt;').replace('>', '&gt;')
components.html(f"""<!DOCTYPE html>
<html><head><style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{background:transparent;margin:0;padding:0;}}
  .summary-block{{
    background:#0d0d0f;
    color:white;
    padding:1.8rem 2rem;
    border-radius:4px;
    margin-bottom:0.5rem;
    position:relative;
    overflow:hidden;
    width:100%;
    display:block;
  }}
  .summary-block::before{{
    content:'\201C';
    position:absolute;
    top:-0.5rem;
    left:1.2rem;
    font-family:Georgia,serif;
    font-size:7rem;
    color:rgba(255,255,255,0.07);
    line-height:1;
    pointer-events:none;
  }}
  .summary-block p{{
    font-family:Georgia,'Times New Roman',serif;
    font-size:1.1rem;
    line-height:1.75;
    color:rgba(255,255,255,0.92);
    margin:0;
    position:relative;
    z-index:1;
    width:100%;
    display:block;
    white-space:normal;
    word-wrap:break-word;
    overflow-wrap:break-word;
  }}
</style></head>
<body>
  <div class="summary-block"><p>{_summary_text}</p></div>
</body></html>""", height=max(160, min(400, 80 + len(result.get("summary","")) // 3)), scrolling=False)

# KEY POINTS + TIMELINE
col_l, col_r = st.columns([3, 2])
with col_l:
    st.markdown("""<div class="reveal-4"><div class="section-header"><span class="section-kicker">Key Points</span><span class="section-title">&nbsp;What Happened</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    bh = '<div class="reveal-4"><ul class="bullets-list">'
    for i, b in enumerate(result.get("bullets", []), 1):
        bh += f'<li class="bullet-item"><span class="bullet-num">0{i}</span>{b}</li>'
    bh += '</ul></div>'
    st.markdown(bh, unsafe_allow_html=True)

with col_r:
    st.markdown("""<div class="reveal-4"><div class="section-header"><span class="section-kicker">Chronology</span><span class="section-title">&nbsp;Timeline</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    if timeline:
        th = "<div class='reveal-4'>"
        for i, evt in enumerate(timeline):
            connector = "" if i == len(timeline)-1 else '<div style="width:2px;height:18px;background:var(--border);margin-left:6px;"></div>'
            th += f"""<div style="display:flex;gap:0.8rem;align-items:flex-start">
  <div style="display:flex;flex-direction:column;align-items:center;flex-shrink:0">
    <div style="width:14px;height:14px;border-radius:50%;background:var(--accent);border:2px solid var(--paper);box-shadow:0 0 0 2px var(--accent);flex-shrink:0;margin-top:2px"></div>{connector}
  </div>
  <div style="padding-bottom:0.9rem">
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.66rem;color:var(--accent);font-weight:500;margin-bottom:2px">{evt.get('when','')}</div>
    <div style="font-size:0.83rem;color:var(--ink-2);line-height:1.55">{evt.get('event','')}</div>
  </div>
</div>"""
        th += "</div>"
        st.markdown(th, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:var(--ink-3);font-size:0.83rem">No clear timeline detected.</p>', unsafe_allow_html=True)

# ENTITIES
if entities:
    st.markdown("""<div class="reveal-5"><div class="section-header"><span class="section-kicker">Who & Where</span><span class="section-title">&nbsp;Key Entities</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
    eh = '<div class="reveal-5"><div class="entities-strip">'
    for e in entities[:5]:
        if not isinstance(e, dict):
            continue
        etype = e.get("type", "").lower()
        eh += f'<div class="entity-pill"><span class="entity-badge {etype}">{etype.upper()}</span><span class="entity-name-pill">{e.get("name","")}</span><span class="entity-role-pill">— {e.get("role","")}</span></div>'
    eh += '</div></div>'
    st.markdown(eh, unsafe_allow_html=True)

# FOLLOW-UP QUESTIONS
st.markdown("""<div class="reveal-5"><div class="section-header"><span class="section-kicker">Go Deeper</span><span class="section-title">&nbsp;Questions to Explore</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
with st.spinner("Generating questions…"):
    try: questions = generate_followup_questions(result.get("summary", ""), _saved_lang_code, _saved_lang_name)
    except: questions = []
qh = "<div class='reveal-5'>"
for i, q in enumerate(questions, 1):
    qh += f'<div class="question-item"><div class="question-num">Q{i:02d}</div>{q}</div>'
qh += "</div>"
st.markdown(qh, unsafe_allow_html=True)

# EXPORT
st.markdown("""<div class="reveal-6"><div class="section-header"><span class="section-kicker">Download</span><span class="section-title">&nbsp;Export Report</span><div class="section-header-rule"></div></div></div>""", unsafe_allow_html=True)
st.markdown('''
<div class="export-panel">
  <div class="export-panel-row">
    <div class="export-item">
      <div class="export-icon">📄</div>
      <div class="export-meta">
        <div class="export-title">Full Analysis Report</div>
        <div class="export-desc">Complete breakdown — summary, key points, timeline, entities</div>
      </div>
    </div>
    <div class="export-item">
      <div class="export-icon">🖼</div>
      <div class="export-meta">
        <div class="export-title">Share Card</div>
        <div class="export-desc">Visual PNG card — ready to share on social or messaging</div>
      </div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

_dl_col, _share_col = st.columns(2)

with _dl_col:
    report = build_report(url, domain, result, entities, timeline, text)
    if st.button("📄  Generate Text Report", use_container_width=True):
        st.session_state["_report_text"] = report
    if "_report_text" in st.session_state:
        with st.expander("📄 Report Preview — click to read & download", expanded=False):
            st.code(st.session_state["_report_text"], language=None)
            st.download_button(
                label="⬇  Download .txt Report",
                data=st.session_state["_report_text"].encode("utf-8"),
                file_name=f"newssnap_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain", use_container_width=True,
            )

with _share_col:
    if PILLOW_AVAILABLE:
        if st.button("🖼  Generate Share Card (.png)", use_container_width=True):
            with st.spinner("Generating share card…"):
                _NON_LATIN = {"hi", "ta", "bn", "te", "ar", "ja", "zh", "ko"}
                if _saved_lang_code in _NON_LATIN:
                    _card_result   = analyze_article(text, "en", "English")
                    _card_cards    = generate_context_cards(text, "en", "English")
                    _card_entities = extract_entities(text, "en", "English")
                    _card_lang_code, _card_lang_name = "en", "English"
                else:
                    _card_result   = result
                    _card_cards    = cards
                    _card_entities = entities
                    _card_lang_code, _card_lang_name = _saved_lang_code, _saved_lang_name

                card_bytes = generate_share_card(
                    summary    = _card_result.get("summary", ""),
                    domain     = domain,
                    category   = _card_result.get("category", "—"),
                    sentiment  = _card_result.get("sentiment", "Neutral"),
                    url        = url,
                    bullets    = _card_result.get("bullets", []),
                    complexity = _card_result.get("reading_complexity", ""),
                    rt         = rt,
                    wc         = wc,
                    entities   = _card_entities,
                    lang_name  = _card_lang_name,
                    cards      = _card_cards,
                    lang_code  = _card_lang_code,
                )
                st.session_state["_card_bytes"] = card_bytes
        if "_card_bytes" in st.session_state:
            with st.expander("🖼 Share Card Preview — click to view & download", expanded=False):
                st.image(st.session_state["_card_bytes"], use_container_width=True)
                st.download_button(
                    label="⬇  Download Share Card (.png)",
                    data=st.session_state["_card_bytes"],
                    file_name=f"newssnap_card_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.png",
                    mime="image/png",
                    use_container_width=True,
                )
    else:
        st.info("Install Pillow to enable share cards: `pip install pillow`")

_footer_date = datetime.datetime.now().strftime('%d %b %Y · %H:%M')
components.html(f"""<!DOCTYPE html>
<html><head><style>
  *{{margin:0;padding:0;box-sizing:border-box;font-family:'DM Sans',sans-serif;}}
  body{{background:transparent;padding-top:1.5rem;}}
  .footer{{
    border-top:2px solid #0d0d0f;
    padding-top:0.9rem;
    display:flex;
    flex-direction:column;
    gap:0.45rem;
    font-size:0.72rem;
    color:#7a7a88;
    letter-spacing:0.04em;
  }}
  .footer-top{{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:0.3rem;
  }}
  .footer-url{{
    display:block;
    word-break:break-all;
    font-family:'JetBrains Mono',monospace;
    font-size:0.68rem;
    color:#c8392b;
    text-decoration:none;
    border-bottom:1px solid rgba(200,57,43,0.35);
    padding-bottom:2px;
    transition:opacity 0.15s;
    cursor:pointer;
  }}
  .footer-url:hover{{opacity:0.7;}}
</style></head>
<body>
  <div class="footer">
    <div class="footer-top">
      <span>NewsSnap AI</span>
      <span>Powered by Groq · LLaMA 3.1 · Tavily Search</span>
      <span>{_footer_date}</span>
    </div>
    <a class="footer-url" href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>
  </div>
</body></html>""", height=90, scrolling=False)


# ══════════════════════════════════════════════════════════════════════
# FLOATING CHAT WIDGET  — injected via components.html so it escapes
# Streamlit's iframe and can use position:fixed on the real viewport.
# The widget talks back to Streamlit through a hidden st.text_input
# that gets programmatically set + a form submit via JS.
# ══════════════════════════════════════════════════════════════════════

# Init chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ── invisible form that captures JS-submitted questions ──
with st.form("chat_form", clear_on_submit=True):
    hidden_q = st.text_input("chat_question", label_visibility="collapsed", key="chat_question_input")
    submitted = st.form_submit_button("send", disabled=True)   # JS clicks this

if submitted and hidden_q.strip() and "article_text" in st.session_state:
    st.session_state["chat_history"].append({"role": "user", "content": hidden_q})
    _chat_lang_code = st.session_state.get("lang_code", "en")
    _chat_lang_name = st.session_state.get("lang_name", "English")
    with st.spinner("Thinking…"):
        try:
            answer, sources = chat_with_search(
                hidden_q,
                st.session_state["article_text"],
                st.session_state["result"].get("summary", ""),
                st.session_state["chat_history"],
                _chat_lang_code,
                _chat_lang_name,
            )
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": answer, "sources": sources}
            )
        except Exception as e:
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": f"Error: {e}", "sources": []}
            )
    st.rerun()

# Hide the invisible form from view completely
st.markdown("""
<style>
div[data-testid="stForm"]{position:absolute!important;left:-9999px!important;width:0!important;height:0!important;overflow:hidden!important;}
</style>""", unsafe_allow_html=True)

# ── Serialise chat history to JSON for the JS widget ──
tavily_ok = bool(tavily_api_key)
article_ready = "article_text" in st.session_state
chat_history_json = json.dumps(st.session_state.get("chat_history", []))

# ── Inject the floating widget via components.html (true fixed positioning) ──
CHAT_WIDGET_HTML = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:transparent; font-family:'DM Sans','Segoe UI',sans-serif; overflow:hidden; }}

  /* ── FAB button ── */
  #fab {{
    position:fixed; bottom:28px; right:28px; z-index:99999;
    width:56px; height:56px; border-radius:50%;
    background:#0d0d0f; border:2.5px solid #e8b84b;
    display:flex; align-items:center; justify-content:center;
    cursor:pointer; box-shadow:0 6px 28px rgba(0,0,0,0.35);
    font-size:22px; transition:transform .18s, background .18s;
    user-select:none;
  }}
  #fab:hover {{ transform:scale(1.1); background:#c8392b; }}

  /* tooltip above FAB */
  #fab-tip {{
    position:fixed; bottom:92px; right:22px; z-index:99998;
    background:#0d0d0f; color:rgba(255,255,255,0.88);
    font-family:'JetBrains Mono',monospace; font-size:11px;
    letter-spacing:.07em; padding:5px 12px; border-radius:3px;
    white-space:nowrap; box-shadow:0 4px 16px rgba(0,0,0,0.28);
    border:1px solid rgba(255,255,255,0.08);
    pointer-events:none; opacity:0; transition:opacity .2s;
  }}
  #fab:hover + #fab-tip {{ opacity:1; }}

  /* ── Chat panel ── */
  #panel {{
    position:fixed; bottom:96px; right:28px; z-index:99998;
    width:400px; max-height:560px;
    background:#fff; border:1.5px solid #e0e0d8;
    border-radius:12px; box-shadow:0 12px 48px rgba(0,0,0,0.22);
    display:none; flex-direction:column; overflow:hidden;
    animation:slideUp .22s ease both;
  }}
  @keyframes slideUp {{ from{{opacity:0;transform:translateY(20px)}} to{{opacity:1;transform:translateY(0)}} }}

  /* top bar */
  .topbar {{
    background:#0d0d0f; padding:12px 16px;
    display:flex; align-items:center; justify-content:space-between; flex-shrink:0;
  }}
  .topbar-left {{ display:flex; align-items:center; gap:8px; }}
  .dot {{ width:8px; height:8px; border-radius:50%; background:#e8b84b;
          animation:pulse 2s ease infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.5;transform:scale(.8)}} }}
  .topbar-title {{ font-family:'JetBrains Mono',monospace; font-size:11px;
                   color:rgba(255,255,255,.85); letter-spacing:.08em; text-transform:uppercase; }}
  .topbar-badge {{ font-family:'JetBrains Mono',monospace; font-size:10px; color:#e8b84b;
                   border:1px solid rgba(232,184,75,.3); padding:2px 7px;
                   border-radius:2px; letter-spacing:.05em; }}
  .close-btn {{ background:none; border:none; color:rgba(255,255,255,.5);
                cursor:pointer; font-size:18px; line-height:1; padding:0 4px; }}
  .close-btn:hover {{ color:#fff; }}

  /* messages */
  #messages {{
    flex:1; overflow-y:auto; padding:14px 14px 6px;
    display:flex; flex-direction:column; gap:10px;
    max-height:380px; scroll-behavior:smooth;
  }}
  .msg {{ display:flex; gap:8px; align-items:flex-start; animation:fadeIn .25s ease both; }}
  @keyframes fadeIn {{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
  .msg.user {{ flex-direction:row-reverse; }}
  .avatar {{
    width:28px; height:28px; border-radius:50%; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    font-size:9px; font-weight:700;
  }}
  .avatar.ai  {{ background:#0d0d0f; color:#e8b84b; }}
  .avatar.user{{ background:#c8392b; color:#fff; }}
  .bubble {{ max-width:82%; padding:9px 12px; border-radius:4px; font-size:13.5px; line-height:1.6; }}
  .bubble.ai  {{ background:#f2f2ee; color:#3a3a44; border:1px solid #e0e0d8;
                 border-radius:2px 10px 10px 10px; }}
  .bubble.user{{ background:#0d0d0f; color:rgba(255,255,255,.92);
                 border-radius:10px 2px 10px 10px; }}

  /* sources */
  .sources {{ margin-top:7px; padding-top:6px; border-top:1px solid #e0e0d8; }}
  .src-label {{ font-family:'JetBrains Mono',monospace; font-size:9px; text-transform:uppercase;
                letter-spacing:.08em; color:#7a7a88; margin-bottom:4px; }}
  .src-chip {{
    display:inline-block; font-size:11px; color:#3a6ea8;
    background:rgba(58,110,168,.07); border:1px solid rgba(58,110,168,.2);
    border-radius:2px; padding:2px 8px; margin:2px 3px 2px 0;
    text-decoration:none; cursor:pointer;
  }}
  .src-chip:hover {{ background:rgba(58,110,168,.16); }}

  /* typing dots */
  #typing {{ display:none; padding:0 14px 8px; gap:8px; align-items:center; flex-shrink:0; }}
  .typing-bubble {{ background:#f2f2ee; border:1px solid #e0e0d8;
                    border-radius:2px 10px 10px 10px; padding:9px 14px;
                    display:flex; gap:5px; align-items:center; }}
  .dot-t {{ width:6px; height:6px; border-radius:50%; background:#7a7a88;
            animation:bounce .9s ease infinite; }}
  .dot-t:nth-child(2){{ animation-delay:.2s; }}
  .dot-t:nth-child(3){{ animation-delay:.4s; }}
  @keyframes bounce {{ 0%,80%,100%{{transform:translateY(0)}} 40%{{transform:translateY(-5px)}} }}

  /* input row */
  .input-row {{
    display:flex; gap:8px; padding:10px 12px; flex-shrink:0;
    border-top:1.5px solid #e0e0d8; background:#fafaf8;
  }}
  #chat-input {{
    flex:1; font-family:'DM Sans',sans-serif; font-size:13.5px;
    background:#fff; border:1.5px solid #e0e0d8; border-radius:4px;
    padding:8px 12px; color:#0d0d0f; outline:none;
    transition:border-color .15s;
  }}
  #chat-input:focus {{ border-color:#c8392b; box-shadow:0 0 0 3px rgba(200,57,43,.1); }}
  #chat-input:disabled {{ opacity:.5; cursor:not-allowed; }}
  #send-btn {{
    background:#0d0d0f; color:#fff; border:none; border-radius:4px;
    padding:0 14px; cursor:pointer; font-size:16px;
    transition:background .15s; display:flex; align-items:center; justify-content:center;
  }}
  #send-btn:hover {{ background:#c8392b; }}
  #send-btn:disabled {{ background:#ccc; cursor:not-allowed; }}

  /* disabled state overlay */
  .disabled-notice {{
    text-align:center; font-size:12px; color:#7a7a88;
    padding:6px 0 2px; font-style:italic;
  }}
</style>
</head>
<body>

<!-- FAB -->
<div id="fab" onclick="togglePanel()" title="Ask about this article">💬</div>
<div id="fab-tip">ASK THE ARTICLE</div>

<!-- Chat panel -->
<div id="panel">
  <div class="topbar">
    <div class="topbar-left">
      <div class="dot"></div>
      <div class="topbar-title">Research Chatbot</div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <div class="topbar-badge">{'TAVILY + ARTICLE' if tavily_ok else 'ARTICLE ONLY'}</div>
      <button class="close-btn" onclick="togglePanel()">×</button>
    </div>
  </div>

  <div id="messages"></div>

  <div id="typing" style="display:none;padding:0 14px 8px;">
    <div style="display:flex;gap:8px;align-items:center;">
      <div class="avatar ai">AI</div>
      <div class="typing-bubble">
        <div class="dot-t"></div><div class="dot-t"></div><div class="dot-t"></div>
      </div>
    </div>
  </div>

  {'<div class="disabled-notice">Analyse an article first to enable chat</div>' if not article_ready else ''}

  <div class="input-row">
    <input id="chat-input" type="text"
      placeholder="{'Ask about this story…' if article_ready else 'Analyse an article first…'}"
      {'disabled' if not article_ready else ''}
      onkeydown="if(event.key==='Enter')sendMessage()"
    />
    <button id="send-btn" onclick="sendMessage()" {'disabled' if not article_ready else ''}>➤</button>
  </div>
</div>

<script>
  // ── State ──
  var isOpen = false;
  var chatHistory = {chat_history_json};
  var sending = false;

  // ── Toggle panel ──
  function togglePanel() {{
    isOpen = !isOpen;
    var panel = document.getElementById('panel');
    if (isOpen) {{
      panel.style.display = 'flex';
      renderMessages();
      setTimeout(function(){{ document.getElementById('chat-input').focus(); }}, 100);
    }} else {{
      panel.style.display = 'none';
    }}
  }}

  // ── Render all messages ──
  function renderMessages() {{
    var box = document.getElementById('messages');
    box.innerHTML = '';

    // welcome message if empty
    if (chatHistory.length === 0) {{
      box.innerHTML = '<div class="msg"><div class="avatar ai">AI</div><div class="bubble ai">Ask me anything about this story. I\'ll search the web for related coverage to give you the full picture.</div></div>';
      return;
    }}

    chatHistory.forEach(function(msg) {{
      var cls = msg.role === 'user' ? 'user' : 'ai';
      var lbl = msg.role === 'user' ? 'YOU' : 'AI';
      var srcHtml = '';
      if (msg.sources && msg.sources.length > 0) {{
        srcHtml = '<div class="sources"><div class="src-label">Sources</div>';
        msg.sources.slice(0,3).forEach(function(s) {{
          var title = (s.title || '').substring(0, 45);
          srcHtml += '<a class="src-chip" href="' + s.url + '" target="_blank" rel="noopener">' + title + '…</a>';
        }});
        srcHtml += '</div>';
      }}
      var div = document.createElement('div');
      div.className = 'msg ' + cls;
      div.innerHTML = '<div class="avatar ' + cls + '">' + lbl + '</div><div class="bubble ' + cls + '">' + escapeHtml(msg.content) + srcHtml + '</div>';
      box.appendChild(div);
    }});
    box.scrollTop = box.scrollHeight;
  }}

  function escapeHtml(s) {{
    return String(s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\\n/g,'<br>');
  }}

  // ── Send message via Streamlit hidden form ──
  function sendMessage() {{
    if (sending) return;
    var inp = document.getElementById('chat-input');
    var q = inp.value.trim();
    if (!q) return;
    inp.value = '';

    sending = true;
    document.getElementById('send-btn').disabled = true;
    document.getElementById('typing').style.display = 'block';

    // Append optimistic user bubble
    chatHistory.push({{role:'user', content:q, sources:[]}});
    renderMessages();

    // ── Write into Streamlit's hidden text input and submit the form ──
    // Streamlit renders inputs inside shadow-like divs; we target by label key.
    var attempts = 0;
    function tryInject() {{
      // Find the hidden input (Streamlit renders it with data-testid="stTextInput")
      var allInputs = window.parent.document.querySelectorAll('input[type="text"]');
      var target = null;
      allInputs.forEach(function(el) {{
        // Our hidden input has placeholder "" and is inside the invisible form
        if (el.closest('form') && el.value === '' && el.placeholder === '') target = el;
      }});

      if (!target && attempts < 20) {{
        attempts++;
        setTimeout(tryInject, 100);
        return;
      }}

      if (target) {{
        // Set value via React's synthetic event system
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(target, q);
        target.dispatchEvent(new Event('input', {{bubbles:true}}));

        setTimeout(function() {{
          // Click the hidden submit button
          var btns = window.parent.document.querySelectorAll('button[kind="secondaryFormSubmit"], button[type="submit"]');
          btns.forEach(function(btn) {{
            if (btn.closest('form')) btn.click();
          }});
        }}, 80);
      }}
    }}
    tryInject();
  }}

  // ── Poll for new messages from Streamlit (session state updates) ──
  // Streamlit re-renders the page; the component gets a new chatHistory prop
  // encoded in the HTML. We compare lengths to detect new AI replies.
  var lastLen = chatHistory.length;
  setInterval(function() {{
    // The updated chat_history is baked into a new render of this component.
    // Since components.html re-renders on st.rerun(), the whole iframe reloads,
    // so polling isn't needed — the iframe will reload with fresh data.
  }}, 1000);

  // Auto-open panel if there's history (i.e. user just got a reply)
  if (chatHistory.length > 0) {{
    isOpen = true;
    document.getElementById('panel').style.display = 'flex';
    setTimeout(renderMessages, 50);
  }}

  // Hide typing indicator (it was shown pre-rerun)
  sending = false;
</script>
</body>
</html>
"""

# Render the floating widget — height=1 because it uses fixed positioning
# within the iframe's viewport which is sized to the parent window by Streamlit
components.html(CHAT_WIDGET_HTML, height=1, scrolling=False)

# Streamlit injects a style to make the iframe height=1px but position:fixed
# children escape the iframe clip in Chrome/Edge. We also set the iframe to
# be transparent and full-window so fixed children are visible everywhere.
st.markdown("""
<style>
iframe[title="components.html"] {
    position: fixed !important;
    bottom: 0 !important;
    right: 0 !important;
    width: 520px !important;
    height: 100vh !important;
    border: none !important;
    z-index: 99997 !important;
    pointer-events: none;
    background: transparent !important;
}
iframe[title="components.html"] * {
    pointer-events: all;
}
</style>
""", unsafe_allow_html=True)