import io

import streamlit as st

from services.book_loader import load_uploaded_book
from services.text_splitter import split_book
from services.vector_store import create_vector_store
from services.rag_service import answer_question
from services.summary_service import generate_summary
from services.quiz_service import generate_quiz


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LearnLens AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown(
    """
<style>

/* =====================================================
   GLOBAL
   ===================================================== */

.stApp {
    background:
        radial-gradient(
            circle at top right,
            rgba(183, 143, 67, 0.07),
            transparent 30%
        ),
        #f8f6f1;
}

.block-container {
    max-width: 1250px;
    padding-top: 2.2rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    color: #17233c;
    letter-spacing: -0.02em;
}

p {
    color: #4c5568;
}


/* =====================================================
   STREAMLIT HEADER SPACING
   ===================================================== */

[data-testid="stHeader"] {
    background: #0e1117;
}

[data-testid="stMainBlockContainer"] {
    padding-top: 2.2rem;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

[data-testid="stSidebar"] {
    background: #17233c;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

[data-testid="stSidebar"] * {
    color: #f7f3e8;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.14);
}

[data-testid="stSidebar"] .stCaption {
    color: #c6cad4 !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.06);
    padding: 0.7rem;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.10);
}


/* =====================================================
   HERO
   ===================================================== */

.ll-hero {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(
            135deg,
            #17233c 0%,
            #263c62 100%
        );
    border-radius: 22px;
    padding: 2.2rem 2.6rem;
    margin-bottom: 2rem;
    box-shadow: 0 14px 38px rgba(23, 35, 60, 0.16);
}

.ll-hero::after {
    content: "AI";
    position: absolute;
    right: 2rem;
    top: -1.2rem;
    font-size: 9rem;
    font-weight: 800;
    color: rgba(255, 255, 255, 0.035);
    pointer-events: none;
}

.ll-eyebrow {
    color: #f1bd50;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

.ll-title {
    color: #ffffff;
    font-size: 2.6rem;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -0.035em;
    margin-bottom: 0.7rem;
}

.ll-title-icon {
    color: #f1bd50;
    margin-right: 0.35rem;
}

.ll-subtitle {
    max-width: 780px;
    color: #e4e8ef !important;
    font-size: 1.02rem;
    line-height: 1.7;
    margin: 0;
}


/* =====================================================
   EMPTY STATE
   ===================================================== */

.ll-empty {
    background: rgba(255, 255, 255, 0.95);
    border: 1px solid #e7e1d6;
    border-radius: 22px;
    padding: 3.5rem 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(32, 43, 64, 0.06);
}

.ll-empty-icon {
    font-size: 2.7rem;
    margin-bottom: 1rem;
}

.ll-empty-title {
    color: #17233c;
    font-size: 1.35rem;
    font-weight: 750;
    margin-bottom: 0.7rem;
}

.ll-empty-text {
    color: #697386;
    max-width: 760px;
    margin: auto;
    line-height: 1.7;
}

.ll-format-row {
    color: #9a762e;
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 0.08em;
    margin-top: 1.6rem;
}


/* =====================================================
   STATUS CARDS
   ===================================================== */

.ll-card {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid #e9e4da;
    border-radius: 17px;
    padding: 1rem 1.15rem;
    min-height: 105px;
    box-shadow: 0 7px 24px rgba(32, 43, 64, 0.05);
}

.ll-card-label {
    color: #9a762e;
    font-size: 0.71rem;
    font-weight: 750;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}

.ll-card-value {
    color: #17233c;
    font-size: 1.03rem;
    font-weight: 720;
    line-height: 1.3;
}

.ll-card-sub {
    color: #7a8392;
    font-size: 0.78rem;
    margin-top: 0.35rem;
}


/* =====================================================
   SECTION HEADERS
   ===================================================== */

.ll-section-kicker {
    color: #a57c2d;
    font-size: 0.73rem;
    font-weight: 750;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-top: 1rem;
    margin-bottom: 0.25rem;
}

.ll-section-title {
    color: #17233c;
    font-size: 1.65rem;
    font-weight: 750;
    margin-bottom: 0.25rem;
}

.ll-section-description {
    color: #697386;
    font-size: 0.94rem;
    margin-bottom: 1rem;
    line-height: 1.55;
}


/* =====================================================
   TABS
   ===================================================== */

.stTabs [data-baseweb="tab-list"] {
    gap: 0.4rem;
    background: #ece8df;
    border-radius: 14px;
    padding: 0.35rem;
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    border-radius: 10px;
    padding-left: 1.4rem;
    padding-right: 1.4rem;
    color: #536074;
    font-weight: 650;
}

.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #17233c !important;
    box-shadow: 0 3px 10px rgba(25, 35, 55, 0.07);
}


/* =====================================================
   BUTTONS
   ===================================================== */

.stButton > button {
    border-radius: 11px;
    font-weight: 650;
    min-height: 42px;
    transition: 0.18s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

button[kind="primary"] {
    background: #17233c !important;
    border-color: #17233c !important;
    color: white !important;
}

/* Secondary buttons on light background */
.stButton > button:not([kind="primary"]) {
    background: #ffffff !important;
    color: #17233c !important;
    border: 1px solid #d8dce4 !important;
}

.stButton > button:not([kind="primary"]):hover {
    background: #f3f5f8 !important;
    color: #17233c !important;
    border-color: #17233c !important;
}

.stButton > button:not([kind="primary"]) p {
    color: #17233c !important;
}

/* =====================================================
   INPUTS
   ===================================================== */

div[data-baseweb="select"] > div {
    border-radius: 11px;
}

[data-testid="stChatInput"] {
    border-radius: 14px;
}

/* =====================================================
   CHAT
   ===================================================== */

[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e4ded3 !important;
    border-radius: 16px !important;
    padding: 0.7rem 1rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: 0 5px 18px rgba(32, 43, 64, 0.05);
}

/* Force chat text to remain readable on light cards */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #344054;
}

/* User question */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) p {
    color: #17233c !important;
    font-weight: 650;
}

/* Assistant answer */
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) p,
[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) li {
    color: #344054 !important;
    line-height: 1.7;
}

/* Markdown headings inside answers */
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 {
    color: #17233c !important;
}

/* Bold text inside answers */
[data-testid="stChatMessage"] strong {
    color: #17233c !important;
}

/* Chat input */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
}

[data-testid="stChatInput"] textarea {
    color: #f8fafc !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #b7bdc8 !important;
}

/* =====================================================
   EXPANDERS
   ===================================================== */

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid #e6e1d7;
    border-radius: 13px;
    overflow: hidden;
}


/* =====================================================
   QUIZ
   ===================================================== */

[data-testid="stRadio"] {
    background: #ffffff;
    border: 1px solid #ebe6dc;
    border-radius: 14px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
}


/* =====================================================
   ALERTS
   ===================================================== */

[data-testid="stAlert"] {
    border-radius: 13px;
}


/* =====================================================
   FOOTER
   ===================================================== */

.ll-footer {
    text-align: center;
    color: #9a9faa;
    font-size: 0.78rem;
    margin-top: 3rem;
    padding-top: 1.3rem;
    border-top: 1px solid #e5e0d7;
}

/* =====================================================
   CONFIRMATION DIALOG
   ===================================================== */

/* Dialog background */
div[data-testid="stDialog"] > div {
    background: #ffffff !important;
    color: #17233c !important;
}

/* Dialog title */
div[data-testid="stDialog"] h2 {
    color: #17233c !important;
    font-weight: 750 !important;
}

/* Normal dialog text */
div[data-testid="stDialog"] p {
    color: #4c5568 !important;
}

/* Warning box */
div[data-testid="stDialog"] [data-testid="stAlert"] {
    background: #fff7df !important;
    border: 1px solid #ead59a !important;
}

/* Warning text */
div[data-testid="stDialog"] [data-testid="stAlert"] p {
    color: #765b18 !important;
}

/* Cancel button */
div[data-testid="stDialog"] button[kind="secondary"] {
    background: #ffffff !important;
    color: #17233c !important;
    border: 1px solid #d8dce4 !important;
}

div[data-testid="stDialog"] button[kind="secondary"] p {
    color: #17233c !important;
}

/* Delete button */
div[data-testid="stDialog"] button[kind="primary"] {
    background: #b42318 !important;
    border-color: #b42318 !important;
    color: #ffffff !important;
}

div[data-testid="stDialog"] button[kind="primary"] p {
    color: #ffffff !important;
}

/* Delete button hover */
div[data-testid="stDialog"] button[kind="primary"]:hover {
    background: #912018 !important;
    border-color: #912018 !important;
}

/* Close X */
div[data-testid="stDialog"] button {
    opacity: 1 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# FINAL UI POLISH OVERRIDES
# =========================================================

st.markdown(
    """
<style>

/* Compact workspace */
.block-container {
    max-width: 1180px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
}

/* Smaller hero: tools appear sooner */
.ll-hero {
    padding: 1.55rem 2rem !important;
    margin-bottom: 1.15rem !important;
    border-radius: 18px !important;
}

.ll-hero::after { font-size: 7rem !important; }
.ll-eyebrow { margin-bottom: 0.45rem !important; }

.ll-title {
    font-size: 2.15rem !important;
    margin-bottom: 0.45rem !important;
}

.ll-subtitle {
    font-size: 0.94rem !important;
    line-height: 1.55 !important;
}

/* Compact status cards */
.ll-card {
    min-height: 88px !important;
    padding: 0.8rem 1rem !important;
}

.ll-card-label { margin-bottom: 0.3rem !important; }
.ll-card-sub { margin-top: 0.2rem !important; }

/* Main navigation */
.stTabs [data-baseweb="tab-list"] {
    position: sticky;
    top: 0.35rem;
    z-index: 20;
    margin-top: 0.15rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 5px 16px rgba(23, 35, 60, 0.06);
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
}

/* Compact section headings */
.ll-section-kicker { margin-top: 0.35rem !important; }
.ll-section-title { font-size: 1.45rem !important; }
.ll-section-description { margin-bottom: 0.7rem !important; }

/* Readable controls */
.stSelectbox label,
.stRadio label,
.stTextInput label {
    color: #344054 !important;
    font-weight: 600 !important;
}

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #17233c !important;
    border: 1px solid #d8dce4 !important;
}

