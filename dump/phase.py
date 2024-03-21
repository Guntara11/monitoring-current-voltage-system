from datetime import datetime
from pymongo import MongoClient

# Ganti URL koneksi dengan URL koneksi MongoDB Atlas Anda
uri = "mongodb+srv://sopiand23:Manusiakuat1@mycluster.bfapaaq.mongodb.net/?retryWrites=true&w=majority"

# Buat koneksi ke database MongoDB Atlas
client = MongoClient(uri)

# Gunakan database dan koleksi yang sesuai
db = client.MyData # Ganti nama_database dengan nama database Anda
collection = db.MyCollect # Ganti nama_koleksi dengan nama koleksi Anda

# Minta pengguna untuk memasukkan waktu awal dan akhir
start_time_str = input("Masukkan waktu awal (format: YYYY-MM-DD HH:MM:SS): ")
end_time_str = input("Masukkan waktu akhir (format: YYYY-MM-DD HH:MM:SS): ")

# Ubah string waktu menjadi objek datetime
# start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
# end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

results = collection.find({"Timestamp": {"$gte": start_time_str, "$lte": end_time_str}})

# Lakukan sesuatu dengan hasil pencarian
for result in results:
    print(result)