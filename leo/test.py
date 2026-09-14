import svgwrite
from svgwrite import mm

def drawLinesSvg():
    min_x, min_y, max_x, max_y = 10.73447889999999, 48.6165844, 13.05009109999999, 51.7994927
    svg = svgwrite.Drawing('test.svg', profile='tiny')
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

    pathString = ('M 10,20 ' + 'L 20,30 ' + 'Z')
    path = svg.path(
        d=pathString,
        stroke=color, 
        stroke_width=strokeWidth
    )
    svg.add(path)
        
    svg.save()
    a = 0

if __name__ == "__main__":
    drawLinesSvg()