import feedparser

def fetch_google_news(stock):
    """Fetch news headlines and links for a given stock from Google News RSS."""
    url = f"https://news.google.com/rss/search?q={stock}"
    feed = feedparser.parse(url)
    news_list = []
    for entry in feed.entries:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })
    return news_list
