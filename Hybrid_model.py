import requests
from bs4 import BeautifulSoup
import feedparser
import pandas as pd
import streamlit as st
from datetime import datetime

# -------------------- CONFIG -------------------- #
AGENT_SITES = [
    "https://www.rightmove.co.uk/",
    "https://www.zoopla.co.uk/",
    "https://www.onthemarket.com/",
    "https://www.primelocation.com/",
    "https://www.boomin.com/",
    "https://www.nestoria.co.uk/",
    "https://www.gumtree.com/property-to-rent/",
    "https://www.openrent.co.uk/",
    "https://www.thehouseshop.com/",
    "https://www.knightfrank.co.uk/",
    "https://www.hamptons.co.uk/",
    "https://www.struttandparker.com/",
    "https://www.chestertons.co.uk/",
    "https://www.winkworth.co.uk/",
    "https://www.your-move.co.uk/",
    "https://www.reedsrains.co.uk/",
    "https://www.connells.co.uk/",
    "https://www.countrywide.co.uk/",
    "https://www.bairstoweves.co.uk/",
    "https://www.belvoir.co.uk/",
    "https://www.hunters.com/",
    "https://www.yopa.co.uk/",
    "https://www.purplebricks.co.uk/",
    "https://www.jackson-stops.co.uk/",
    "https://www.dexters.co.uk/",
    "https://www.jll.co.uk/",
    "https://www.cbre.co.uk/",
    "https://www.fineandcountry.com/",
    "https://www.haart.co.uk/",
    "https://www.mccarthyandstone.co.uk/",
    "https://www.themodernhouse.com/",
    "https://www.propertypal.com/",
    "https://www.propertyheads.com/",
    "https://www.mouseprice.com/",
    "https://www.findaproperty.com/",
    "https://www.mashroom.co.uk/",
    "https://www.carterjonas.co.uk/",
    "https://www.movehut.co.uk/",
    "https://www.home.co.uk/",
    "https://www.rightmove.co.uk/commercial-property.html/",
    "https://www.zoopla.co.uk/for-sale/commercial-property/",
    "https://thenegotiator.co.uk/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -------------------- RSS FETCH -------------------- #
def fetch_rss(url):
    """Try to detect and parse RSS feed from the site."""
    possible_feeds = [
        url + "/rss",
        url + "/feed",
        url + "/rss.xml",
        url + "/feed.xml",
        url + "/rssfeed",
    ]
    for feed_url in possible_feeds:
        try:
            resp = requests.get(feed_url, headers=HEADERS, timeout=8)
            if resp.status_code == 200 and ("xml" in resp.headers.get("Content-Type", "")):
                feed = feedparser.parse(resp.text)
                if len(feed.entries) > 0:
                    return feed.entries
        except Exception:
            pass
    return None

# -------------------- HTML FALLBACK -------------------- #
def fallback_scrape(url):
    """Basic HTML fallback scraper if no RSS feed."""
    listings = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find common patterns (adjust per site)
        for prop in soup.find_all(["article", "div"], class_=lambda x: x and "property" in x.lower()):
            title = prop.find(["h2", "h3"])
            price = prop.find(string=lambda s: "£" in s)
            link = prop.find("a", href=True)
            listings.append({
                "title": title.get_text(strip=True) if title else "N/A",
                "price": price.strip() if price else "N/A",
                "link": link["href"] if link else url,
            })
    except Exception:
        pass
    return listings[:10]

# -------------------- STREAMLIT DASHBOARD -------------------- #
st.set_page_config(page_title="UK Property Feed Dashboard", page_icon="🏠", layout="wide")

st.title("🏠 UK Property Feed Dashboard")
st.caption("Powered by RSS feeds — live listings from UK estate agents")

data = []

for site in AGENT_SITES:
    st.write(f"🔍 Checking: **{site}**")
    rss_entries = fetch_rss(site)
    if rss_entries:
        for entry in rss_entries[:10]:
            data.append({
                "source": site,
                "title": entry.get("title", "N/A"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "N/A"),
                "price": entry.get("price", "N/A"),
            })
        st.success(f"✅ RSS Feed Found — {len(rss_entries)} entries")
    else:
        scraped = fallback_scrape(site)
        if scraped:
            data.extend([{**prop, "source": site} for prop in scraped])
            st.warning(f"⚠️ RSS not found — scraped {len(scraped)} listings")
        else:
            st.error(f"❌ No RSS or HTML data detected for {site}")

if data:
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.info("No property data found. Try refreshing or adding more estate agents.")
