from pymongo import MongoClient

def test_db_connection():
    # Connecting to the local MongoDB
    client = MongoClient('mongodb://localhost:27017/') #mongodb+srv://admin_db:<db_password>@cluster0.baqddkn.mongodb.net/?appName=Cluster0
    
    # Created the database: 'plagiarism_db'
    db = client['plagiarism_db']
    
    # Created collections for the documents and the similarity results
    documents_collection = db['documents']
    results_collection = db['results']
    
    documents_collection.insert_one({"test_key": "Database is working perfectly!"})
    
    print("MongoDB Connected Successfully!")
    print(f"Active Database: {db.name}")
    print(f"Active Collections: {db.list_collection_names()}")

if __name__ == "__main__":
    test_db_connection()