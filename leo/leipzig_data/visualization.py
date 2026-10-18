import json
import plotly.graph_objects as go
import numpy as np


with open('../raw.json') as r:
    raw = json.load(r)
    
fig = go.Figure()
cleaned = []

x = []; y = []; names = []
    
for feat in raw['features']:

    for seg in feat['geometry']['coordinates'][0]:
        x.append(seg[0])
        y.append(seg[1])
        names.append(feat['properties']['str'])
        
        cleaned.append({
            'objectid': feat['properties']['objectid'],
            'str_nr': feat['properties']['str_nr'],
            'von_str_nr': feat['properties']['von_str_nr'],
            'bis_str_nr': feat['properties']['bis_str_nr'],
            'x': seg[0],
            'y': seg[1],
            'str':feat['properties']['str']
        })
        
    x.append(np.nan); y.append(np.nan); names.append(np.nan)
        
fig.add_trace(go.Scatter(
    x=x, y=y, mode="lines", 
    customdata=names, 
    hovertemplate="%{customdata}<extra></extra>",
))
fig.update_layout(template = "plotly_dark")

fig.show()

a = 0
