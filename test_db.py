from pymongo import MongoClient

# Paste your EXACT connection string inside the quotes below
# Make sure your real password is in it, with no < > brackets
uri = "mongodb+srv://admin_db:ewSSmfOmNOD1on6T@cluster0.baqddkn.mongodb.net/?appName=Cluster0"

try:
    print("Attempting to connect to MongoDB Atlas...")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ SUCCESS! The password and connection string are perfect.")
except Exception as e:
    print("❌ FAILED! Here is the error:")
    print(e)