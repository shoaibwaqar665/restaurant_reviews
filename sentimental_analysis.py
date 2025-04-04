# Import required libraries for sentiment analysis
from textblob import TextBlob  # For basic sentiment analysis
import nltk  # Natural Language Toolkit
from nltk.sentiment import SentimentIntensityAnalyzer  # For VADER sentiment analysis
import pandas as pd  # For data manipulation and analysis
import json  # For reading JSON files
import os  # For file operations
import re  # For text processing
from myapp.dbOperations import fetch_trip_data,fetch_google_data
from decimal import Decimal
from datetime import date, datetime

# Download required NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')  # For word tokenization

# Define categories and their associated keywords
CATEGORIES = {
    'Room Experience': ['room', 'bed', 'bedroom', 'bathroom', 'shower', 'view', 'window', 'suite', 'accommodation', 'comfort', 'cleanliness', 'space', 'size', 'amenities'],
    'Service/Staff': ['staff', 'service', 'employee', 'reception', 'concierge', 'friendly', 'helpful', 'attentive', 'professional', 'courteous', 'assistance', 'support'],
    'Facilities/Property': ['facility', 'property', 'building', 'lobby', 'pool', 'gym', 'spa', 'restaurant', 'bar', 'lounge', 'area', 'grounds', 'architecture', 'design'],
    'Food/Beverage': ['food', 'breakfast', 'dinner', 'lunch', 'meal', 'restaurant', 'dining', 'beverage', 'drink', 'bar', 'menu', 'taste', 'quality', 'fresh'],
    'Location/Neighborhood': ['location', 'area', 'neighborhood', 'surroundings', 'nearby', 'close', 'distance', 'access', 'transportation', 'walking', 'convenient'],
    'Price/Value': ['price', 'cost', 'value', 'expensive', 'cheap', 'affordable', 'worth', 'budget', 'rate', 'pricing', 'deal'],
    'Technology/Connectivity': ['wifi', 'internet', 'connection', 'signal', 'technology', 'smart', 'digital', 'device', 'connectivity', 'network'],
    'Booking/Check-In/Check-out': ['booking', 'reservation', 'check-in', 'checkout', 'arrival', 'departure', 'process', 'procedure', 'registration', 'cancellation'],
    'Hygiene/Safety': ['clean', 'hygiene', 'sanitary', 'safety', 'security', 'health', 'sanitization', 'disinfection', 'protection', 'precaution'],
    'Overall Sentiment Phrases': ['amazing', 'excellent', 'great', 'wonderful', 'fantastic', 'perfect', 'terrible', 'awful', 'horrible', 'disappointing', 'outstanding', 'recommend']
}

def analyze_sentiment_textblob(text):
    """
    Analyze sentiment using TextBlob
    Returns a tuple of (polarity, subjectivity)
    """
    analysis = TextBlob(text)
    return analysis.sentiment

def analyze_sentiment_nltk(text):
    """
    Analyze sentiment using NLTK's VADER
    Returns a dictionary with positive, negative, neutral, and compound scores
    """
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)

def get_sentiment_label(score):
    """
    Convert sentiment score to label
    """
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"

def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)  # or str(obj) if you prefer strings
    raise TypeError(f"Type {type(obj)} not serializable")

