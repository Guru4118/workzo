from pymongo import MongoClient
import certifi

uri = "mongodb+srv://gprasath103_db_user:L1SiIBS4ILvJQTte@cluster0.dt74rim.mongodb.net/job_portal?retryWrites=true&w=majority"

client = MongoClient(uri, tlsCAFile=certifi.where())

try:
    db = client["job_portal"]
    db["test"].insert_one({"msg": "hello"})
    print("DB connected and write works!")
except Exception as e:
    print("DB ERROR:", e)