div[data-baseweb="select"] span {
    color: #17233c !important;
}

/* Primary buttons */
button[kind="primary"],
.stButton > button[kind="primary"] {
    background: #17233c !important;
    border-color: #17233c !important;
    color: #ffffff !important;
    opacity: 1 !important;
}

button[kind="primary"] p,
.stButton > button[kind="primary"] p {
    color: #ffffff !important;
}

/* Prominent chat input */
[data-testid="stChatInput"] {
    border: 2px solid #263c62 !important;
    box-shadow: 0 5px 16px rgba(23, 35, 60, 0.09) !important;
    margin-bottom: 0.75rem !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #cbd1dc !important;
}

/* Compact chat cards */
[data-testid="stChatMessage"] {
    padding: 0.65rem 0.9rem !important;
    margin-bottom: 0.55rem !important;
}

[data-testid="stChatMessage"] p {
    margin-bottom: 0.45rem !important;
}

/* Bordered result/question containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-radius: 16px !important;
    margin-bottom: 0.45rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] li,
[data-testid="stVerticalBlockBorderWrapper"] strong {
    color: #26344d !important;
}

[data-testid="stVerticalBlockBorderWrapper"] h1,
[data-testid="stVerticalBlockBorderWrapper"] h2,
[data-testid="stVerticalBlockBorderWrapper"] h3 {
    color: #17233c !important;
}

/* Quiz */
[data-testid="stRadio"] {
    background: #ffffff !important;
    border: 1px solid #ded8cd !important;
    padding: 0.55rem 0.8rem !important;
    margin: 0.3rem 0 0.25rem !important;
}

