from datetime import datetime
from pymongo import MongoClient

# Ganti URL koneksi dengan URL koneksi MongoDB Atlas Anda
# Anda dapat menemukan URL ini di panel MongoDB Atlas Anda
# Formatnya mirip dengan mongodb+srv://username:password@cluster-url/database-name
uri = "mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/?retryWrites=true&w=majority"

# Buat koneksi ke database MongoDB Atlas
client = MongoClient(uri)

# Gunakan database dan koleksi yang sesuai
db = client.MyData # Ganti nama_database dengan nama database Anda
collection = db.MyCollect # Ganti nama_koleksi dengan nama koleksi Anda

results = collection.find({"Timestamp" : { "$gte" : "2024-02-09_03:13:38", "$lt" : "2024-02-09_03:14:38" }})

# Lakukan sesuatu dengan hasil pencarian
for result in results:
    print(result)
