import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def scrape_news(company, num_articles=10):
    """
    Search Google News for the given company and scrape content from news articles.
    Returns a list of dicts with 'title' and 'content' for each article.
    """
    query = quote_plus(company)
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    headers = {"User-Agent": "Mozilla/5.0"}  # set a user-agent to mimic a browser
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching news feed for '{company}': {e}")
        return []
    soup = BeautifulSoup(response.text, 'xml')
    items = soup.find_all('item')
    articles = []
    for item in items:
        if len(articles) >= num_articles:
            break
        # Parse title and source from the RSS feed item
        title_tag = item.find('title')
        source_tag = item.find('source')
        title = title_tag.text if title_tag else ""
        source = source_tag.text if source_tag else ""
        # Remove source name from title (if present after a " - ")
        if source and title.endswith(source):
            title = title[:title.rfind(source)].rstrip(" -")
        # Get the link to the news article
        link_tag = item.find('link')
        link = link_tag.text if link_tag else None
        if not link:
            continue
        # Fetch the article webpage
        try:
            article_resp = requests.get(link, headers=headers, timeout=10)
            article_resp.raise_for_status()
        except Exception as e:
            print(f"Skipping article (fetch error): {e}")
            continue
        page_soup = BeautifulSoup(article_resp.text, 'html.parser')
        # Attempt to extract main article text
        content = ""
        article_body = page_soup.find('article')
        if article_body:
            # Join text content of all sub-elements in <article> tag
            content = article_body.get_text(separator=' ')
        else:
            # Fallback: join all paragraph texts in the page
            paragraphs = page_soup.find_all('p')
            content = ' '.join(p.get_text() for p in paragraphs)
        content = content.strip()
        if not content:
            continue
        articles.append({"title": title, "content": content})
    return articles
