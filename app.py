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

# ---------- Page Config ----------
st.set_page_config(page_title="BingeBoo 🍿", layout="wide")

# ---------- Styles ----------
st.markdown("""
<style>
body, .stApp {
    background-color: #000000;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}
.title-style {
    font-size: 2.2rem;
    font-weight: bold;
    color: #e50914;
}
.subtitle-style {
    font-size: 1rem;
    color: #cccccc;
    margin-bottom: 1rem;
}
.poster-card {
    background-color: #121212;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    width: 100%;
}
.poster-card img {
    border-radius: 5px;
    width: 10%;
    max-height:50px;
    object-fit: cover;
}
.poster-title {
    font-size: 1rem;
    font-weight: bold;
    margin-top: 0.5rem;
    color: #ffffff;
}
.poster-meta {
    font-size: 0.8rem;
    color: #999999;
}
.poster-overview {
    font-size: 0.85rem;
    margin-top: 0.5rem;
    color: #cccccc;
}
@media (max-width: 768px) {
    .poster-card img { max-height: 180px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Session ----------
if "mood" not in st.session_state:
    st.session_state.mood = ""
if "genre" not in st.session_state:
    st.session_state.genre = ""
if "trigger" not in st.session_state:
    st.session_state.trigger = "mood"

# ---------- Header ----------
st.markdown("""<div class="title-style">BingeBoo 🍿 - Top TV Picks For The Week</div>""", unsafe_allow_html=True)
st.markdown("""<div class="subtitle-style">(Handpicked shows for Deviii, the binge queen 👸🙈)</div>""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([4, 1.5, 2, 1.5])
with col1:
    st.markdown("**Deviii, how’s your heart today? 🥹 Let BingeBoo AI serve you a genre you love**")

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

# ---------- Determine Genre ----------
final_genre = st.session_state.genre
custom_message = None
if st.session_state.trigger == "mood" and st.session_state.mood in mood_genre_map:
    final_genre, custom_message = mood_genre_map[st.session_state.mood]

# ---------- API Helpers ----------
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

def get_tvmaze_poster(show_name):
    try:
        url = f"https://api.tvmaze.com/singlesearch/shows?q={show_name}"
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return data.get("image", {}).get("original", None)
    except requests.RequestException:
        return None

# ---------- Display Cards ----------
def display_posters(shows):
    for show in shows:
        st.markdown("<div class='poster-card'>", unsafe_allow_html=True)
        title = show.get("title", "Untitled")
        year = show.get("year", "")
        rating = show.get("rating", "N/A")
        overview = wrap_text(show.get("overview"), 90)
        image_url = get_tvmaze_poster(title) or "https://via.placeholder.com/200x300.png?text=No+Image"
        st.image(image_url,width=200)
        st.markdown(f"<div class='poster-title'>{title} ({year})</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='poster-meta'>⭐ {rating:.1f}</div>" if isinstance(rating, float) else "<div class='poster-meta'>⭐ N/A</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='poster-overview'>{overview}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- Show Results ----------
if final_genre:
    message = custom_message if custom_message else f"✨ Binging top {final_genre.title()} shows for you Deviii..."
    with st.spinner(message):
        display_posters(fetch_trending_shows(final_genre))
