import pandas as pd
from shapely import from_wkb
import sqlite3
import json
import datetime as dt


# TODO: build db with useful data

def info():
    tableNames = osmCur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
    for table in tableNames:
        tableName = str(table[0])
        print(tableName)
        print("-----------")
        columns = osmCur.execute(f"PRAGMA table_info({tableName})").fetchall()
        for col in columns:
            print(f"{col[0]:<8}{col[1]:<32}{col[2]:<8}")
            
def readOsmDb():
    osmCur = sqlite3.connect('openstreet_raw.gpkg').cursor()
    osmLines = osmCur.execute("SELECT * FROM lines WHERE geom IS NOT NULL").fetchall()
    # osmPoints = osmCur.execute("SELECT * FROM points").fetchall()

    counter = 0
    lines = []
    segments = []
    lineColumnNames = ["id", "geom", "osm_id", "name", "highway", "waterway", "aerialway", "barrier", "man_made", "railway", "z_order", "other_tags"]
    for row in osmLines:
        counter += 1
        rowDict = {}
        for i, cell in enumerate(row):
            if i == 1:
                coords = from_wkb(cell[40:]).coords._coords
                for i, coord in enumerate(coords):
                    segments.append({
                        "osm_line_id": row[2], 
                        "count": i,
                        "x": coord[0],
                        "y": coord[1]
                    })
            else: 
                rowDict[lineColumnNames[i]] = cell
                # rowDict = {lineColumnNames[i]: cell}
        lines.append(rowDict)
        
        if counter > 1000: break
        
    return lines


def create_db():
    resCur.execute("DROP TABLE IF EXISTS street_names")
    resCur.execute("DROP TABLE IF EXISTS street_parts")
    resCur.execute("DROP TABLE IF EXISTS street_part_coordinates")

    resCur.execute("""
        CREATE TABLE lines (
            lineId TEXT PRIMARY KEY,
             TEXT
        )
    """)
    
    resCur.execute("""
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

    resCur.execute("""
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
    
    resCon.commit()

if __name__ == "__main__":
    resCon = sqlite3.connect('streets.db')
    resCur = resCon.cursor()
    
    lines = readOsmDb()

    
    """
        lines
        -----------
        0       id                              INTEGER 
        1       geom                            LINESTRING
        2       osm_id                          TEXT    
        3       name                            TEXT    
        4       highway                         TEXT    
        5       waterway                        TEXT    
        6       aerialway                       TEXT    
        7       barrier                         TEXT    
        8       man_made                        TEXT    
        9       railway                         TEXT    
        10      z_order                         MEDIUMINT
        11      other_tags                      TEXT   
        points
        -----------
        0       id                              INTEGER 
        1       geom                            POINT   
        2       osm_id                          TEXT    
        3       name                            TEXT    
        4       barrier                         TEXT    
        5       highway                         TEXT    
        6       ref                             TEXT    
        7       address                         TEXT    
        8       is_in                           TEXT    
        9       place                           TEXT    
        10      man_made                        TEXT    
        11      other_tags                      TEXT    
    """
    
