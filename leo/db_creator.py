import sqlite3
import json
import datetime as dt
from shapely import from_wkb
import svgwrite
from svgwrite import mm
import numpy as np

resCon = sqlite3.connect('streets.db')
resCur = resCon.cursor()

def create_db():
    resCur.execute("DROP TABLE IF EXISTS metadata")
    resCur.execute("DROP TABLE IF EXISTS street_names")
    resCur.execute("DROP TABLE IF EXISTS street_parts")
    resCur.execute("DROP TABLE IF EXISTS street_part_coordinates")

    resCur.execute("""
        CREATE TABLE metadata (
            creation_date TEXT
        )
    """)
    
    resCur.execute("""
        CREATE TABLE street_names (
            street_id TEXT PRIMARY KEY,
            street_name TEXT
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
    
def read_lines_openstreetmap():
    osmCon = sqlite3.connect('openstreet_raw.gpkg')
    osmCur = osmCon.cursor()
    
    tableNames = osmCur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()
    tables = []
    
    if False:
        for table in tableNames:
            tableName = str(table[0])
            print(tableName)
            print("-----------")
            columns = osmCur.execute(f"PRAGMA table_info({tableName})").fetchall()
            for col in columns:
                # print('{}{}{}'.format(col[0].ljust(8),col[1].ljust(8),col[2].ljust(8)))
                print(f"{col[0]:<8}{col[1]:<32}{col[2]:<8}")
            a = 0
            # tables.append({
            #     tableName : osmCur.execute(f"SELECT * FROM {tableName}").fetchall()
            # })
        
    lines = osmCur.execute("SELECT * FROM lines WHERE geom IS NOT NULL").fetchall()
    # minMax = osmCur.execute("SELECT * FROM gpkg_contents").fetchall()
    
    osmCon.close()
    return lines
    
def read_raw_data_leipzig_official():
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
    resCur.execute("INSERT INTO metadata VALUES(?)", timestamp)
    resCur.executemany("INSERT INTO street_names VALUES(?,?)", 
        street_names)
    resCur.executemany("INSERT INTO street_parts VALUES(?,?,?,?,?,?,?,?,?)",
        street_parts)
    resCur.executemany("""
        INSERT INTO street_part_coordinates 
        (str_part_id, x_coord, y_coord) VALUES(?,?,?)
        """,
        street_part_coordinates)
    
    resCon.commit()
    
def read_db():
    metadata = resCur.execute("SELECT * FROM metadata").fetchall()
    street_names = resCur.execute("SELECT * FROM street_names").fetchall()
    street_parts = resCur.execute("SELECT * FROM street_parts").fetchall()
    street_part_coordinates = resCur.execute("SELECT * FROM street_part_coordinates").fetchall()
    
    return (
        metadata,
        street_names,
        street_parts,
        street_part_coordinates
    )

def drawLinesSvg(lines, min_x, min_y, max_x, max_y):
    svg = svgwrite.Drawing('1.svg', profile='tiny')
    color = svgwrite.rgb(10, 10, 16, '%')
    sv = 1000 # scaling value
    borderStrokeWidth = 10
    strokeWidth = 0.1
    svg.add(svg.line(
        ((0          )      , (0          )      ), 
        ((max_x-min_x)*sv*mm, (0          )      ), stroke=color, stroke_width=borderStrokeWidth))
    svg.add(svg.line(
        ((max_x-min_x)*sv*mm, (0          )      ), 
        ((max_x-min_x)*sv*mm, (max_y-min_y)*sv*mm), stroke=color, stroke_width=borderStrokeWidth))
    svg.add(svg.line(
        ((max_x-min_x)*sv*mm, (max_y-min_y)*sv*mm), 
        ((0          )      , (max_y-min_y)*sv*mm), stroke=color, stroke_width=borderStrokeWidth))
    svg.add(svg.line(
        ((0          )      , (max_y-min_y)*sv*mm), 
        ((0          )      , (0          )      ), stroke=color, stroke_width=borderStrokeWidth))

    counter = 0
    for line in lines:
        l = from_wkb(line[1][40:])
        # print(l.coords.xy[0],l.coords.xy[1])
        if len(l.coords._coords) == 2:
            svg.add(svg.line(
                (l.coords._coords[0]-np.array([min_x,min_y]))*sv*mm, 
                (l.coords._coords[1]-np.array([min_x,min_y]))*sv*mm, 
                stroke=color, stroke_width=strokeWidth
            ))
        else:
            path = svgwrite.path.Path(stroke=color, stroke_width=strokeWidth)
            string = ('M ' + str((l.coords._coords[0]  -np.array([min_x,min_y]))*sv*mm)) # buggy, TODO
            # string = ((l.coords._coords[0]  -np.array([min_x,min_y]))*sv*mm)
            path.push(string)
            for i in range(1, len(l.coords._coords)):
                string = ('L ' + (l.coords._coords[i]  -np.array([min_x,min_y]))*sv*mm )
                path.push(string)
                
            svg.add(path)

        counter += 1
        if counter > 20: break
        
    svg.save()
    a = 0
        

if __name__ == "__main__":
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
    """
    min_x, min_y, max_x, max_y = 10.73447889999999, 48.6165844, 13.05009109999999, 51.7994927
    lines = read_lines_openstreetmap()
    drawLinesSvg(lines, min_x, min_y, max_x, max_y)

    
    
    # street_names, street_parts, street_part_coordinates = read_raw_data_leipzig_official()
    # creation()
    # db_filling(street_names, street_parts, street_part_coordinates)
    # metadata, street_names, street_parts, street_part_coordinates = read_db()
    

a = 0