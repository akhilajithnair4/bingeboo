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
    "Happy 😊": ("comedy", "Yayy!Deviii Something funny to keep the smiles going 😄"),
    "Sad 😢": ("drama", "Deviii, don’t worry, everything will be okay 💗"),
    "Excited 🚀": ("action", "Deviii Let’s keep that energy high with some thrills! ⚡"),
    "Romantic 💖": ("romance", "Deviii Love is in the air! 💕 Grab some tissues 😘"),
    "Adventurous 🏞️": ("adventure", "Deviii Let’s go exploring wild worlds 🌍✨"),
    "Chill 😌": ("documentary", "Deviii Time to relax and learn a thing or two ☕"),
    "Scared 😱": ("horror", "Deviii Brace yourself, it's about to get spooky 👻"),
    "Curious 🧠": ("mystery", "Deviii Let’s solve something intriguing 🔍🕵️‍♀️"),
    "Musical 🎶": ("music", "Deviii Sing along with your soul 🎤🎧"),
    "Dreamy 🌌": ("fantasy", "Deviii Let’s escape reality for a while 🌈🦄")
}

# Styling
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

st.markdown("""<div class="title-style">BingeBoo 🍿 - Top TV Picks For The Week</div>""", unsafe_allow_html=True)
st.markdown("""<div class="subtitle-style">(Handpicked shows for Deviii, the binge queen 👸🙈)</div>""", unsafe_allow_html=True)

# Initialize session state
if "mood" not in st.session_state:
    st.session_state["mood"] = ""
if "genre" not in st.session_state:
    st.session_state["genre"] = ""

col1, col2, col3, col4 = st.columns([4, 1.3, 2, 1.3])

with col1:
    #st.markdown("<div style='font-size: 1.1rem; font-weight: bold;'>Deviii, how’s your heart today?🥹 let BingeBoo AI serve you a genre you love </div>", unsafe_allow_html=True)

    st.markdown("**Deviii, how’s your heart today?🥹let BingeBoo AI serve you a genre you love**")

moods = ["", *mood_genre_map.keys()]
with col2:
    mood_selection = st.selectbox("Mood", moods, index=moods.index(st.session_state["mood"]), label_visibility="collapsed")
    if mood_selection != st.session_state["mood"]:
        st.session_state["mood"] = mood_selection
        st.session_state["genre"] = ""

with col3:
    st.markdown("**Or Deviii just pick your favorite genre🍿💫**")

all_genres = ["", "action", "adventure", "animation", "anime", "comedy", "crime", "documentary",
              "drama", "family", "fantasy", "game-show", "history", "horror", "music",
              "mystery", "reality", "romance", "science-fiction", "soap", "talk-show",
              "thriller", "war", "western"]
with col4:
    genre_selection = st.selectbox("Genre", [g.title() for g in all_genres],
                                   index=all_genres.index(st.session_state["genre"]) if st.session_state["genre"] else 0,
                                   label_visibility="collapsed")
    if genre_selection.lower() != st.session_state["genre"]:
        st.session_state["genre"] = genre_selection.lower()
        st.session_state["mood"] = ""

# Fetching logic
def safe_get(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=timeout)
            res.raise_for_status()
            return res
        except requests.HTTPError:
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

# Final genre + custom message
final_genre = st.session_state["genre"]
custom_message = None

if not final_genre and st.session_state["mood"]:
    final_genre, custom_message = mood_genre_map.get(st.session_state["mood"], (None, None))

if final_genre:
    with st.spinner(f"✨ {custom_message or f'Binging top {final_genre.title()} shows for you...'}"):
        shows = fetch_trending_shows(genre=final_genre)
        display_posters(shows)
