from sentence_transformers import SentenceTransformer, util

def calculate_similarity(text1, text2):
    # Load the model (It will be instant this time since it's already downloaded!)
    model = SentenceTransformer('all-mpnet-base-v2')
    
    # 1. Generate the embeddings for BOTH texts
    # convert_to_tensor=True makes the math operations much faster
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    
    # 2. Calculate the Cosine Similarity
    cosine_score = util.cos_sim(embedding1, embedding2)
    
    # 3. Convert the raw mathematical score into a clean percentage (e.g., 0.85 -> 85.0%)
    percentage = cosine_score.item() * 100
    
    return percentage

if __name__ == "__main__":
    # Let's test it with a classic paraphrasing trick students use!
    source_text = "Educational institutions often struggle with undetected plagiarism in student submissions."
    student_text = "Schools and universities frequently find it hard to catch copied work in assignments turned in by students."
    
    print("Calculating semantic similarity...")
    
    # Run the comparison
    similarity_percentage = calculate_similarity(source_text, student_text)
    
    print("\n✅ Comparison Complete!")
    print("-" * 50)
    print(f"Source Text:  {source_text}")
    print(f"Student Text: {student_text}")
    print(f"\nSimilarity Score: {similarity_percentage:.2f}%")
    
    # 4. Apply the Threshold (As outlined in Objective iv)
    THRESHOLD = 80.0
    
    if similarity_percentage >= THRESHOLD:
        print("🚨 FLAG: Plagiarism Detected! (Score exceeds threshold)")
    else:
        print("✅ CLEAR: Document seems original.")
    print("-" * 50)