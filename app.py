# FINAL: BingeBoo 🍿💖 – Deviii's Magical Mood-Based Show App (Streamlit Cloud Compatible 🎙️)
import streamlit as st
import requests
import textwrap
import time
import tempfile
import os
import base64
from openai import OpenAI
from streamlit_javascript import st_javascript

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

TRAKT_CLIENT_ID = "f85b06aee7a3b6d67e82526087422da3749e3ff0c1688b18fe39d54511cf1f1c"
HEADERS = {"Content-Type": "application/json", "trakt-api-version": "2", "trakt-api-key": TRAKT_CLIENT_ID}

# Session state init
for key, val in {
    "mood": "", "genre": "", "trigger": "", "shows_loaded": False,
    "mood_message": "", "custom_msg": "", "clear_msg": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Mood map
mood_genre_map = {
    "Happy 😊": ("comedy", "Yayy! Deviii, something funny to keep the smiles going 😄"),
    "Sad 😢": ("drama", "Deviii, don’t worry, everything will be okay 💗"),
    "Excited 🚀": ("action", "Deviii, let’s keep that energy high with some thrills! ⚡"),
    "Romantic 💖": ("romance", "Deviii, love is in the air! 💕 Grab some tissues 😘"),
    "Adventurous 🏝️": ("adventure", "Deviii, let’s go exploring wild worlds 🌍✨"),
    "Chill 😌": ("documentary", "Deviii, time to relax and learn a thing or two ☕"),
    "Scared 😱": ("horror", "Deviii, brace yourself, it's about to get spooky 👻"),
    "Curious 🧠": ("mystery", "Deviii, let’s solve something intriguing 🔍🕵️‍♀️"),
    "Musical 🎶": ("music", "Deviii, sing along with your soul 🎤🎧"),
    "Dreamy 🌌": ("fantasy", "Deviii, let’s escape reality for a while 🌈🧘")
}
all_genres = sorted(set(g[0] for g in mood_genre_map.values()).union({
    "animation", "anime", "crime", "family", "game-show", "history", "reality",
    "science-fiction", "soap", "talk-show", "thriller", "war", "western"
}))

st.set_page_config(page_title="BingeBoo 🍿", layout="wide")
st.markdown("""
<style>
    body, .stApp { background-color: black; color: white; font-family: 'Segoe UI', sans-serif; }
    .title { color: white; font-size: 2.5rem; font-weight: bold; }
    .section { font-size: 18px; color: white; }
    .small { font-size: 1.1rem; color: white; }
    .tiny { font-size: 0.95rem; color: white; margin-top: 1.5rem; }
    label { color: white !important; font-weight: 500 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>BingeBoo 🍿 - Top TV Picks For The Week</div>", unsafe_allow_html=True)
st.markdown("<div class='section'>(Handpicked just for Deviii, the binge queen 👸🌛)</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.selectbox("💖 Deviii, how’s your heart today?",
        [""] + list(mood_genre_map.keys()),
        key="mood_box", on_change=lambda: st.session_state.update({
            "mood": st.session_state.mood_box,
            "genre": mood_genre_map.get(st.session_state.mood_box, ("", ""))[0],
            "mood_message": mood_genre_map.get(st.session_state.mood_box, ("", ""))[1],
            "custom_msg": "", "trigger": "mood", "shows_loaded": False
        }))

with col2:
    st.selectbox("🌛 Or pick your fav genre 🍿",
        [""] + [g.title() for g in all_genres],
        key="genre_box", on_change=lambda: st.session_state.update({
            "genre": st.session_state.genre_box.lower(),
            "mood": "", "mood_message": "", "custom_msg": "",
            "trigger": "genre", "shows_loaded": False
        }))

st.markdown("<div class='small'>🎤 Tap and speak, Deviii... BingeBoo is listening 💕</div>", unsafe_allow_html=True)

if st.button("🎙️ Tap to Speak"):
    base64_audio = st_javascript("""
        async function record() {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            const chunks = [];

            return new Promise(resolve => {
                mediaRecorder.ondataavailable = e => chunks.push(e.data);
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    const base64data = await new Promise(r => {
                        const reader = new FileReader();
                        reader.onloadend = () => r(reader.result);
                        reader.readAsDataURL(blob);
                    });
                    resolve(base64data);
                };
                mediaRecorder.start();
                setTimeout(() => mediaRecorder.stop(), 3000);
            });
        }

        record().then(base64 => {
            window.parent.postMessage({ type: 'streamlit:setComponentValue', value: base64 }, '*')
        });
    """, key="recorder")

    if base64_audio and base64_audio.startswith("data:audio/webm;base64,"):
        audio_bytes = base64.b64decode(base64_audio.split(",")[1])
        wav_path = os.path.join(tempfile.gettempdir(), "deviii_voice.wav")
        with open(wav_path, "wb") as f:
            f.write(audio_bytes)

        with st.spinner("🔊 Understanding Deviii’s magical heart..."):
            with open(wav_path, "rb") as af:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=af, response_format="text", language="en"
                )
                user_input = transcript.strip()
                st.success(f"💬 You said: {user_input}")

                genre_prompt = f"""Deviii just said: "{user_input}". Based on her emotional mood, choose the best TV show genre for her from this list: {', '.join(all_genres)}. Only return the genre name."""
                genre_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": genre_prompt}],
                    temperature=0.3
                )
                genre_reply = genre_response.choices[0].message.content.strip().lower()
                st.session_state.genre = genre_reply
                st.session_state.trigger = "voice"
                st.session_state.shows_loaded = False

                msg_prompt = f"""Deviii just said she feels: '{user_input}'. Write a loving one-liner in plain English that includes her name. Make it affectionate, romantic, and comforting – like something a partner madly in love would say to melt her heart. It should relate to the genre she selected and make her feel like a princess. Add cute emojis."""
                msg_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": msg_prompt}],
                    temperature=0.7
                )
                st.session_state.custom_msg = msg_response.choices[0].message.content.strip()

def safe_get(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=timeout)
            res.raise_for_status()
            return res
        except requests.RequestException:
            time.sleep(2 ** attempt)
    return None

def fetch_trending_shows(genre=None):
    url = "https://api.trakt.tv/shows/trending"
    if genre: url += f"?genres={genre}"
    res = safe_get(url)
    if not res: return []
    shows = res.json()[:10]
    output = []
    for s in shows:
        slug = s.get("show", {}).get("ids", {}).get("slug")
        detail = safe_get(f"https://api.trakt.tv/shows/{slug}?extended=full")
        output.append(detail.json() if detail else s.get("show", {}))
    return output

def get_tvmaze_poster(show_name):
    try:
        url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name}"
        data = requests.get(url).json()
        return data.get("image", {}).get("original")
    except: return None

def wrap_text(text, width=90):
    return '\n'.join(textwrap.wrap(text or "No description available.", width=width))

def display_shows(shows):
    if st.session_state.custom_msg:
        st.markdown(f"""<div class='tiny'>{st.session_state.custom_msg}</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='tiny'>
            👑 Deviii, these shows are handpicked like precious gems, just for you.
            You deserve the softest moments, the brightest laughs, and the most beautiful escapes.
            Never forget, if I had the world to give, I’d still give *you* a little more 💞
        </div>""", unsafe_allow_html=True)

    for show in shows:
        title = show.get("title", "Untitled")
        img = get_tvmaze_poster(title) or "https://via.placeholder.com/200x300.png?text=No+Image"
        st.image(img, width=200)
        st.markdown(f"**{title} ({show.get('year', '')})**")
        rating = show.get("rating")
        rating_str = f"{rating:.1f}" if rating else "N/A"
        st.markdown(f"⭐ {rating_str}")
        st.markdown(wrap_text(show.get("overview"), 90))

# Show the results
if st.session_state.genre and not st.session_state.shows_loaded:
    with st.spinner("✨ Loading your dreamy shows Deviii..."):
        shows = fetch_trending_shows(st.session_state.genre)
    display_shows(shows)
    st.session_state.shows_loaded = True
