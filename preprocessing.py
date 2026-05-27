import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

def clean_and_preprocess(raw_text):
    # 1. Converts everything to lowercase
    text = raw_text.lower()
    
    # 2. Removes all punctuation (commas, periods, exclamation marks)
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 3. Tokenization: Break the giant paragraph into individual words
    tokens = word_tokenize(text)
    
    # 4. Stopword Removal: Filtering out common filler words ('the', 'is', 'at')
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # 5. Lemmatization: Reducing words to their root form (e.g., 'running' -> 'run')
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Join the clean tokens back into a single string for the SBERT model
    clean_text = " ".join(lemmatized_tokens)
    
    return clean_text
