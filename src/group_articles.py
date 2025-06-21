import re
import sys
import argparse
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

def preprocess_title(title):
    """Preprocess article title: tokenize, remove stopwords, and lemmatize."""
    # Convert to lowercase
    title = title.lower()
    # Remove punctuation and special characters
    title = re.sub(r'[^\w\s]', '', title)
    # Tokenize
    tokens = word_tokenize(title)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    # Lemmatize
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(tokens)

def group_articles(titles, num_groups):
    """Group article titles into subject categories using K-means clustering."""
    if not titles:
        return {}
    
    # Preprocess all titles
    processed_titles = [preprocess_title(title) for title in titles]
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(processed_titles)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=num_groups, random_state=42)
    labels = kmeans.fit_predict(X)
    
    # Group titles by cluster
    groups = defaultdict(list)
    for title, label in zip(titles, labels):
        groups[label].append(title)
    
    return groups

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Group article titles by subject.")
    parser.add_argument('num_groups', type=int, help="Number of subject groups to create")
    args = parser.parse_args()
    
    # Validate number of groups
    if args.num_groups <= 0:
        print("Error: Number of groups must be positive.")
        sys.exit(1)
    
    # Read titles from stdin
    print("Enter article titles (press Ctrl+D or Ctrl+Z when done):")
    titles = []
    try:
        for line in sys.stdin:
            title = line.strip()
            if title:  # Only add non-empty titles
                titles.append(title)
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully
    
    if not titles:
        print("No titles provided.")
        sys.exit(1)
    
    # Ensure number of groups doesn't exceed number of titles
    num_groups = min(args.num_groups, len(titles))
    
    # Group articles
    grouped_articles = group_articles(titles, num_groups)
    
    # Print results
    for group_id, titles in grouped_articles.items():
        print(f"\nSubject Group {group_id + 1}:")

        for title in titles:
            print(f"- {title}")

if __name__ == "__main__":
    main()
