from pymongo import MongoClient
from pymongo.database import Database




def get_db()-> Database:
    client = MongoClient("mongodb://localhost:27017/") 
# client.admin.command('ping')
    db = client["management_system"]                      
    return db 







































# def get_user_collection():
#     db = get_db()
#     return db["users_db"]

# def get_db():
#     try:
#         client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000, tls=True, tlsCAFile=certifi.where())
        
#         client.admin.command('ping')
#         db = client["management_system"]                        #my mongoDB connection name
#         return db
#     except (ConnectionFailure, ServerSelectionTimeoutError) as e:
#         raise Exception(f"Failed to connect to MongoDB: {e}")
#     except Exception as e:
#         raise Exception(f"Database connection error: {e}")
    
# def get_user_collection():
#     db = get_db()
#     return db["users_db"]

































































