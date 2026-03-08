from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
import nltk

# Ensure the sentence splitter dictionaries are downloaded
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Load the model globally so it doesn't have to reload for every single function call
model = SentenceTransformer('all-mpnet-base-v2')

def calculate_similarity(text1, text2):
    """Calculates the overall document-level similarity."""
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    cosine_score = util.cos_sim(embedding1, embedding2)
    return cosine_score.item() * 100

def get_matched_sentences(raw_text1, raw_text2, threshold_percentage=80.0):
    """
    Splits text into sentences, computes an N x M similarity matrix,
    and returns the specific sentence pairs that cross the threshold.
    """
    # 1. Break the giant text blocks into individual sentences
    sentences1 = sent_tokenize(raw_text1)
    sentences2 = sent_tokenize(raw_text2)
    
    # Safety check if a document is empty
    if not sentences1 or not sentences2:
        return []
        
    # 2. Generate embeddings for EVERY sentence at once
    # This turns our lists of sentences into two giant matrices of numbers
    embeddings1 = model.encode(sentences1, convert_to_tensor=True)
    embeddings2 = model.encode(sentences2, convert_to_tensor=True)
    
    # 3. Compute the N x M similarity matrix
    # This instantly calculates the angle between every sentence in Doc 1 and Doc 2
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

if __name__ == "__main__":
    # UNIT TEST: Let's test the sentence matrix with a mini-document!
    
    doc1_dummy = "Deep learning is a subset of machine learning. Educational institutions often struggle with undetected plagiarism. It requires large amounts of data."
    
    doc2_dummy = "Artificial neural networks need massive datasets to train. Schools and universities frequently find it hard to catch copied work in assignments. AI is changing the world."
    
    print("Calculating Sentence-by-Sentence Matrix...")
    
    # Run the new function
    matched_pairs = get_matched_sentences(doc1_dummy, doc2_dummy, threshold_percentage=70.0)
    
    print("\n✅ Matrix Comparison Complete!")
    print("-" * 50)
    print(f"Total flagged sentence pairs found: {len(matched_pairs)}\n")
    
    for match in matched_pairs:
        print(f"🚨 Score: {match['score']:.2f}%")
        print(f"Doc 1: {match['doc1_sentence']}")
        print(f"Doc 2: {match['doc2_sentence']}")
        print("-")
    print("-" * 50)