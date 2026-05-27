from sentence_transformers import SentenceTransformer

def get_sentence_embeddings(text):
    # Load the specific SBERT model (12-layer, 110M parameter, 768-dim requirement)
    # *The very first time this runs, it will download the model (approx. 400MB) from Hugging Face.
    model = SentenceTransformer('all-mpnet-base-v2')
    
    # Generate the embeddings for the inputted text
    embeddings = model.encode(text)
    
    return embeddings

if __name__ == "__main__":
    test_text = "quick brown fox running quickly dark forest"
    
    print("Loading the Deep Learning SBERT model (this might take a minute on the first run to download)...")
    
    # Running the model
    vector = get_sentence_embeddings(test_text)
    
    print("\n✅ Embedding successful!")
    print("-" * 50)
    print(f"Vector dimensions (Should be 768): {len(vector)}")
    print(f"First 5 numbers of the 768-dimensional vector:\n{vector[:5]}")
    print("-" * 50)