def custom_serializer(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def categorize_words(text):
    """
    Categorize words in the text based on predefined categories
    """
    words = nltk.word_tokenize(text.lower())
    word_categories = {category: [] for category in CATEGORIES.keys()}
    
    for word in words:
        # Clean the word
        word = re.sub(r'[^\w\s]', '', word)
        if not word:
            continue
            
        # Check each category
        for category, keywords in CATEGORIES.items():
            if word in keywords:
                word_categories[category].append(word)
    
    return word_categories

def analyze_reviews(reviews):
    """
    Analyze a list of reviews and return DataFrames with sentiment analysis results
    """
    # Overall sentiment results
    overall_results = []
    
    # Word-level analysis results
    word_results = []
    
    for review in reviews:
        # TextBlob analysis
        polarity, subjectivity = analyze_sentiment_textblob(review)
        
        # NLTK analysis
        nltk_scores = analyze_sentiment_nltk(review)
        
        # Word tokenization and counting
        words = nltk.word_tokenize(review)
        word_count = len(words)
        
        # Categorize words
        word_categories = categorize_words(review)
        
        # Add to overall results
        overall_results.append({
            'Review': review,
            'Word_Count': word_count,
            'TextBlob_Polarity': polarity,
            'TextBlob_Subjectivity': subjectivity,
            'TextBlob_Sentiment': get_sentiment_label(polarity),
            'NLTK_Positive': nltk_scores['pos'],
            'NLTK_Negative': nltk_scores['neg'],
            'NLTK_Neutral': nltk_scores['neu'],
            'NLTK_Compound': nltk_scores['compound'],
            'NLTK_Sentiment': get_sentiment_label(nltk_scores['compound'])
        })
        
        # Add to word-level results
        for category, words in word_categories.items():
            if words:  # Only add if there are words in this category
                word_results.append({
                    'Review': review,
                    'Category': category,
                    'Words': ', '.join(words),
                    'Word_Count': len(words)
                })
    
    return pd.DataFrame(overall_results), pd.DataFrame(word_results)

def read_reviews_from_db():
    """
    Read reviews from a JSON file
    """
    try:
        
        data = fetch_trip_data()
        data = json.dumps(data, default=custom_serializer)
        data = json.loads(data)
        print(data)
        # Extract reviews from the JSON structure
        reviews = []
        if isinstance(data, dict):
            # Handle different possible JSON structures
            if 'reviews' in data:
                for review in data['reviews']:
                    # Check if the review has a translated version
                    if review.get('translated', False) and 'translatedText' in review:
                        reviews.append(review['translatedText'])
                    else:
                        reviews.append(review.get('text', ''))
            elif 'responses' in data:
                for response in data['responses']:
                    # Check if the response has a translated version
                    if response.get('translated', False) and 'translatedText' in response:
                        reviews.append(response['translatedText'])
                    else:
                        reviews.append(response.get('text', ''))
            elif 'text' in data:
                # Check if the text has a translated version
                if data.get('translated', False) and 'translatedText' in data:
                    reviews.append(data['translatedText'])
                else:
                    reviews.append(data['text'])
        return [review for review in reviews if review.strip()]
    except Exception as e:
        print(f"Error reading from db: {str(e)}")
        return []

def analyze_json_files(directory):
    """
    Analyze all JSON files in the directory
    """
    all_reviews = []
    
    # # Walk through the directory
    # for root, dirs, files in os.walk(directory):
    #     for file in files:
    #         if file.endswith('.json') and 'Ovolo' in file:
    #             file_path = os.path.join(root, file)
    all_reviews = read_reviews_from_db()
    
    # if not all_reviews:
    #     print("No Ovolo reviews found in the JSON files.")
    #     return
    
    # Analyze all reviews
    overall_df, word_df = analyze_reviews(all_reviews)
    
    # Print the results
    print("\nOverall Sentiment Analysis Results:")
    print(overall_df)
    
    print("\nWord-Level Analysis Results:")
    print(word_df)
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Total Reviews: {len(all_reviews)}")
    print("\nTextBlob Sentiment Distribution:")
    print(overall_df['TextBlob_Sentiment'].value_counts())
    print("\nNLTK Sentiment Distribution:")
    print(overall_df['NLTK_Sentiment'].value_counts())
    
    # Save results to CSV with multiple sheets
    with pd.ExcelWriter('sentiment_analysis_results.xlsx') as writer:
        overall_df.to_excel(writer, sheet_name='Overall_Sentiment', index=False)
        word_df.to_excel(writer, sheet_name='Word_Level_Analysis', index=False)
    
    print("\nResults have been saved to 'sentiment_analysis_results.xlsx'")

if __name__ == "__main__":
    # Analyze reviews from the restaurant_reviews directory
    analyze_json_files('restaurant_reviews')