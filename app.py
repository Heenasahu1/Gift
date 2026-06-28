"""
A Little Something, Just For You — a guarded digital birthday gift.

Flow:
  landing -> name verification -> "are you ready?" -> 6-question quiz
  (each correct answer reveals one tile of a hidden photo) -> full reveal
  + personalized message -> the actual gift (a PDF), viewed in-app.

Run with:  streamlit run app.py
"""

import base64
import random
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------
# Paths & page config
# --------------------------------------------------------------------------
ASSETS = Path(__file__).parent / "assets"

st.set_page_config(
    page_title="Happy Birthday!!",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GRID_COLS, GRID_ROWS = 3, 2  # 6 tiles -> matches the 6 correct answers needed

# --------------------------------------------------------------------------
# Loaders (cached so files are only read once per session)
# --------------------------------------------------------------------------
@st.cache_data
def get_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


@st.cache_data
def load_names() -> set:
    text = (ASSETS / "Name.txt").read_text(encoding="utf-8", errors="ignore")
    return {line.strip().lower() for line in text.splitlines() if line.strip()}


@st.cache_data
def load_questions() -> list:
    df = pd.read_excel(ASSETS / "Question.xlsx")
    df = df.dropna(subset=["Question"]).reset_index(drop=True)
    answer_cols = [c for c in df.columns if str(c).lower().startswith("answer")]
    records = []
    for _, row in df.iterrows():
        accepted = [
            str(row[c]).strip().lower()
            for c in answer_cols
            if pd.notna(row[c]) and str(row[c]).strip()
        ]
        records.append({"question": str(row["Question"]).strip(), "accepted": accepted})
    return records


@st.cache_data
def load_message() -> str:
    return (ASSETS / "message.txt").read_text(encoding="utf-8", errors="ignore").strip()


WALLPAPER_B64 = get_base64(ASSETS / "wallpaper.webp")
PUZZLE_B64 = get_base64(ASSETS / "puzzle.jpeg")
PDF_B64 = get_base64(ASSETS / "gift.pdf")
NAMES = load_names()
QUESTIONS = load_questions()
FINAL_MESSAGE = load_message()

# --------------------------------------------------------------------------
# Fun feedback lines
# --------------------------------------------------------------------------
CORRECT_MESSAGES = [
    "Aww! 😍 Tumko yaad tha, {name}!",
    "Kya baat hai {name}!.",
    "Wah wah! 👏 Topper of the 'Knowing Me' exam!",
    "Ikzactly.",
    "Haa ye to pata hona hi chahiye tha tumko.",
    "Ye hui na baat. 📈❤️",
    "Itna kaise dhyaan se meri baatein yaad rehti hai tumhe! 🥰",
    "Iske liye to tumko bahot sare hugs milne chahiye.",
]

WRONG_MESSAGES = [
    "Galat! 😤 Itna bhi nahi pata mere baare mein?",
    "Nope! 🙈",
    "Wrong answer! Koi dusra question try kro. 🥲",
    "Try again, yaad kro {name}! 💭",
    "Hmm, ye kaise galat hua tumse! 🔍",
    "Chalo chhodo, tumse nahi ho payega shayad",
    "Tera dhyan kidhar hai, ye tera answer galat hai",
    "Common yarr, itne bhi hard questions nahi diye h maine. 😏",
]

# --------------------------------------------------------------------------
# Global styling
# --------------------------------------------------------------------------
def inject_css():
    st.markdown(
        f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,600&family=Quicksand:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{ font-family: 'Quicksand', sans-serif; }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    .stApp {{
        background-image: linear-gradient(180deg, rgba(8,18,22,0.55), rgba(8,18,22,0.68)),
                           url("data:image/webp;base64,{WALLPAPER_B64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    .hero-title {{
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        color: #fffaf0;
        text-shadow: 0 4px 18px rgba(0,0,0,0.55);
        text-align: center;
        letter-spacing: 0.3px;
    }}

    .sub-text {{
        text-align: center;
        color: #fffaf0;
        font-size: 1.05rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.55);
        margin-bottom: 1.1rem;
    }}

    .gift-emoji {{
        text-align: center;
        font-size: 5.5rem;
        animation: bounce 2.2s infinite ease-in-out;
        filter: drop-shadow(0 10px 18px rgba(0,0,0,0.45));
    }}
    @keyframes bounce {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-14px); }}
    }}

    .glass-card {{
        background: rgba(255, 252, 245, 0.92);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 22px;
        padding: 1.8rem 2.1rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
        color: #1b2a2e;
    }}

    div[data-testid="stForm"] {{
        background: rgba(255, 252, 245, 0.92);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 22px;
        padding: 1.6rem 1.9rem 0.6rem 1.9rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }}

    .feedback-banner {{
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        font-weight: 600;
        text-align: center;
        padding: 0.8rem 1.1rem;
        border-radius: 14px;
        margin-bottom: 1rem;
    }}
    .feedback-correct {{
        background: rgba(125, 191, 132, 0.28);
        color: #F8F8F8;
        border: 1px solid rgba(58, 138, 65, 0.45);
    }}
    .feedback-wrong {{
        background: rgba(232, 167, 152, 0.32);
        color: #F8F8F8;
        border: 1px solid rgba(196, 87, 60, 0.45);
    }}

    div.stButton > button {{
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        border-radius: 999px;
        padding: 0.55rem 1.6rem;
        border: none;
        background: linear-gradient(135deg, #d4af37, #b8860b);
        color: #fffdf6;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 24px rgba(0,0,0,0.38);
    }}
    div[data-testid="stFormSubmitButton"] > button {{
        width: 100%;
        font-family: 'Quicksand', sans-serif;
        font-weight: 700;
        border-radius: 999px;
        border: none;
        background: linear-gradient(135deg, #d4af37, #b8860b);
        color: #fffdf6;
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    }}

    .puzzle-wrap {{
        position: relative;
        width: 100%;
        aspect-ratio: 3 / 4;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 14px 40px rgba(0,0,0,0.45);
        border: 4px solid rgba(255,250,240,0.85);
    }}
    .puzzle-blur {{
        position: absolute; inset: 0;
        background-image: url("data:image/jpeg;base64,{PUZZLE_B64}");
        background-size: cover;
        background-position: center;
        filter: blur(22px) brightness(0.85) saturate(0.9);
        transform: scale(1.12);
    }}
    .puzzle-grid {{
        position: absolute; inset: 0;
        display: grid;
        grid-template-columns: repeat({GRID_COLS}, 1fr);
        grid-template-rows: repeat({GRID_ROWS}, 1fr);
    }}
    .puzzle-tile {{
        background-image: url("data:image/jpeg;base64,{PUZZLE_B64}");
        opacity: 0;
        transform: scale(1.05);
        transition: opacity 1.1s ease, transform 1.1s ease;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .puzzle-tile.revealed {{
        opacity: 1;
        transform: scale(1);
    }}

    .progress-track {{
        width: 100%;
        height: 10px;
        border-radius: 999px;
        background: rgba(255,255,255,0.3);
        overflow: hidden;
        margin-top: 0.7rem;
    }}
    .progress-fill {{
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #d4af37, #f3d27a);
        transition: width 0.8s ease;
    }}
    .progress-label {{
        text-align: center;
        color: #fffaf0;
        font-weight: 600;
        margin-top: 0.5rem;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------
def init_state():
    defaults = {
        "stage": "landing",
        "verified_name": None,
        "question_pool": [],
        "current_q": None,
        "correct_count": 0,
        "reveal_order": [],
        "revealed_tiles": set(),
        "feedback": None,
        "feedback_type": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def start_quiz():
    st.session_state.question_pool = list(range(len(QUESTIONS)))
    st.session_state.current_q = random.choice(st.session_state.question_pool)
    st.session_state.correct_count = 0
    st.session_state.revealed_tiles = set()
    st.session_state.reveal_order = random.sample(
        range(GRID_COLS * GRID_ROWS), GRID_COLS * GRID_ROWS
    )
    st.session_state.feedback = None
    st.session_state.feedback_type = None
    st.session_state.stage = "quiz"


def handle_answer(raw_answer: str):
    q = QUESTIONS[st.session_state.current_q]
    cleaned = raw_answer.strip().lower()
    name = st.session_state.verified_name

    if cleaned and cleaned in q["accepted"]:
        st.session_state.correct_count += 1
        if st.session_state.current_q in st.session_state.question_pool:
            st.session_state.question_pool.remove(st.session_state.current_q)

        next_tile_slot = len(st.session_state.revealed_tiles)
        if next_tile_slot < len(st.session_state.reveal_order):
            st.session_state.revealed_tiles.add(
                st.session_state.reveal_order[next_tile_slot]
            )

        st.session_state.feedback = random.choice(CORRECT_MESSAGES).format(name=name)
        st.session_state.feedback_type = "correct"

        if st.session_state.correct_count >= 6 or not st.session_state.question_pool:
            st.session_state.stage = "complete"
        else:
            st.session_state.current_q = random.choice(st.session_state.question_pool)
    else:
        st.session_state.feedback = random.choice(WRONG_MESSAGES).format(name=name)
        st.session_state.feedback_type = "wrong"
        if st.session_state.question_pool:
            st.session_state.current_q = random.choice(st.session_state.question_pool)


# --------------------------------------------------------------------------
# Puzzle renderer (CSS grid-of-tiles trick over a blurred base image)
# --------------------------------------------------------------------------
def render_puzzle(revealed_set: set):
    tiles_html = ""
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            idx = r * GRID_COLS + c
            bg_x = 0 if GRID_COLS == 1 else (c / (GRID_COLS - 1)) * 100
            bg_y = 0 if GRID_ROWS == 1 else (r / (GRID_ROWS - 1)) * 100
            cls = "revealed" if idx in revealed_set else ""
            tiles_html += (
                f'<div class="puzzle-tile {cls}" '
                f'style="background-size:{GRID_COLS * 100}% {GRID_ROWS * 100}%; '
                f'background-position:{bg_x}% {bg_y}%;"></div>'
            )

    st.markdown(
        f"""
        <div class="puzzle-wrap">
            <div class="puzzle-blur"></div>
            <div class="puzzle-grid">{tiles_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Stages
# --------------------------------------------------------------------------
def stage_landing():
    st.markdown("<div style='height:5vh'></div>", unsafe_allow_html=True)
    col = st.columns([1, 1.1, 1])[1]
    with col:
        st.markdown("<div class='gift-emoji'>🎁</div>", unsafe_allow_html=True)
        st.markdown(
            "<h1 class='hero-title'>A Little Something, Just For You</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='sub-text'>This gift is for a very special person "
            "Are you the one? 👀</p>",
            unsafe_allow_html=True,
        )
        with st.form("name_form"):
            name_input = st.text_input(
                "Your name",
                placeholder="Type your name here...",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Unlock 🔓")

        if submitted:
            if name_input.strip().lower() in NAMES:
                st.session_state.verified_name = name_input.strip()
                st.session_state.stage = "ready"
                st.rerun()
            else:
                st.warning(
                    "Try again?"
                    "Khud ka naam to sahi likho"
                    "I think I call you something else"
                )


def stage_ready():
    col = st.columns([1, 1.1, 1])[1]
    with col:
        st.markdown(
            f"<h1 class='hero-title'>Hi {st.session_state.verified_name} 💛</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='sub-text'>Tumhare gift tak pahuchne k liye thoda wait krna padega. "
            "This will be easy for you. To shuru kare?</p>",
            unsafe_allow_html=True,
        )
        with st.form("ready_form"):
            st.markdown(
                "<p style='text-align:center; margin:0 0 0.6rem 0; "
                "color:#1b2a2e; font-weight:600;'>I want 6 correct answers to "
                "unlock a special birthday wish & your gift.</p>",
                unsafe_allow_html=True,
            )
            go = st.form_submit_button("Chalo, chalo!")
        if go:
            start_quiz()
            st.rerun()


def stage_quiz():
    left, right = st.columns([1.1, 1], gap="large")

    with right:
        render_puzzle(st.session_state.revealed_tiles)
        pct = int(len(st.session_state.revealed_tiles) / 6 * 100)
        st.markdown(
            f"""
            <div class="progress-track"><div class="progress-fill"
                style="width:{pct}%;"></div></div>
            <p class="progress-label">{len(st.session_state.revealed_tiles)} / 6
                pieces unlocked</p>
            """,
            unsafe_allow_html=True,
        )

    with left:
        st.markdown(
            f"<h2 class='hero-title' style='font-size:1.7rem;'>Sab sawaal sahi sahi answer karne hai "
            f"{st.session_state.verified_name} 💭</h2>",
            unsafe_allow_html=True,
        )

        if st.session_state.feedback:
            cls = (
                "feedback-correct"
                if st.session_state.feedback_type == "correct"
                else "feedback-wrong"
            )
            st.markdown(
                f"<div class='feedback-banner {cls}'>{st.session_state.feedback}</div>",
                unsafe_allow_html=True,
            )

        q = QUESTIONS[st.session_state.current_q]
        with st.form("quiz_form", clear_on_submit=True):
            st.markdown(
                f"<p style='font-size:1.15rem; font-weight:700; color:#1b2a2e;'>"
                f"{q['question']}</p>",
                unsafe_allow_html=True,
            )
            answer = st.text_input(
                "Your answer",
                placeholder="Type your answer...",
                label_visibility="collapsed",
            )
            go = st.form_submit_button("Submit Answer 💌")

        if go:
            handle_answer(answer)
            st.rerun()


def stage_complete():
    st.balloons()
    col = st.columns([1, 1.3, 1])[1]
    with col:
        st.markdown(
            "<h1 class='hero-title'>From Sunrise to Sunset, Thank You for being there with me :) </h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""<img src="data:image/jpeg;base64,{PUZZLE_B64}"
                 style="width:100%; border-radius:20px;
                 box-shadow:0 14px 40px rgba(0,0,0,0.45);
                 border:4px solid rgba(255,250,240,0.85);">""",
            unsafe_allow_html=True,
        )
        personalized = FINAL_MESSAGE.replace("{name}", st.session_state.verified_name)
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:1.4rem; text-align:center;
                font-family:'Playfair Display', serif; font-size:1.25rem;
                line-height:1.6;">{personalized}</div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Open Your Gift 🎁", use_container_width=True):
            st.session_state.stage = "gift"
            st.rerun()


def stage_gift():
    st.markdown(
        f"<h1 class='hero-title'>For You, {st.session_state.verified_name} 🎁</h1>",
        unsafe_allow_html=True,
    )

    with open(ASSETS / "gift.pdf", "rb") as pdf_file:
        st.download_button(
            label="🎁 Open Your Gift",
            data=pdf_file,
            file_name="gift.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    init_state()
    inject_css()

    stage_router = {
        "landing": stage_landing,
        "ready": stage_ready,
        "quiz": stage_quiz,
        "complete": stage_complete,
        "gift": stage_gift,
    }
    stage_router[st.session_state.stage]()


if __name__ == "__main__":
    main()