[data-testid="stRadio"] p,
[data-testid="stRadio"] label,
[data-testid="stRadio"] span,
[data-testid="stRadio"] div {
    color: #26344d !important;
}

[data-testid="stVerticalBlockBorderWrapper"] h3 {
    font-size: 1.16rem !important;
    line-height: 1.4 !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.45rem !important;
}

[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] p {
    color: #7a8392 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
}

/* Metrics */
[data-testid="stMetricLabel"] p {
    color: #697386 !important;
}

[data-testid="stMetricValue"] {
    color: #17233c !important;
}

/* Sidebar metrics */
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.35rem !important;
}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] p {
    color: #c6cad4 !important;
}

/* Alerts and footer */
[data-testid="stAlert"] p { opacity: 1 !important; }
.ll-footer { margin-top: 1.8rem !important; }

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# FINAL UX REDESIGN
# =========================================================

st.markdown(
    """
<style>
/* Final visual system */
.block-container { max-width: 1120px !important; padding-top: 1.15rem !important; }
.ll-hero { padding: 1.35rem 1.7rem !important; margin-bottom: 1rem !important; border-radius: 18px !important; }
.ll-title { font-size: 2rem !important; }
.ll-subtitle { max-width: 700px !important; }

/* Compact document strip instead of dashboard clutter */
.ll-doc-strip {
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
  background:#fff; border:1px solid #e6e0d5; border-radius:14px;
  padding:.8rem 1rem; margin:.75rem 0 1rem; box-shadow:0 5px 18px rgba(23,35,60,.045);
}
.ll-doc-main { color:#17233c; font-weight:750; }
.ll-doc-meta { color:#7a8392; font-size:.82rem; margin-top:.15rem; }
.ll-ready-pill { white-space:nowrap; background:#edf7ef; color:#287a43; border:1px solid #cfe8d5; border-radius:999px; padding:.4rem .75rem; font-size:.78rem; font-weight:750; }

/* Tool navigation should look like real navigation */
.stTabs [data-baseweb="tab-list"] {
  position:static !important; background:#fff !important; border:1px solid #e3ddd2 !important;
  border-radius:15px !important; padding:.35rem !important; gap:.35rem !important;
  box-shadow:0 6px 20px rgba(23,35,60,.055) !important; margin-bottom:1.15rem !important;
}
.stTabs [data-baseweb="tab"] { min-height:52px !important; font-size:.95rem !important; color:#5d687a !important; }
.stTabs [aria-selected="true"] { background:#17233c !important; color:#fff !important; box-shadow:none !important; }
.stTabs [aria-selected="true"] p { color:#fff !important; }

/* Ask AI is the primary action */
.ll-chat-intro { background:#fff; border:1px solid #e4ded3; border-radius:16px; padding:1rem 1.15rem .9rem; margin-bottom:.75rem; }
.ll-chat-intro .ll-section-kicker { margin-top:0 !important; }
[data-testid="stChatInput"] { background:#17233c !important; border:2px solid #17233c !important; border-radius:15px !important; box-shadow:0 8px 24px rgba(23,35,60,.13) !important; }
[data-testid="stChatInput"] textarea { color:#fff !important; font-size:1rem !important; }
[data-testid="stChatInput"] textarea::placeholder { color:#cbd2df !important; }

/* Summary controls */
.ll-tool-card { background:#fff; border:1px solid #e4ded3; border-radius:18px; padding:1.1rem 1.2rem; box-shadow:0 6px 20px rgba(23,35,60,.045); margin-bottom:1rem; }
[data-testid="stAlert"] { background:#f4f7fb !important; border:1px solid #dde5ef !important; }
[data-testid="stAlert"] p { color:#43516a !important; }

/* Quiz: high contrast, grouped, readable */
[data-testid="stVerticalBlockBorderWrapper"] {
  background:#fff !important; border:1px solid #e1dbd0 !important; border-radius:18px !important;
  box-shadow:0 5px 18px rgba(23,35,60,.045) !important; padding:.35rem !important; margin-bottom:1rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] h3,
[data-testid="stVerticalBlockBorderWrapper"] h3 p { color:#17233c !important; opacity:1 !important; font-size:1.16rem !important; line-height:1.45 !important; }
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stVerticalBlockBorderWrapper"] span { color:#344054 !important; opacity:1 !important; }
[data-testid="stRadio"] { border:0 !important; background:transparent !important; padding:.15rem 0 !important; }
[data-testid="stRadio"] label { background:#f8f9fb !important; border:1px solid #e1e5eb !important; border-radius:10px !important; padding:.55rem .7rem !important; margin:.22rem 0 !important; }
[data-testid="stRadio"] label:hover { border-color:#263c62 !important; background:#f2f5f9 !important; }

/* Keep every heading readable on cream background */
.stApp h1,.stApp h2,.stApp h3,.stApp h4 { color:#17233c !important; }
.stApp [data-testid="stCaptionContainer"] p { color:#7a8392 !important; }

@media (max-width: 760px) {
  .ll-doc-strip { align-items:flex-start; flex-direction:column; }
  .ll-ready-pill { align-self:flex-start; }
  .ll-hero::after { display:none; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<style>
/* ===== Workspace navigation: large, unmistakable controls ===== */
[data-testid="stSegmentedControl"] { margin: .7rem 0 1.35rem !important; }
[data-testid="stSegmentedControl"] [role="radiogroup"] {
    width:100% !important; background:#ffffff !important; border:1px solid #ddd6ca !important;
    border-radius:16px !important; padding:6px !important; gap:6px !important;
    box-shadow:0 6px 20px rgba(23,35,60,.06) !important;
}
[data-testid="stSegmentedControl"] label {
    flex:1 1 0 !important; min-height:50px !important; justify-content:center !important;
    border-radius:11px !important; font-weight:750 !important; color:#46546b !important;
}
[data-testid="stSegmentedControl"] label:has(input:checked) {
    background:#17233c !important; color:#ffffff !important;
}
[data-testid="stSegmentedControl"] label:has(input:checked) p,
[data-testid="stSegmentedControl"] label:has(input:checked) span { color:#ffffff !important; }

/* ===== Summary: one compact focused card ===== */
.ll-section-description { max-width:820px !important; margin-bottom:1rem !important; }

/* ===== Quiz: explicit contrast and compact question cards ===== */
.ll-quiz-question {
    color:#17233c !important; font-size:1.28rem !important; line-height:1.42 !important;
    font-weight:800 !important; margin:.35rem 0 .8rem !important; opacity:1 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    background:#ffffff !important; border:1px solid #ddd7cc !important;
    border-radius:16px !important; box-shadow:0 5px 18px rgba(23,35,60,.05) !important;
    margin-bottom:.85rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"] p {
    color:#8a6a1f !important; font-weight:800 !important; letter-spacing:.055em !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label {
    width:100% !important; background:#f8f9fb !important; border:1px solid #e1e5eb !important;
    border-radius:10px !important; padding:.62rem .8rem !important; margin:.18rem 0 !important;
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stRadio"] label p {
    color:#17233c !important; font-size:.96rem !important; opacity:1 !important;
}
@media (max-width:760px) {
  [data-testid="stSegmentedControl"] [role="radiogroup"] { flex-direction:column !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# HERO
# =========================================================

st.markdown(
    '<div class="ll-hero">'
    '<div class="ll-eyebrow">AI-Powered Learning Workspace</div>'
    '<div class="ll-title">'
    '<span class="ll-title-icon">&#10022;</span> LearnLens AI'
    '</div>'
    '<p class="ll-subtitle">'
    'Turn your learning material into interactive knowledge. '
    'Ask grounded questions, generate intelligent summaries, '
    'and test your understanding with AI-generated quizzes.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# =========================================================
# SIDEBAR BRANDING
# =========================================================

st.sidebar.markdown(
    """
## 📚 LearnLens AI

**AI Study & Document Assistant**

Upload learning material and transform it into an
interactive AI-powered knowledge base.
"""
)

st.sidebar.divider()


# =========================================================
# DOCUMENT UPLOAD
# =========================================================

st.sidebar.subheader(
    "📤 Upload Material"
)

uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF or TXT file",
    type=["pdf", "txt"],
    help=(
        "Upload books, textbooks, study notes, "
        "research papers, or other readable learning material."
    ),
)

st.sidebar.caption(
    "Supports books, textbooks, notes, papers "
    "and study material in PDF or TXT format."
)

# =========================================================
# EMPTY STATE
# =========================================================

if uploaded_file is None:

    st.markdown(
        '<div class="ll-empty">'
        '<div class="ll-empty-icon">📄</div>'
        '<div class="ll-empty-title">'
        'Your AI learning workspace is ready'
        '</div>'
        '<div class="ll-empty-text">'
        'Upload a PDF or TXT document from the sidebar. '
        'LearnLens AI will build a searchable knowledge base '
        'that you can explore through grounded question answering, '
        'smart summaries, and AI-generated quizzes.'
        '</div>'
        '<div class="ll-format-row">'
        'BOOKS &nbsp;·&nbsp; '
        'TEXTBOOKS &nbsp;·&nbsp; '
        'NOTES &nbsp;·&nbsp; '
        'RESEARCH PAPERS &nbsp;·&nbsp; '
        'STUDY MATERIAL'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.stop()

# =========================================================
# PROCESS UPLOADED DOCUMENT
# =========================================================

@st.cache_resource(show_spinner=False)
def prepare_uploaded_book(
    file_name,
    file_bytes,
):

    class UploadedDocument:

        def __init__(
            self,
            name,
            data,
        ):
            self.name = name
            self._data = data

        def getvalue(self):
            return self._data

        def read(
            self,
            *args,
            **kwargs,
        ):
            return self._data

    document_file = UploadedDocument(
        file_name,
        file_bytes,
    )

    if file_name.lower().endswith(".pdf"):

        document_file = io.BytesIO(
            file_bytes
        )

        document_file.name = file_name

    documents = load_uploaded_book(
        document_file
    )

    chunks = split_book(
        documents
    )

    vector_store = create_vector_store(
        chunks
    )

    return (
        documents,
        chunks,
        vector_store,
    )


try:

    with st.spinner(
        "Preparing your AI learning workspace..."
    ):

        documents, chunks, vector_store = (
            prepare_uploaded_book(
                uploaded_file.name,
                uploaded_file.getvalue(),
            )
        )

except Exception as error:

    st.error(
        f"Unable to process this document: {error}"
    )

    st.stop()


# =========================================================
# DOCUMENT METADATA
# =========================================================

file_type = (
    uploaded_file.name
    .split(".")[-1]
    .upper()
)

file_size_mb = (
    len(uploaded_file.getvalue())
    / (1024 * 1024)
)

document_display_name = uploaded_file.name

if len(document_display_name) > 34:

    document_display_name = (
        document_display_name[:31]
        + "..."
    )


# =========================================================
# SIDEBAR - CURRENT DOCUMENT
# =========================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📄 Current Document"
)

st.sidebar.markdown(
    f"**{uploaded_file.name}**"
)

sidebar_meta_1, sidebar_meta_2 = (
    st.sidebar.columns(2)
)

with sidebar_meta_1:

    st.metric(
        "Type",
        file_type,
    )

with sidebar_meta_2:

    st.metric(
        "Size",
        f"{file_size_mb:.2f} MB",
    )

st.sidebar.caption(
    f"🧩 {len(chunks)} knowledge chunks indexed"
)


# =========================================================
# SIDEBAR - AI STACK
# =========================================================

st.sidebar.divider()

st.sidebar.subheader(
    "🧠 AI Stack"
)

st.sidebar.markdown(
    """
**Embedding Model**  
BAAI/bge-small-en-v1.5

**Vector Database**  
FAISS

**Language Model**  
Llama 3.1 8B Instant

**Inference**  
Groq

**Architecture**  
Retrieval-Augmented Generation
"""
)


# =========================================================
# SIDEBAR - RAG PIPELINE
# =========================================================

with st.sidebar.expander(
    "⚙️ How LearnLens Works"
):

    st.markdown(
        """
**01 · Extract**  
Read text from the uploaded material.

**02 · Chunk**  
Split the document into smaller passages.

**03 · Embed**  
Convert passages into semantic vectors.

**04 · Index**  
Store embeddings inside FAISS.

**05 · Retrieve**  
Find passages relevant to the user's query.

**06 · Generate**  
Provide retrieved context to the LLM to produce a grounded response.
"""
    )


# =========================================================
# COMPACT DOCUMENT STATUS
# =========================================================

st.markdown(
    f'<div class="ll-doc-strip">'
    f'<div><div class="ll-doc-main">📄 {document_display_name}</div>'
    f'<div class="ll-doc-meta">{file_type} · {file_size_mb:.2f} MB · {len(chunks)} searchable chunks</div></div>'
    f'<div class="ll-ready-pill">● AI workspace ready</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# =========================================================
# WORKSPACE NAVIGATION
# =========================================================

# Use a real segmented workspace switch instead of Streamlit tabs.
# This keeps the primary tools obvious and avoids the tiny tab strip.
workspace = st.segmented_control(
    "Workspace",
    ["💬 Ask AI", "📝 Smart Summary", "🧠 AI Quiz"],
    default="💬 Ask AI",
    key="workspace_navigation",
    label_visibility="collapsed",
)

if workspace is None:
    workspace = "💬 Ask AI"


# =========================================================
# CLEAR CHAT CONFIRMATION
# =========================================================

@st.dialog(
    "Delete conversation?"
)
def confirm_clear_chat():

    st.warning(
        "Are you sure you want to delete "
        "the entire conversation?"
    )

    st.write(
        "All questions, answers and retrieved sources "
        "from this session will be removed."
    )

    cancel_col, delete_col = st.columns(2)

    with cancel_col:

        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_clear_chat",
        ):
            st.rerun()

    with delete_col:

        if st.button(
            "🗑️ Delete Conversation",
            type="primary",
            use_container_width=True,
            key="confirm_clear_chat",
        ):

            st.session_state.chat_history = []

            st.rerun()


# =========================================================
# ASK AI / DOCUMENT CHAT
# =========================================================

if workspace == "💬 Ask AI":

    st.markdown(
        """
<div class="ll-chat-intro">
<div class="ll-section-kicker">
    Grounded Question Answering
</div>

<div class="ll-section-title">
    Chat with your learning material
</div>

<div class="ll-section-description">
    Ask questions in natural language.
    LearnLens retrieves relevant passages from your uploaded
    document before generating a grounded answer.
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # INITIALIZE CHAT HISTORY
    # -----------------------------------------------------

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "active_document" not in st.session_state:
        st.session_state.active_document = uploaded_file.name

    # -----------------------------------------------------
    # RESET HISTORY WHEN DOCUMENT CHANGES
    # -----------------------------------------------------

    if (
        st.session_state.active_document
        != uploaded_file.name
    ):

        st.session_state.chat_history = []
        st.session_state.active_document = uploaded_file.name

    # -----------------------------------------------------
    # CHAT INPUT
    # -----------------------------------------------------

    question = st.chat_input(
        "Ask something about your material...",
        key="document_chat_input",
    )

    # -----------------------------------------------------
    # PROCESS QUESTION
    # -----------------------------------------------------

    if question:

        try:

            with st.spinner(
                "Searching your material and generating an answer..."
            ):

                answer, sources = answer_question(
                    vector_store,
                    question,
                )

            stored_sources = []

            for source in sources:

                stored_sources.append(
                    {
                        "content": source.page_content,
                        "document_name":
                            source.metadata.get(
                                "book_name",
                                uploaded_file.name,
                            ),
                    }
                )

            conversation = {
                "question": question,
                "answer": answer,
                "sources": stored_sources,
            }

            # Newest conversation appears first.
            st.session_state.chat_history.insert(
                0,
                conversation,
            )

        except Exception as error:

            conversation = {
                "question": question,
                "answer": (
                    "Unable to generate an answer: "
                    f"{error}"
                ),
                "sources": [],
            }

            st.session_state.chat_history.insert(
                0,
                conversation,
            )

    # -----------------------------------------------------
    # CHAT CONTROLS
    # -----------------------------------------------------

    if st.session_state.chat_history:

        clear_col, spacer_col = st.columns(
            [1.4, 5.6]
        )

        with clear_col:

            if st.button(
                "🗑️ Clear Conversation",
                key="clear_chat_button",
                use_container_width=True,
            ):
                confirm_clear_chat()

        st.divider()

    else:

        st.info(
            "Ask about concepts, characters, definitions, "
            "events, explanations, relationships, or any "
            "information contained in the uploaded material."
        )

    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    for conversation_index, conversation in enumerate(
        st.session_state.chat_history
    ):

        with st.chat_message(
            "user"
        ):

            st.markdown(
                f"**{conversation['question']}**"
            )

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                conversation["answer"]
            )

            sources = conversation.get(
                "sources",
                [],
            )

            if sources:

                with st.expander(
                    f"🔎 Retrieved Sources · {len(sources)}"
                ):

                    for source_index, source in enumerate(
                        sources,
                        start=1,
                    ):

                        st.markdown(
                            f"**Passage {source_index}**"
                        )

                        st.write(
                            source["content"]
                        )

                        if source.get(
                            "document_name"
                        ):

                            st.caption(
                                "Source · "
                                f"{source['document_name']}"
                            )

                        if source_index < len(
                            sources
                        ):
                            st.divider()

        if (
            conversation_index
            < len(
                st.session_state.chat_history
            ) - 1
        ):
            st.divider()


