from pymongo import MongoClient

def test_db_connection():
    # Connect to your local MongoDB instance
    client = MongoClient('mongodb://localhost:27017/')
    
    # Create (or connect to) a database named 'plagiarism_db'
    db = client['plagiarism_db']
    
    # Create (or connect to) collections for your documents and the similarity results
    documents_collection = db['documents']
    results_collection = db['results']
    
    # Insert a dummy record just to force MongoDB to physically create the database
    # (MongoDB waits until data is inserted before showing it in Compass)
    documents_collection.insert_one({"test_key": "Database is working perfectly!"})
    
    print("MongoDB Connected Successfully!")
    print(f"Active Database: {db.name}")
    print(f"Active Collections: {db.list_collection_names()}")

if __name__ == "__main__":
    test_db_connection()