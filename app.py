import streamlit as st
import requests
import textwrap
import time

TRAKT_CLIENT_ID = "f85b06aee7a3b6d67e82526087422da3749e3ff0c1688b18fe39d54511cf1f1c"
HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": TRAKT_CLIENT_ID
}

mood_genre_map = {
    "Happy 😊": ("comedy", "Yayy! Deviii, something funny to keep the smiles going 😄"),
    "Sad 😢": ("drama", "Deviii, don’t worry, everything will be okay 💗"),
    "Excited 🚀": ("action", "Deviii, let’s keep that energy high with some thrills! ⚡"),
    "Romantic 💖": ("romance", "Deviii, love is in the air! 💕 Grab some tissues 😘"),
    "Adventurous 🏞️": ("adventure", "Deviii, let’s go exploring wild worlds 🌍✨"),
    "Chill 😌": ("documentary", "Deviii, time to relax and learn a thing or two ☕"),
    "Scared 😱": ("horror", "Deviii, brace yourself, it's about to get spooky 👻"),
    "Curious 🧠": ("mystery", "Deviii, let’s solve something intriguing 🔍🕵️‍♀️"),
    "Musical 🎶": ("music", "Deviii, sing along with your soul 🎤🎧"),
    "Dreamy 🌌": ("fantasy", "Deviii, let’s escape reality for a while 🌈🦄")
}

st.set_page_config(page_title="BingeBoo 🍿", layout="wide")
st.markdown("""
<style>
body, .stApp { background-color: #000000; color: #ffffff; }
.title-style { font-size: 2.5rem; font-weight: bold; color: #e50914; font-family: 'Segoe UI', sans-serif; }
.subtitle-style { font-size: 1.2rem; color: #cccccc; margin-bottom: 1rem; }
.poster-card {
    background-color: #121212; border-radius: 10px; padding: 1rem; margin: 1rem 0.5rem;
    width: 300px; display: inline-block; vertical-align: top;
}
.poster-card img { border-radius: 5px; width: 100%; }
.poster-title { font-size: 1.3rem; font-weight: bold; margin-top: 0.5rem; color: #ffffff; }
.poster-meta { font-size: 0.9rem; color: #999999; }
.poster-overview { font-size: 0.9rem; margin-top: 0.5rem; color: #cccccc; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "mood" not in st.session_state:
    st.session_state.mood = ""
if "genre" not in st.session_state:
    st.session_state.genre = ""
if "trigger" not in st.session_state:
    st.session_state.trigger = "mood"  # controls which dropdown just got changed

# --- Header ---
st.markdown("""<div class="title-style">BingeBoo 🍿 - Top TV Picks For The Week</div>""", unsafe_allow_html=True)
st.markdown("""<div class="subtitle-style">(Handpicked shows for Deviii, the binge queen 👸🙈)</div>""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([4, 1.5, 2, 1.5])
with col1:
    st.markdown("**Deviii, how’s your heart today? 🥹 Let BingeBoo AI serve you a genre you love**")

# --- Mood Select ---
moods = [""] + list(mood_genre_map.keys())
with col2:
    selected_mood = st.selectbox(
        "Mood",
        moods,
        index=moods.index(st.session_state.mood),
        key="mood_box",
        label_visibility="collapsed",
        on_change=lambda: (
            st.session_state.update({
                "mood": st.session_state.mood_box,
                "genre": "",
                "trigger": "mood"
            })
        )
    )

# --- Genre Select ---
with col3:
    st.markdown("**Or Deviii just pick your favorite genre 🍿💫**")

all_genres = [""] + [
    "action", "adventure", "animation", "anime", "comedy", "crime", "documentary",
    "drama", "family", "fantasy", "game-show", "history", "horror", "music",
    "mystery", "reality", "romance", "science-fiction", "soap", "talk-show",
    "thriller", "war", "western"
]
genre_names = [g.title() for g in all_genres]
with col4:
    selected_genre = st.selectbox(
        "Genre",
        genre_names,
        index=all_genres.index(st.session_state.genre),
        key="genre_box",
        label_visibility="collapsed",
        on_change=lambda: (
            st.session_state.update({
                "genre": genre_names.index(st.session_state.genre_box) and genre_names[genre_names.index(st.session_state.genre_box)].lower() or "",
                "mood": "",
                "trigger": "genre"
            })
        )
    )

# --- Determine Final Genre ---
final_genre = st.session_state.genre
custom_message = None
if st.session_state.trigger == "mood" and st.session_state.mood in mood_genre_map:
    final_genre, custom_message = mood_genre_map[st.session_state.mood]

# --- Fetch Shows ---
def safe_get(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=timeout)
            res.raise_for_status()
            return res
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

def wrap_text(text, width=80):
    return '\n'.join(textwrap.wrap(text or "No description available.", width=width))

def fetch_trending_shows(genre=None):
    url = "https://api.trakt.tv/shows/trending"
    if genre:
        url += f"?genres={genre}"
    res = safe_get(url)
    if not res:
        return []
    shows = res.json()[:10]
    full_data = []
    for entry in shows:
        show = entry.get("show", {})
        slug = show.get("ids", {}).get("slug")
        if slug:
            details_url = f"https://api.trakt.tv/shows/{slug}?extended=full"
            details_res = safe_get(details_url)
            full_data.append(details_res.json() if details_res else show)
        else:
            full_data.append(show)
    return full_data

def display_posters(shows):
    cols = st.columns(2)
    for i, show in enumerate(shows):
        with cols[i % 2]:
            st.markdown("<div class='poster-card'>", unsafe_allow_html=True)
            image_url = show.get("images", {}).get("poster", {}).get("thumb") or \
                        "https://via.placeholder.com/300x450.png?text=No+Image"
            st.image(image_url, use_container_width=True)
            title = show.get("title", "Untitled")
            year = show.get("year", "")
            rating = show.get("rating", "N/A")
            overview = wrap_text(show.get("overview"), 120)
            st.markdown(f"<div class='poster-title'>{title} ({year})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='poster-meta'>⭐ {rating:.1f}</div>" if isinstance(rating, float) else "<div class='poster-meta'>⭐ N/A</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='poster-overview'>{overview}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- Render Show Results ---
if final_genre:
    message = custom_message if custom_message else f"✨ Binging top {final_genre.title()} shows for you..."
    with st.spinner(message):
        display_posters(fetch_trending_shows(final_genre))
