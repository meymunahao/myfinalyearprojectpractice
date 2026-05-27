from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
import nltk

# Downloading the sentence splitter dictionaries
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Loading the model globally so it doesn't have to reload for every single function call
model = SentenceTransformer('all-mpnet-base-v2')

def calculate_similarity(text1, text2):
    """Calculates the document-level cosine similarity."""
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    cosine_score = util.cos_sim(embedding1, embedding2)
    return cosine_score.item() * 100

def get_matched_sentences(raw_text1, raw_text2, threshold_percentage=80.0):
    """
    Tokenizes text into sentences, computes an N x M similarity matrix,
    and extracts sentence pairs that cross/exceed the threshold.
    """
    # 1. Break the giant text blocks into individual sentences
    sentences1 = sent_tokenize(raw_text1)
    sentences2 = sent_tokenize(raw_text2)
    
    # Checking if a document is empty  or not
    if not sentences1 or not sentences2:
        return []
        
    # 2. Generate embeddings for EVERY sentence at once
    # This turns our lists of sentences into two giant matrices of numbers
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)
    
    # 3. Compute the N x M similarity matrix
    # It instantly calculates the angle between every sentence in Doc 1 and Doc 2
    cosine_scores = util.cos_sim(embeddings1, embeddings2)
    
    # 4. Filter and extract the matches
    threshold_decimal = threshold_percentage / 100.0
    matches = []
    
    # Loop through the matrix grid to find the high scores
    for i in range(len(sentences1)):
        for j in range(len(sentences2)):
            score = cosine_scores[i][j].item()
            
            if score >= threshold_decimal:
                matches.append({
                    "doc1_sentence": sentences1[i],
                    "doc2_sentence": sentences2[j],
                    "score": score * 100
                })
                
    # Sort the matches so the highest similarity scores appear at the top of the list
    matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    return matches