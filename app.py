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

# Set Streamlit page config
st.set_page_config(page_title="BingeBoo 🍿", layout="wide")
st.markdown("""
    <style>
        body, .stApp {
            background-color: #000000;
            color: #ffffff;
        }
        .block-container {
            padding: 2rem 1rem;
        }
        .title-style {
            font-size: 2.5rem;
            font-weight: bold;
            color: #e50914;
            font-family: 'Segoe UI', sans-serif;
        }
        .subtitle-style {
            font-size: 1.2rem;
            color: #cccccc;
            margin-bottom: 1rem;
        }
        .poster-card {
            background-color: #121212;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0.5rem;
            width: 300px;
            display: inline-block;
            vertical-align: top;
        }
        .poster-card img {
            border-radius: 5px;
            width: 100%;
        }
        .poster-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-top: 0.5rem;
            color: #ffffff;
        }
        .poster-meta {
            font-size: 0.9rem;
            color: #999999;
        }
        .poster-overview {
            font-size: 0.9rem;
            margin-top: 0.5rem;
            color: #cccccc;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="title-style">BingeBoo 🍿 - Top TV Picks For The Week</div>
    <div class="subtitle-style">(Handpicked shows for Deviii, the binge queen 👸🙈)</div>
""", unsafe_allow_html=True)

def safe_get(url, max_retries=3, timeout=10):
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=timeout)
            res.raise_for_status()
            return res
        except requests.HTTPError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise e

def wrap_text(text, width=80):
    return '\n'.join(textwrap.wrap(text or "No description available.", width=width))

def fetch_trending_shows(genre=None):
    url = "https://api.trakt.tv/shows/trending"
    if genre:
        url += f"?genres={genre}"
    res = safe_get(url)
    shows = res.json()[:10]

    full_data = []
    for entry in shows:
        show = entry.get("show", {})
        slug = show.get("ids", {}).get("slug")
        if slug:
            try:
                details_url = f"https://api.trakt.tv/shows/{slug}?extended=full"
                full_data.append(safe_get(details_url).json())
            except Exception:
                full_data.append(show)
        else:
            full_data.append(show)
    return full_data

def display_posters(shows):
    cols = st.columns(2)
    for i, show in enumerate(shows):
        with cols[i % 2]:
            st.markdown("<div class='poster-card'>", unsafe_allow_html=True)
            poster_url = show.get("images", {}).get("poster", {}).get("thumb")
            if poster_url:
                st.image(poster_url, use_column_width=True)
            title = show.get("title", "Untitled")
            year = show.get("year", "")
            rating = show.get("rating", "N/A")
            overview = wrap_text(show.get("overview"), 120)

            st.markdown(f"<div class='poster-title'>{title} ({year})</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='poster-meta'>⭐ {rating:.1f}</div>" if isinstance(rating, float) else "<div class='poster-meta'>⭐ N/A</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='poster-overview'>{overview}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# Genre buttons
genres = [
    "action", "adventure", "animation", "anime", "comedy", "crime", "documentary",
    "drama", "family", "fantasy", "game-show", "history", "horror", "music",
    "mystery", "reality", "romance", "science-fiction", "soap", "talk-show",
    "thriller", "war", "western"
]

selected_genre = st.selectbox("Pick a genre:", [""] + [g.title() for g in genres])

if selected_genre:
    with st.spinner("Binging..."):
        shows = fetch_trending_shows(genre=selected_genre.lower())
        display_posters(shows)
else:
    if st.button("🔁 Refresh Trending Shows"):
        with st.spinner("Binging..."):
            shows = fetch_trending_shows()
            display_posters(shows)
