# Note: In a real scenario, you would integrate Google Generative AI (Gemini) here.
# For this mock implementation, we generate summaries, topics, and sentiments with simple heuristics.
import re

class GeminiService:
    def __init__(self, api_key=None):
        """
        Initialize the Gemini service. If an API key is provided and the Google Generative AI 
        SDK is available, you could configure it here. (Using mock implementation by default.)
        """
        if api_key:
            # Example: Configure the real Gemini API client with the provided key (if library is available)
            # import google.generativeai as genai
            # genai.configure(api_key=api_key)
            pass

    def analyze_articles(self, company_name, articles):
        """
        Analyze the given articles (list of dicts with 'title' and 'content').
        Returns a dictionary containing summaries, topics, sentiment analysis, and comparative analysis.
        """
        result = {"Company": company_name, "Articles": []}
        # Define some keywords for simplistic sentiment analysis and topic extraction
        positive_keywords = ["positive", "growth", "good", "great", "record", "increase", "profit", "success", "upbeat", "achievement"]
        negative_keywords = ["negative", "decline", "bad", "decrease", "loss", "fall", "down", "risk", "concern", "issue", "scandal"]
        # Analyze each article
        all_topics = []  # to collect topics for overlap analysis
        for art in articles:
            title = art.get("title", "")
            content = art.get("content", "")
            # Generate a brief summary (e.g., first 1-2 sentences)
            sentences = content.replace('\n', ' ').split('.')
            summary = sentences[0].strip()
            if len(sentences) > 1:
                summary += ". " + sentences[1].strip()
            if len(sentences) > 2:
                summary += "..."
            # Determine sentiment (very basic heuristic based on keyword counts)
            text_lower = content.lower()
            pos_count = sum(text_lower.count(word) for word in positive_keywords)
            neg_count = sum(text_lower.count(word) for word in negative_keywords)
            if pos_count > neg_count:
                sentiment = "Positive"
            elif neg_count > pos_count:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            # Extract topics (using simple keyword matching and proper nouns)
            topics_set = set()
            # Rule-based topic extraction
            if "electric" in text_lower and "vehicle" in text_lower:
                topics_set.add("Electric Vehicles")
            if "stock" in text_lower or "market" in text_lower:
                topics_set.add("Stock Market")
            if "innovation" in text_lower or "innovative" in text_lower:
                topics_set.add("Innovation")
            if "regulation" in text_lower or "regulator" in text_lower:
                topics_set.add("Regulations")
            if "autonomous" in text_lower or "self-driving" in text_lower:
                topics_set.add("Autonomous Vehicles")
            if "merger" in text_lower or "acquisition" in text_lower:
                topics_set.add("Mergers & Acquisitions")
            if "profit" in text_lower or "earnings" in text_lower or "quarter" in text_lower:
                topics_set.add("Financial Performance")
            # Extract capitalized words (proper nouns) as potential topics, excluding the company name
            for word in re.findall(r'\b[A-Z][a-zA-Z]+\b', content):
                if word.lower() == company_name.lower():
                    continue
                if len(topics_set) >= 5:  # limit the number of topics
                    break
                # Add the word if it seems like a relevant proper noun
                topics_set.add(word)
            topics = list(topics_set)
            all_topics.append(topics_set)
            # Append analyzed article data
            result["Articles"].append({
                "Title": title,
                "Summary": summary,
                "Sentiment": sentiment,
                "Topics": topics
            })
        # Comparative Sentiment Analysis
        positive_count = sum(1 for art in result["Articles"] if art["Sentiment"] == "Positive")
        negative_count = sum(1 for art in result["Articles"] if art["Sentiment"] == "Negative")
        neutral_count = sum(1 for art in result["Articles"] if art["Sentiment"] == "Neutral")
        sentiment_dist = {
            "Positive": positive_count,
            "Negative": negative_count,
            "Neutral": neutral_count
        }
        # Coverage Differences (simple comparative statements)
        coverage_diffs = []
        if positive_count > 0 and negative_count > 0:
            # If there are both positive and negative articles
            coverage_diffs.append({
                "Comparison": "Article 1 highlights positive developments, while Article 2 focuses on negative issues.",
                "Impact": "The first article may boost optimism, whereas the second could raise concerns."
            })
            coverage_diffs.append({
                "Comparison": "Article 1 is focused on successes, whereas Article 2 points out challenges and risks.",
                "Impact": "Mixed coverage like this can lead to a balanced but cautious outlook among readers."
            })
        elif positive_count > 0 and negative_count == 0:
            # All non-negative (positive or neutral)
            coverage_diffs.append({
                "Comparison": "News coverage is generally positive and neutral with no negative reports.",
                "Impact": "This fosters a confident outlook as no major concerns are reported."
            })
        elif negative_count > 0 and positive_count == 0:
            # All non-positive (negative or neutral)
            coverage_diffs.append({
                "Comparison": "News coverage is generally negative or neutral with no positive reports.",
                "Impact": "This may create a cautious or pessimistic outlook among observers."
            })
        else:
            # Only neutral articles (no clear positive or negative)
            coverage_diffs.append({
                "Comparison": "All articles maintain a neutral tone without strong positive or negative language.",
                "Impact": "The coverage appears unbiased and factual, giving no clear indication of sentiment."
            })
        # Topic Overlap analysis
        common_topics = []
        unique_topics_map = {}
        if all_topics:
            # Find topics that appear in at least 2 articles
            topic_counts = {}
            for topics_set in all_topics:
                for t in topics_set:
                    topic_counts[t] = topic_counts.get(t, 0) + 1
            common_topics = [t for t, count in topic_counts.items() if count > 1]
            # Unique topics per article
            for idx, topics_set in enumerate(all_topics, start=1):
                unique_topics = [t for t in topics_set if topic_counts.get(t, 0) == 1]
                unique_topics_map[f"Unique Topics in Article {idx}"] = unique_topics
        topic_overlap = {
            "Common Topics": common_topics
        }
        topic_overlap.update(unique_topics_map)
        # Final overall sentiment analysis statement
        if positive_count > negative_count and positive_count >= neutral_count:
            if negative_count == 0:
                final_sent = f"{company_name}'s latest news coverage is overall positive."
            else:
                final_sent = f"{company_name}'s latest news coverage is mostly positive."
            final_sent += " This suggests an optimistic outlook for the company."
        elif negative_count > positive_count and negative_count >= neutral_count:
            if positive_count == 0:
                final_sent = f"{company_name}'s latest news coverage is overall negative."
            else:
                final_sent = f"{company_name}'s latest news coverage is mostly negative."
            final_sent += " This raises concerns about the company's current situation."
        elif neutral_count > positive_count and neutral_count > negative_count:
            final_sent = f"{company_name}'s latest news coverage is largely neutral."
            final_sent += " Most articles are impartial, indicating a balanced perspective."
        else:
            final_sent = f"{company_name}'s latest news coverage is mixed."
            final_sent += " There are both positive and negative aspects in the recent news."
        # Assemble the comparative analysis results
        result["Comparative Sentiment Score"] = {
            "Sentiment Distribution": sentiment_dist,
            "Coverage Differences": coverage_diffs,
            "Topic Overlap": topic_overlap
        }
        result["Final Sentiment Analysis"] = final_sent
        return result
