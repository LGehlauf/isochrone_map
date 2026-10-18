using DataFrames,CSV,CairoMakie, Graphs

vel=2
function get_point_by_PID(points,PID)
    index=0
    for i=1:nrow(points)
        if points[i,:].PID==PID
            index=i
            break
        end
    end
    if index==0
        error("PID not found in points DataFrame")
    end
    return points[index,:]
end
function get_lines_by_PID(lines,PID)
    indices=[0]
    for i=1:nrow(lines)
        if lines[i,:].PID1==PID || lines[i,:].PID2==PID
            indices=[indices,i] 
        end
    end
    if lastindex(indices)==1
        error("PID not found in lines DataFrame")
    end
    return lines[indices,:]
end

function get_line_by_LID(lines,LID)
    index=0
    for i=1:nrow(lines)
        if lines[i,:].LID==LID
            index=i
            break
        end
    end
    if index==0
        error("LID not found in lines DataFrame")
    end
    return lines[index,:]
end
function line_distance(points,lines,LID)
    line=get_line_by_LID(lines,LID)
    point1=get_point_by_PID(points,line.PID1)
    point2=get_point_by_PID(points,line.PID2)
    distance=sqrt((point2.x-point1.x)^2+(point2.y-point1.y)^2)
    return distance
end
function plot_graph(points,lines)
    fig = Figure()#resolution = (800, 600))
    ax = Axis(fig[1, 1], xlabel = "X", ylabel = "Y", title = "Graph Plot")
    
    # Plot points
    scatter!(ax, points.x, points.y, color = :blue, label = "Points")
    
    # Plot lines
    for i in 1:nrow(lines)
        x_coords = [get_point_by_PID(points, lines.PID1[i]).x, get_point_by_PID(points, lines.PID2[i]).x]
        y_coords = [get_point_by_PID(points, lines.PID1[i]).y, get_point_by_PID(points, lines.PID2[i]).y]
        lines!(ax, x_coords, y_coords, color = :red, label = "Line $(i)")
    end
    
    Legend(fig[1, 2], ax)#axislegend(ax)
    display(fig)
end

function calc_distances(points,lines,PID)
    g=SimpleGraph(nrow(points))
    for i=1:nrow(lines)
        add_edge!(g,lines.PID1[i],lines.PID2[i])
    end
    weights=zeros(nrow(lines),nrow(lines))
    for i=1:nrow(lines)
        weights[lines.PID1[i],lines.PID2[i]]=line_distance(points,lines,lines.LID[i])
        weights[lines.PID2[i],lines.PID1[i]]=weights[lines.PID1[i],lines.PID2[i]]
    end
    res=dijkstra_shortest_paths(g,PID,weights)
    return res
end

function transform(points,distances,PID)
    times=distances./vel
    x0=get_point_by_PID(points,PID).x
    y0=get_point_by_PID(points,PID).y
    new_points=points 
    for i=1:nrow(points)
        luftlinie=sqrt((points.x[i]-x0)^2+(points.y[i]-y0)^2)
        if luftlinie==0
            luftlinie=1
        end
        new_points.x[i]=(points.x[i]-x0)/luftlinie*times[i]
        new_points.y[i]=(points.y[i]-y0)/luftlinie*times[i]

    end
    return new_points
end

function main()
    points=CSV.read("test_points.csv",DataFrame)
    lines=CSV.read("test_lines.csv",DataFrame)
    lines.d=zeros(nrow(lines))
    for i=1:nrow(lines)
        lines.d[i]=line_distance(points,lines,lines.LID[i])
    end
    println(lines)
    plot_graph(points,lines)
    res=calc_distances(points,lines,2)
    distances=res.dists
    new_points=transform(points,distances,2)
    println(new_points)
    plot_graph(new_points,lines)


end





