#!/usr/bin/env python3
"""
Sentiment analysis for feedback with vaderSentiment support
"""

import re
from typing import Tuple

# Try to import vaderSentiment, fallback to simple analysis
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

class SentimentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'like', 
            'fantastic', 'wonderful', 'perfect', 'best', 'brilliant', 'outstanding'
        }
        self.negative_words = {
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'worst', 'horrible', 
            'poor', 'disappointing', 'boring', 'slow', 'confusing', 'annoying'
        }
    
    def analyze_sentiment(self, text: str, rating: int = None) -> Tuple[str, float]:
        """
        Analyze sentiment from text and rating using VADER or fallback
        Returns (sentiment, engagement_score)
        """
        if not text:
            text = ""
        
        # Use VADER if available, otherwise fallback to simple analysis
        if self.vader_analyzer and text.strip():
            sentiment = self._analyze_with_vader(text, rating)
        else:
            sentiment = self._analyze_simple(text, rating)
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement(text, rating)
        
        return sentiment, round(engagement_score, 3)
    
    def _analyze_with_vader(self, text: str, rating: int = None) -> str:
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        # Combine VADER score with rating if available
        if rating:
            rating_sentiment = (rating - 3) / 2.0  # Convert 1-5 to -1 to 1
            # Weight VADER 70%, rating 30%
            combined_score = (compound * 0.7) + (rating_sentiment * 0.3)
        else:
            combined_score = compound
        
        if combined_score >= 0.1:
            return "positive"
        elif combined_score <= -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_simple(self, text: str, rating: int = None) -> str:
        """Simple sentiment analysis fallback"""
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Determine sentiment based on rating and text
        if rating:
            if rating >= 4:
                return "positive"
            elif rating <= 2:
                return "negative"
            else:
                return "neutral"
        else:
            # Use text analysis
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
    
    def _calculate_engagement(self, text: str, rating: int = None) -> float:
        """Calculate engagement score (0-1)"""
        # Text length component (longer comments = higher engagement)
        text_length_score = min(len(text) / 100, 1.0)
        
        # Rating component
        if rating:
            # Extreme ratings (1,2,5) show higher engagement than neutral (3,4)
            rating_engagement = 1.0 if rating in [1, 2, 5] else 0.7
        else:
            rating_engagement = 0.5
        
        # Word count component (more words = higher engagement)
        word_count = len(text.split()) if text else 0
        word_score = min(word_count / 20, 1.0)  # Cap at 20 words
        
        # Combine components
        engagement_score = (text_length_score * 0.4) + (rating_engagement * 0.4) + (word_score * 0.2)
        
        return engagement_score

# Global analyzer instance
analyzer = SentimentAnalyzer()