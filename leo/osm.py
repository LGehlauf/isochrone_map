import svgwrite
from svgwrite import mm
import sqlite3
from shapely import from_wkb
import numpy as np

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

def drawLinesSvg(lines, min_x, min_y, max_x, max_y):
    dwg = svgwrite.Drawing('1.svg', profile='tiny')
    color = svgwrite.rgb(10, 10, 16, '%')
    sv = 1000 # scaling value
    borderStrokeWidth = 10
    strokeWidth = 0.1
    dwg.add(dwg.line(
        ((0          )      , (0          )      ), 
        ((max_x-min_x)*sv*mm, (0          )      ), stroke=color, stroke_width=borderStrokeWidth))
    dwg.add(dwg.line(
        ((max_x-min_x)*sv*mm, (0          )      ), 
        ((max_x-min_x)*sv*mm, (max_y-min_y)*sv*mm), stroke=color, stroke_width=borderStrokeWidth))
    dwg.add(dwg.line(
        ((max_x-min_x)*sv*mm, (max_y-min_y)*sv*mm), 
        ((0          )      , (max_y-min_y)*sv*mm), stroke=color, stroke_width=borderStrokeWidth))
    dwg.add(dwg.line(
        ((0          )      , (max_y-min_y)*sv*mm), 
        ((0          )      , (0          )      ), stroke=color, stroke_width=borderStrokeWidth))

    counter = 0
    for line in lines:
        l = from_wkb(line[1][40:])
        # print(l.coords.xy[0],l.coords.xy[1])
        if len(l.coords._coords) == 2:
            dwg.add(dwg.line(
                (l.coords._coords[0]-np.array([min_x,min_y]))*sv*mm, 
                (l.coords._coords[1]-np.array([min_x,min_y]))*sv*mm, 
                stroke=color, stroke_width=strokeWidth
            ))
        else:
            x = (l.coords._coords[0][0] - min_x) * sv
            y = (l.coords._coords[0][1] - min_y) * sv
            string = ('M ' + str(x) + "," + str(y)) 
            for i in range(1, len(l.coords._coords)):
                x = (l.coords._coords[i][0] - min_x) * sv
                y = (l.coords._coords[i][1] - min_y) * sv
                string += (' L ' + str(x) + "," + str(y))
                a = 0
            path = dwg.path(
                d=string,
                stroke=color, 
                stroke_width=strokeWidth,
                fill = "none"
            )
            dwg.add(path)

        counter += 1
        if counter > 20: break
        
    dwg.save()
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
