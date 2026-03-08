import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# We have to tell NLTK to download its background dictionaries the very first time we run this.
# (It might take a few seconds to download these when you first run the script)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def clean_and_preprocess(raw_text):
    # 1. Convert everything to lowercase
    text = raw_text.lower()
    
    # 2. Remove all punctuation (commas, periods, exclamation marks)
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 3. Tokenization: Break the giant paragraph into individual words
    tokens = word_tokenize(text)
    
    # 4. Stopword Removal: Filter out common filler words ('the', 'is', 'at')
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # 5. Lemmatization: Reduce words to their root form (e.g., 'running' -> 'run')
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Join the clean tokens back into a single string for the SBERT model
    clean_text = " ".join(lemmatized_tokens)
    
    return clean_text

if __name__ == "__main__":
    # Let's test it with a messy dummy sentence first!
    messy_text = "The quick brown foxes are running quickly through the dark forests!"
    
    print("Working on it...")
    print("-" * 50)
    print(f"Original Raw Text: {messy_text}")
    
    cleaned_result = clean_and_preprocess(messy_text)
    print(f"Cleaned NLP Text:  {cleaned_result}")
    print("-" * 50)