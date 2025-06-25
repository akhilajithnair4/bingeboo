# 👇 Paste this entire code in your main file

import streamlit as st 
import requests
import textwrap
import time
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

TRAKT_CLIENT_ID = "f85b06aee7a3b6d67e82526087422da3749e3ff0c1688b18fe39d54511cf1f1c"
HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": TRAKT_CLIENT_ID
}

for key, val in {
    "mood": "", "genre": "", "trigger": "", "shows_loaded": False,
    "mood_message": "", "custom_msg": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

mood_genre_map = {
    "Happy 😊": ("comedy", "Yayy! Deviii, something funny to keep the smiles going 😄"),
    "Sad 😢": ("drama", "Deviii, don't worry, everything will be okay 💗"),
    "Excited 🚀": ("action", "Deviii, let's keep that energy high with some thrills! ⚡"),
    "Romantic 💖": ("romance", "Deviii, love is in the air! 💕 Grab some tissues 😘"),
    "Adventurous 🏞️": ("adventure", "Deviii, let's go exploring wild worlds 🌍✨"),
    "Chill 😌": ("documentary", "Deviii, time to relax and learn a thing or two ☕"),
    "Scared 😱": ("horror", "Deviii, brace yourself, it's about to get spooky 👻"),
    "Curious 🧠": ("mystery", "Deviii, let's solve something intriguing 🔍🕵️‍♀️"),
    "Musical 🎶": ("music", "Deviii, sing along with your soul 🎤🎧"),
    "Dreamy 🌌": ("fantasy", "Deviii, let's escape reality for a while 🌈💄")
}

all_genres = sorted(set(g[0] for g in mood_genre_map.values()).union({
    "animation", "anime", "crime", "family", "game-show", "history", "reality",
    "science-fiction", "soap", "talk-show", "thriller", "war", "western"
}))

st.set_page_config(page_title="BingeBoo 🍿", layout="wide")

st.markdown("""<style>
body, .stApp { background-color: #000; color: #fff; font-family: 'Segoe UI', sans-serif; }
.title-style { font-size: 2.5rem; font-weight: bold; color: #e50914; text-align: center; margin-bottom: 0.5rem; }
.subtitle-style { font-size: 1.2rem; color: #cccccc; text-align: center; margin-bottom: 2rem; }
.poster-card { display: flex; gap: 1.5rem; padding: 1.5rem 0; border-bottom: 1px solid #222; }
.poster-title { font-size: 1.3rem; font-weight: bold; margin-top: 0.5rem; color: #ffffff; }
.poster-meta { font-size: 1rem; color: #ffb800; margin: 0.5rem 0; }
.poster-overview { font-size: 0.95rem; margin-top: 1rem; color: #cccccc; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
label { color: white !important; font-weight: 600 !important; font-size: 1.1rem !important; }
.stButton > button {
    background-color: #ffe6f0; color: #e50914; font-weight: bold;
    font-size: 1.05rem; padding: 0.6rem 1.4rem; border-radius: 14px;
    border: 2px solid #ff4da6; box-shadow: 0 0 12px #ff99cc, 0 0 20px #ff4da6;
    transition: all 0.3s ease-in-out; font-family: 'Segoe UI', cursive;
    text-shadow: 0 0 3px white;
}
.stButton > button:hover {
    background-color: #ffccdf; color: #c70039; transform: scale(1.05);
    box-shadow: 0 0 15px #ff4da6, 0 0 25px #ffc0cb; cursor: pointer;
}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="title-style">BingeBoo 🍿</div>', unsafe_allow_html=True)
st.markdown('<div class="title-style">Top TV Picks For The Week</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-style">(Handpicked shows for Deviii, the binge queen 👸✨)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**💖 Deviii, what little feeling is dancing in your heart today?**")
    selected_mood = st.selectbox("", [""] + list(mood_genre_map.keys()),
        key="mood_selector",
        on_change=lambda: st.session_state.update({
            "mood": st.session_state.mood_selector,
            "genre": mood_genre_map.get(st.session_state.mood_selector, ("", ""))[0],
            "mood_message": mood_genre_map.get(st.session_state.mood_selector, ("", ""))[1],
            "custom_msg": "",
            "trigger": "mood",
            "shows_loaded": False
        })
    )

with col2:
    st.markdown("**🍿 Or Deviii pick your favorite genre:**")
    selected_genre = st.selectbox("", [""] + [g.title() for g in all_genres],
        key="genre_selector",
        on_change=lambda: st.session_state.update({
            "genre": st.session_state.genre_selector.lower() if st.session_state.genre_selector else "",
            "mood": "",
            "mood_message": "",
            "custom_msg": "",
            "trigger": "genre",
            "shows_loaded": False
        })
    )

voice_text = st.text_input("✨ Deviii Just whisper it here, and BingeBoo AI will weave a dreamy watchlist only for you, princess 🌙", 
    placeholder="e.g., 'I'm feeling romantic today' or 'I want something funny'")

if st.button("💖 Process My Heart") and voice_text:
    with st.spinner("🎧 BingeBoo is understanding your heart, Deviii..."):
        try:
            genre_prompt = f"""
            Deviii said: "{voice_text}"
            From these genres: {', '.join(all_genres)}
            Which genre best matches her mood or request? Return only the genre name in lowercase.
            """
            genre_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": genre_prompt}],
                max_tokens=50,
                temperature=0.3
            )
            detected_genre = genre_response.choices[0].message.content.strip().lower()
            if detected_genre in all_genres:
                st.session_state.genre = detected_genre
                st.session_state.trigger = "voice"
                st.session_state.shows_loaded = False
                msg_prompt = f"""
                Deviii said she feels: '{voice_text}'
                Write a loving, encouraging message for her (max 50 words). 
                Make it affectionate and relate to the {detected_genre} genre.
                Include her name 'Deviii' and cute emojis. Also very lightly just mention shortly since that is your mood Binge Boo AI is recommending these shows.
                Also she should feel pampered and like a princess.
                """
                msg_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": msg_prompt}],
                    max_tokens=100,
                    temperature=0.7
                )
                st.session_state.custom_msg = msg_response.choices[0].message.content.strip()
                st.rerun()
            else:
                st.warning("😅 Sorry Deviii, couldn't detect a clear genre. Try the dropdown instead!")
        except Exception as e:
            st.error(f"❌ Error processing your mood: {str(e)}")

def safe_get(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                st.error(f"API request failed: {e}")
                return None

def fetch_trending_shows(genre=None):
    url = "https://api.trakt.tv/shows/trending"
    if genre:
        url += f"?genres={genre}"
    response = safe_get(url)
    if not response:
        return []
    shows_data = response.json()[:10]
    full_shows = []
    for entry in shows_data:
        show = entry.get("show", {})
        slug = show.get("ids", {}).get("slug")
        if slug:
            details_url = f"https://api.trakt.tv/shows/{slug}?extended=full"
            details_response = safe_get(details_url)
            if details_response:
                full_shows.append(details_response.json())
            else:
                full_shows.append(show)
        else:
            full_shows.append(show)
    return full_shows

def get_tvmaze_poster(show_name):
    try:
        url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name.replace(' ', '%20')}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        image_data = data.get("image", {})
        return image_data.get("original") or image_data.get("medium")
    except requests.RequestException:
        return None

def wrap_text(text, width=90):
    if not text:
        return "No description available."
    return '\n'.join(textwrap.wrap(text, width=width))

def display_shows(shows):
    if not shows:
        st.warning("No shows found. Please try a different genre.")
        return
    if st.session_state.custom_msg:
        st.markdown(f"<p style='color:white; text-align:center; font-size:1.1rem;'>{st.session_state.custom_msg}</p>", unsafe_allow_html=True)
   
    for show in shows:
        title = show.get("title", "Untitled")
        year = show.get("year", "N/A")
        rating = show.get("rating") or 0.0
        overview = wrap_text(show.get("overview", "No description available."))
        poster_url = get_tvmaze_poster(title) or "https://via.placeholder.com/150x225.png?text=No+Image"

        st.markdown(f"""
        <div class="poster-card">
            <div>
                <img src="{poster_url}" style="width:150px; height:225px; object-fit:cover; border-radius:8px;">
            </div>
            <div>
                <div class="poster-title">{title} ({year})</div>
                <div class="poster-meta">⭐ {rating:.1f}/10</div>
                <div class="poster-overview">{overview}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ✅ Corrected: Loading message based on mood dictionary
# ✅ Corrected: Loading message logic
current_genre = st.session_state.genre
if current_genre and not st.session_state.shows_loaded:
    with st.spinner(
        "✨ Just a sec Deviii... your dreamy shows are loading ✨" if st.session_state.trigger == "voice"
        else st.session_state.mood_message if st.session_state.trigger == "mood"
        else f"✨ Binginggg {current_genre.title()} shows for you, Deviii..."
    ):
        shows = fetch_trending_shows(current_genre)
        display_shows(shows)
        st.session_state.shows_loaded = True


st.markdown("---")
st.markdown('<div style="text-align: center; color: #666; margin-top: 2rem;">Made with 💖 for Deviii | Powered by Trakt & TVMaze APIs</div>', unsafe_allow_html=True)
