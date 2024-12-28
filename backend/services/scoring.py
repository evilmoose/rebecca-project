from textblob import TextBlob
import re

def calculate_scores(message, context=""):
    """
    Calculate scores for various conversational metrics.
    Metrics include:
    - Emotional Resonence
    - Engagement 
    - Creativity
    - Personalization
    = Overall Revelance
    """
    scores = {}

    # Emotional Resonance: Sentiment similarity and depth
    message_sentiment = TextBlob(message).sentiment.polarity
    context_sentiment = TextBlob(context).sentiment.polarity
    tone_similarity = 1 - abs(message_sentiment - context_sentiment)
    scores['emotional_resonance'] = round(tone_similarity * 0.7 + message_sentiment * 0.3, 2)

    # Engagement: Open-ended questions and response length
    open_ended_prompts = len(re.findall(r"\b(how|what|why|feel|think)\b", message, re.IGNORECASE))
    scores['engagement'] = round(open_ended_prompts * 0.5 + len(message.split()) / 50, 2)

    # Creativity: Semantic richness and reflective prompts
    semantic_richness = len(set(message.split())) / len(message.split()) if message.split() else 0
    scores['creativity'] = round(semantic_richness * 0.6 + open_ended_prompts * 0.4, 2)

    # Personalization: Context relevance and tone alignment
    user_context_relevance = len(set(message.split()) & set(context.split())) / len(message.split()) if message.split() else 0
    scores['personalization'] = round(user_context_relevance * 0.8 + tone_similarity * 0.2, 2)

    # Overall Relevance: Combination of context relevance and richness
    scores['overall_relevance'] = round(user_context_relevance * 0.7 + semantic_richness * 0.3, 2)

    return scores