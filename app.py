# app.py
import streamlit as st
import requests
import textwrap
import time

# Trakt API config
TRAKT_CLIENT_ID = "f85b06aee7a3b6d67e82526087422da3749e3ff0c1688b18fe39d54511cf1f1c"
HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": TRAKT_CLIENT_ID
}

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

def wrap_text(text, width=90):
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

def display_shows(shows):
    for show in shows:
        title = show.get("title", "Untitled")
        year = show.get("year", "")
        rating = show.get("rating", "N/A")
        overview = wrap_text(show.get("overview"))

        st.markdown(f"### {title} ({year})")
        st.markdown(f"⭐ **{rating:.1f}**" if isinstance(rating, float) else f"⭐ **{rating}**")
        st.markdown(f"<div style='color: gray;'>{overview}</div>", unsafe_allow_html=True)
        st.markdown("---")

# 🎬 BingeBoo App Title
st.set_page_config(page_title="BingeBoo 🎬", layout="centered")
st.title("🍿 BingeBoo - Top TV Picks For The Week")
st.markdown("### _(Handpicked shows for Deviii, the binge queen 👸🙈)_")

st.write("Pick a genre or refresh trending shows for the week.")

# Genres
genres = [
    "action", "adventure", "animation", "anime", "comedy", "crime", "documentary",
    "drama", "family", "fantasy", "game-show", "history", "horror", "music",
    "mystery", "reality", "romance", "science-fiction", "soap", "talk-show",
    "thriller", "war", "western"
]

# Mobile-friendly selectbox layout 🎯
selected_genre_display = st.selectbox("🎬 Choose a Genre", [""] + [g.title() for g in genres])

if selected_genre_display:
    selected_genre = selected_genre_display.lower()
    with st.spinner("Binging..."):
        shows = fetch_trending_shows(genre=selected_genre)
        display_shows(shows)
else:
    if st.button("🔁 Refresh Trending Shows"):
        with st.spinner("Binging..."):
            shows = fetch_trending_shows()
            display_shows(shows)

if __name__ == "__main__":
    pass    

