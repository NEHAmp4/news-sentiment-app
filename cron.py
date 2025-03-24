import pandas as pd
import pickle
import re
import os

from utils.news_scraper import scrape_news
from utils.gemini_service import GeminiService

def main():
    # Read list of companies from CSV
    try:
        df = pd.read_csv('data/company_list.csv')
    except Exception as e:
        print(f"Failed to read company list: {e}")
        return
    companies = df['Company'].dropna().tolist()
    if not companies:
        print("No companies found in the list.")
        return

    service = GeminiService(api_key=None)  # Initialize the Gemini service (mock or real API if key provided)
    os.makedirs('data/output', exist_ok=True)

    for company in companies:
        print(f"Processing company: {company}...")
        # Scrape news articles for the company
        articles = scrape_news(company, num_articles=10)
        if not articles:
            print(f"No articles found or unable to scrape for {company}. Skipping.")
            continue
        # Analyze articles using the Gemini service (LLM)
        result = service.analyze_articles(company, articles)
        # Save the result as a pickle file
        filename_base = re.sub(r'\W+', '_', company.lower())
        file_path = os.path.join('data', 'output', f"{filename_base}.pkl")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(result, f)
            print(f"Saved analysis for {company} to {file_path}")
        except Exception as e:
            print(f"Error saving output for {company}: {e}")

if __name__ == "__main__":
    main()
