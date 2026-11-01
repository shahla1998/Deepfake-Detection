import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('deepfake_history.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             image_name TEXT NOT NULL,
             prediction TEXT NOT NULL,
             confidence REAL NOT NULL, 
             timestamp TEXT NOT NULL   
        )
    ''')

    conn.commit()
    conn.close()

def log_prediction(image_name, prediction, confidence):
   conn = sqlite3.connect('deepfake_history.db')
   cursor = conn.cursor()

   current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

   cursor.execute('''
        INSERT INTO predictions (image_name, prediction, confidence, timestamp)
        VALUES (?, ?, ?, ?)
   ''', (image_name, prediction, confidence, current_time))

   conn.commit()
   conn.close()
   print(f"Logged to Database: {image_name} -> {prediction}")

def fetch_history():
   conn = sqlite3.connect('deepfake_history.db')
   cursor = conn.cursor()

   cursor.execute('SELECT * FROM predictions ORDER BY id DESC')
   rows = cursor.fetchall()

   conn.close()
   return rows

if __name__ == '__main__':
   init_db()
   print("Database and table successfully created!")