# =========================================================
# SMART SUMMARY
# =========================================================

if workspace == "📝 Smart Summary":

    st.markdown(
        """
<div class="ll-section-kicker">
    AI-Powered Understanding
</div>

<div class="ll-section-title">
    Summarize your learning material
</div>

<div class="ll-section-description">
    Choose the level of detail you need and let LearnLens
    condense your uploaded material into a focused,
    study-friendly overview.
</div>
""",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("**Choose how detailed you want the summary to be**")

        summary_type = st.segmented_control(
            "Summary depth",
            ["⚡ Short", "📖 Medium", "🔎 Detailed"],
            default="📖 Medium",
            key="summary_depth_control",
            label_visibility="collapsed",
        )

        if summary_type is None:
            summary_type = "📖 Medium"

        summary_type = summary_type.split(" ", 1)[1]

        summary_descriptions = {
            "Short": "Quick revision · key ideas only · fastest to read",
            "Medium": "Balanced study notes · important concepts with context",
            "Detailed": "Deeper coverage · concepts, events, arguments and relationships",
        }

        st.caption(summary_descriptions[summary_type])

        generate_summary_clicked = st.button(
            "✨ Generate Summary",
            key="generate_summary_button",
            type="primary",
            use_container_width=True,
        )

    if generate_summary_clicked:

        with st.spinner(
            f"Creating your {summary_type.lower()} summary..."
        ):

            try:

                summary = generate_summary(
                    chunks,
                    summary_type,
                )

                st.divider()

                st.markdown(
                    f"""
<div class="ll-section-kicker">
    Generated Result
</div>

<div class="ll-section-title">
    {summary_type} Summary
</div>
""",
                    unsafe_allow_html=True,
                )

                with st.container(
                    border=True
                ):

                    st.markdown(
                        summary
                    )

            except Exception as error:

                st.error(
                    "Unable to generate summary: "
                    f"{error}"
                )


# =========================================================
# AI QUIZ
# =========================================================

if workspace == "🧠 AI Quiz":

    st.markdown(
        """
<div class="ll-section-kicker">
    Test Your Understanding
</div>

<div class="ll-section-title">
    Generate a practice quiz
</div>

<div class="ll-section-description">
    Create fresh multiple-choice questions from your uploaded
    learning material and instantly evaluate your understanding.
</div>
""",
        unsafe_allow_html=True,
    )

    quiz_col1, quiz_col2, quiz_col3 = (
        st.columns(
            [1, 1, 1]
        )
    )

    # -----------------------------------------------------
    # NUMBER OF QUESTIONS
    # -----------------------------------------------------

    with quiz_col1:

        num_questions = st.selectbox(
            "Questions",
            [
                3,
                5,
                10,
            ],
            key="num_questions",
        )

    # -----------------------------------------------------
    # DIFFICULTY
    # -----------------------------------------------------

    with quiz_col2:

        difficulty = st.selectbox(
            "Difficulty",
            [
                "Easy",
                "Medium",
                "Hard",
            ],
            key="quiz_difficulty",
        )

    # -----------------------------------------------------
    # GENERATE QUIZ
    # -----------------------------------------------------

    with quiz_col3:

        st.write("")
        st.write("")

        generate_quiz_clicked = st.button(
            "✨ Generate Quiz",
            key="generate_quiz_button",
            type="primary",
            use_container_width=True,
        )

    if generate_quiz_clicked:

        with st.spinner(
            f"Creating a {difficulty.lower()} quiz..."
        ):

            try:

                quiz = generate_quiz(
                    chunks,
                    num_questions,
                    difficulty,
                )

                if not quiz:

                    st.error(
                        "The AI could not generate a valid quiz. "
                        "Please try again."
                    )

                else:

                    st.session_state.quiz = quiz

                    # Clear previous answers.
                    for key in list(
                        st.session_state.keys()
                    ):

                        if key.startswith(
                            "quiz_answer_"
                        ):
                            del st.session_state[key]

                    # Remove previous result.
                    if (
                        "quiz_result"
                        in st.session_state
                    ):
                        del st.session_state[
                            "quiz_result"
                        ]

            except Exception as error:

                st.error(
                    "Unable to generate quiz: "
                    f"{error}"
                )

    # -----------------------------------------------------
    # DISPLAY QUIZ
    # -----------------------------------------------------

    if "quiz" in st.session_state:

        quiz = st.session_state.quiz

        st.divider()

        quiz_header_col, quiz_badge_col = (
            st.columns(
                [4, 1]
            )
        )

        with quiz_header_col:

            st.subheader(
                "Your Practice Quiz"
            )

            st.caption(
                "Choose one answer for every question "
                "before submitting."
            )

        with quiz_badge_col:

            st.metric(
                "Questions",
                len(quiz),
            )

        answers = []

        for index, question_data in enumerate(
            quiz
        ):

            with st.container(
                border=True
            ):

                st.caption(
                    f"QUESTION {index + 1} OF {len(quiz)}"
                )

                question_text = question_data.get(
                    "question",
                    "Question unavailable",
                )

                st.markdown(
                    f'<div class="ll-quiz-question">{question_text}</div>',
                    unsafe_allow_html=True,
                )

                options = question_data.get(
                    "options",
                    [],
                )

                if options:

                    answer = st.radio(
                        "Choose your answer",
                        options,
                        key=f"quiz_answer_{index}",
                        index=None,
                        label_visibility="collapsed",
                    )

                    answers.append(
                        answer
                    )

                else:

                    st.warning(
                        "No options are available "
                        "for this question."
                    )

                    answers.append(
                        None
                    )

        # -------------------------------------------------
        # SUBMIT QUIZ
        # -------------------------------------------------

        submit_col, submit_spacer = (
            st.columns(
                [1.4, 4.6]
            )
        )

        with submit_col:

            submit_clicked = st.button(
                "Submit Quiz",
                type="primary",
                key="submit_quiz_button",
                use_container_width=True,
            )

        if submit_clicked:

            unanswered = sum(
                answer is None
                for answer in answers
            )

            if unanswered > 0:

                st.warning(
                    f"You still have {unanswered} "
                    f"unanswered question"
                    f"{'s' if unanswered != 1 else ''}."
                )

            else:

                score = 0
                results = []

                for index, question_data in enumerate(
                    quiz
                ):

                    user_answer = answers[
                        index
                    ]

                    correct_answer = (
                        question_data.get(
                            "correct_answer"
                        )
                    )

                    is_correct = (
                        user_answer
                        == correct_answer
                    )

                    if is_correct:
                        score += 1

                    results.append(
                        {
                            "question":
                                question_data.get(
                                    "question"
                                ),
                            "user_answer":
                                user_answer,
                            "correct_answer":
                                correct_answer,
                            "is_correct":
                                is_correct,
                        }
                    )

                st.session_state.quiz_result = {
                    "score": score,
                    "results": results,
                }

    # -----------------------------------------------------
    # QUIZ RESULTS
    # -----------------------------------------------------

    if (
        "quiz" in st.session_state
        and
        "quiz_result" in st.session_state
    ):

        quiz = st.session_state.quiz

        result_data = (
            st.session_state.quiz_result
        )

        score = result_data[
            "score"
        ]

        results = result_data[
            "results"
        ]

        percentage = (
            score / len(quiz)
        ) * 100

        st.divider()

        result_col1, result_col2, result_col3 = (
            st.columns(3)
        )

        with result_col1:

            st.metric(
                "Score",
                f"{score}/{len(quiz)}",
            )

        with result_col2:

            st.metric(
                "Percentage",
                f"{percentage:.0f}%",
            )

        with result_col3:

            if percentage == 100:
                performance = "Excellent"

            elif percentage >= 60:
                performance = "Good"

            else:
                performance = "Keep Learning"

            st.metric(
                "Performance",
                performance,
            )

        if percentage == 100:

            st.success(
                "🏆 Excellent — perfect score!"
            )

        elif percentage >= 60:

            st.success(
                "👏 Good work! You have a solid "
                "understanding of the material."
            )

        else:

            st.info(
                "📚 Keep studying and try another quiz."
            )

        # -------------------------------------------------
        # ANSWER REVIEW
        # -------------------------------------------------

        with st.expander(
            "📋 Review Answers",
            expanded=True,
        ):

            for index, result in enumerate(
                results,
                start=1,
            ):

                st.markdown(
                    f"### Question {index}"
                )

                st.write(
                    result["question"]
                )

                if result[
                    "is_correct"
                ]:

                    st.success(
                        "✓ Correct"
                    )

                    st.write(
                        "**Your answer:** "
                        f"{result['user_answer']}"
                    )

                else:

                    st.error(
                        "✕ Incorrect"
                    )

                    st.write(
                        "**Your answer:** "
                        f"{result['user_answer']}"
                    )

                    st.write(
                        "**Correct answer:** "
                        f"{result['correct_answer']}"
                    )

                if index < len(
                    results
                ):
                    st.divider()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div class="ll-footer">
    &#10022; LearnLens AI
    &nbsp;·&nbsp;
    Retrieval-Augmented Learning Assistant
    &nbsp;·&nbsp;
    BGE + FAISS + Llama 3.1
</div>
""",
    unsafe_allow_html=True,
)