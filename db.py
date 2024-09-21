from datetime import datetime
import sqlite3

DB_NAME = 'downloads.db'

def connect_to_db():
    return sqlite3.connect(DB_NAME)

def create_tables(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spotify_url TEXT NOT NULL,
            submitted DATETIME NOT NULL,
            song_info_id INTEGER,
            s3_url TEXT,
            FOREIGN KEY (song_info_id) REFERENCES songinfo (id)
        )
        ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS songinfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            artist TEXT,
            cover_url TEXT,
            duration INTEGER,
            year INTEGER,
            upload_date TEXT,
            spotify_song_id TEXT,
            spotify_url TEXT
        )
        ''')
    conn.commit()

def insert_download(conn, spotify_url, song_info_id, s3_url):
    c = conn.cursor()
    submitted = datetime.now()
    c.execute('''
        INSERT INTO downloads (spotify_url, submitted, song_info_id, s3_url)
        VALUES (?, ?, ?, ?)
        ''', (spotify_url, submitted, song_info_id, s3_url))
    conn.commit()

def insert_song_info(conn, name, artist, cover_url, duration, year, upload_date, spotify_song_id, spotify_url):
    c = conn.cursor()
    c.execute('''
        INSERT INTO songinfo (name, artist, cover_url, duration, year, upload_date, spotify_song_id, spotify_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, artist, cover_url, duration, year, upload_date, spotify_song_id, spotify_url))  
    conn.commit()


if __name__ == '__main__':
    conn = connect_to_db()
    create_tables(conn)
    conn.close()
    print('Database setup complete')
