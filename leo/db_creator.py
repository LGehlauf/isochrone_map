import sqlite3
import json
import datetime as dt

con = sqlite3.connect('streets.db')
cur = con.cursor()
def creation():
    
    cur.execute("DROP TABLE IF EXISTS metadata")
    cur.execute("DROP TABLE IF EXISTS street_names")
    cur.execute("DROP TABLE IF EXISTS street_parts")
    cur.execute("DROP TABLE IF EXISTS street_part_coordinates")

    cur.execute("""
        CREATE TABLE metadata (
            creation_date TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE street_names (
            street_id TEXT PRIMARY KEY,
            street_name TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE street_parts (
            str_part_id INTEGER PRIMARY KEY,
            street_id TEXT NOT NULL,
            from_str_id INTEGER NOT NULL,
            to_str_id INTEGER NOT NULL,
            bbox_start_x REAL NOT NULL,
            bbox_start_y REAL NOT NULL,
            bbox_end_x REAL NOT NULL,
            bbox_end_y REAL NOT NULL,
            length_m REAL,
            FOREIGN KEY (street_id)
            REFERENCES street_names (street_id)
                ON UPDATE RESTRICT
                ON DELETE RESTRICT
        )
    """)

    cur.execute("""
        CREATE TABLE street_part_coordinates (
            str_part_coord_id INTEGER PRIMARY KEY,
            str_part_id INTEGER NOT NULL,
            x_coord REAL NOT NULL,
            y_coord REAL NOT NULL,
            FOREIGN KEY (str_part_coord_id)
            REFERENCES street_parts (str_part_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE
        )
    """)
    
    con.commit()
    
def read_raw_data():
    with open('../raw.json') as r:
        raw = json.load(r)

    street_names_with_duplicates = []
    street_parts = []
    street_part_coordinates = []
    for feat in raw['features']:  
        street_names_with_duplicates.append((
            feat['properties']['str'],
            feat['properties']['str_nr']
        ))
        street_parts.append((
            feat['properties']['objectid'], # str_part_id
            feat['properties']['str_nr'],   # street_id
            feat['properties']['von_str_nr'],
            feat['properties']['bis_str_nr'],
            feat['bbox'][0],
            feat['bbox'][1],
            feat['bbox'][2],
            feat['bbox'][3],
            feat['properties']['laenge_m']
        ))
        for seg in feat['geometry']['coordinates'][0]:
            street_part_coordinates.append((
                feat['properties']['str_nr'],
                seg[0], 
                seg[1]
            ))
    
    return (
        list(set(street_names_with_duplicates)),
        street_parts,
        street_part_coordinates
    )
    
def db_filling(street_names, street_parts, street_part_coordinates):
    timestamp = [str(dt.datetime.now()).replace(" ", "T")]
    cur.execute("INSERT INTO metadata VALUES(?)", timestamp)
    cur.executemany("INSERT INTO street_names VALUES(?,?)", 
        street_names)
    cur.executemany("INSERT INTO street_parts VALUES(?,?,?,?,?,?,?,?,?)",
        street_parts)
    cur.executemany("""
        INSERT INTO street_part_coordinates 
        (str_part_id, x_coord, y_coord) VALUES(?,?,?)
        """,
        street_part_coordinates)
    
    con.commit()
    
def reading():
    metadata = cur.execute("SELECT * FROM metadata").fetchall()
    street_names = cur.execute("SELECT * FROM street_names").fetchall()
    street_parts = cur.execute("SELECT * FROM street_parts").fetchall()
    street_part_coordinates = cur.execute("SELECT * FROM street_part_coordinates").fetchall()
    
    return (
        metadata,
        street_names,
        street_parts,
        street_part_coordinates
    )

if __name__ == "__main__":
    # street_names, street_parts, street_part_coordinates = read_raw_data()
    # creation()
    # db_filling(street_names, street_parts, street_part_coordinates)
    metadata, street_names, street_parts, street_part_coordinates = reading()
    

a = 0