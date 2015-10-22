'''
Created on Oct 07, 2015

@author: Myullyari
'''

if __name__ == '__main__':
    import math

    EARTH_RAD = 3959.0                  # mean Earth radius [miles]
    EARTH_CIRC = 2*math.pi*EARTH_RAD    # equator and meridians circumference [miles]
    DEGREE_LAT = EARTH_CIRC / 360.0     # ~69.1 -- geodesical length of 1 degree [miles]
    rad = math.pi / 180.0               # coefficient for converting degrees to radians

    EPS = 0.00000001      # to help define a small vicinity of a point

    # geo-desic distance between two points [miles]
    def distance (lat1, lon1, lat2, lon2) :
        _cos = math.cos ((90 - lat2)*rad) * math.cos ((90 - lat1)*rad) + math.sin ((90 - lat2)*rad) * math.sin ((90 - lat1)*rad) * math.cos ((lon2 - lon1)*rad)
        return math.acos (_cos)*EARTH_RAD

    def non_blank (str_in) :
        return str_in !=""



    # ==================================================================
    #                     create a list of segments                    
    # ==================================================================
    
    # read a polygon from a file; must be in WKT format    
    file_poly = open ("polygon.wkt", 'r')

    str_poly = "#"
    while (str_poly[0] == "#"):                #comments start from '#'
      str_poly = file_poly.readline()
   
    p = str_poly.find("POLYGON((")
    if (p == -1):
      print ("Error: invalid polygon")
      exit(-100)

    str_coords = str_poly[p+9:]
    str_coords = str_coords.replace ("))", "")

    # a list of GDC points
    coords_pairs = str_coords.split(",")
    num_poly_points = len(coords_pairs)
    num_segments = num_poly_points - 1;        # must be closed polygon
    print ("points in polygon: ", num_poly_points)
    print ("number of segments:", num_segments)

    #print ("polygon points:")
    #for i in range(num_poly_points):
    #    print (i, ": ", coords_pairs[i])

    segments = list()

    # a list of segments; each item is a pair of tuples: start and end of a segment
    for i in range(num_segments):
        point_start = tuple(list (map (float, filter (non_blank, coords_pairs[i].split(' ')))))
        point_end   = tuple(list (map (float, filter (non_blank, coords_pairs[i+1].split(' ')))))
        segments.append ((point_start, point_end))

#    print ("\nsegments:")
#    for i in range(num_segments):
#        print ("seg", i, ": ", segments[i])
 

    # ==================================================================
    # create a list of points we want to test for being inside a polygon
    # ==================================================================
    points = [];

#    file_points = open ("x_points_0.txt", 'r')   # a pair of GDC point a line
#    file_points = open ("x_points_1.txt", 'r')   # a pair of GDC point a line
#    file_points = open ("x_points_2.txt", 'r')   # a pair of GDC point a line
#    file_points = open ("x_points_3.txt", 'r')   # a pair of GDC point a line
#    file_points = open ("x_points_4.txt", 'r')   # a pair of GDC point a line
    file_points = open ("x_points_500.txt", 'r')   # a pair of GDC point a line
    for line in file_points:
      point_lst = list (filter (non_blank, line.split('\t')))
      l_pnt = len(point_lst)
      if (l_pnt < 5): continue
#      print (point_lst)

      p = False
      if ((point_lst[l_pnt-1] == "TRUE") or (point_lst[l_pnt-1] == "TRUE\n")):
        p = True
      points.append ((float(point_lst[0]), float(point_lst[1]), p));

        
    num_points = len(points)
    print ("points to test:", num_points)
#    for point in points:
#        print (point)
    

    # ==================================================================
    # Main loop
    # ==================================================================
    res_points = []

    # some counts for stat/debug 
    cnt_simple = 0
    cnt_complex = 0
    cnt_edge = 0
    cnt_vertex = 0
    cnt_skip = 0
    cnt_included = 0
    
    for point in (points):
        p_long = point[0]
        p_lat = point[1]
#        print(point)
      
        # For each point loop over the all segments.
        # I will drow a vertical line at this point longitude and count
        # how many segments this line crosses BELOW point's latitude
        belongs = False
        cnt_intersections = 0
        skip_segment = -1

        for s in range (num_segments):
            segment = segments[s]

#            print ("s:", s, end=" ")        
            if (s == skip_segment):  # hit vertex in the previos step and already counted or dismissed
              skip_segment = -1
              cnt_skip += 1
              continue  
        
            # read GDC into individual numbers, I'll use them a lot
            start_long = segment[0][0]
            start_lat  = segment[0][1]
            end_long   = segment[1][0]
            end_lat    = segment[1][1]
        
            #first, few trivial tests if a vertical line certanly crosses or misses current segment

            # 1. ignore segment which is completly on the left or right of a given point
            if (((start_long < p_long) and (end_long < p_long)) or
                ((start_long > p_long) and (end_long > p_long))):
              cnt_simple += 1
#              print (" simple 1", end=" ")        
              continue  

            # 2. ignore segment which is completly up a given point
            if (start_lat > p_lat) and (end_lat > p_lat):
              cnt_simple += 1
#              print (" simple 2", end=" ")        
              continue  


            # 3. count a segment if it is below a given point (it certainly will be crossed)
            if (start_lat < p_lat) and (end_lat < p_lat):
              cnt_simple += 1
              cnt_intersections += 1
#              print (" simple 3", end=" ")
              continue  

            # if still "do_test", then a point is withing a rectangle with this segment as a diagonal,
            # and we need to find out if this point's longitude line crosses this segment
            # above (should be ignored) or below (should be counted) point's latitude

            # 4. I will assume we do cross a segment which is almost vertical;
            # this allows to avoid trigonometrical calculations issues later on
            if (abs(start_long - end_long) < EPS):
              cnt_intersections += 1
              cnt_edge += 1
#              print (" edge", end=" ")
              continue  


            # 5. when intersection occurs NOT at the vertex:
            #      (need to check both cases, since I don't know the direction I'm traversing the polygon)
            if (((start_long > p_long) and (end_long < p_long)) or
                ((start_long < p_long) and (end_long > p_long))):
          
              #y = kx+b, k -- tangent of incline, b -- indent
              dy = (end_lat - start_lat)
              dx = (end_long - start_long)
              k = dy / dx
              b = end_lat - end_long*k
              intersec_lat = k*p_long + b
              if (intersec_lat <= p_lat):       # a point is either on the segment or "above" it
                cnt_intersections += 1
              cnt_complex += 1
              '''
              print ("\n          dy:", dy)
              print ("          dx:", dx)
              print ("           k:", k)
              print ("           b:", b)
              print ("     int_lat:", intersec_lat)
              '''

            # 6. intersection occurs EXACTLY on the vertex 
            else: 
              # I will count vertex-intersection only if both left and right points 
              # from the vicinity of a given point intersect left/right segments
              cnt_vertex += 1
              skip_segment = s + 1                 # skip next segment
              if (s == 0):
                skip_segment = num_segments - 1

#            print("s:", s, "st:", cnt_simple, "edge:", cnt_edge, "ct:", cnt_complex, "vertex:", cnt_vertex)

            # final decision:
            # if number of intersections even, then this point is outside of the polygon
#        print (" intr:", cnt_intersections, "div:", cnt_intersections % 2)
        if (cnt_intersections % 2 == 1):
          belongs = True
          cnt_included += 1

        res_points.append((p_long, p_lat, point[2], belongs, cnt_intersections))
        # for segment in segments: -------------------------------------------
      
    # for point in (points): -------------------------------------------


#    print("\nresults:")
#    for point in res_points:
#      print(point) 

    #TODO: find a way to use filter
    print("\ndifferences:")
    cnt_diff = 0
    for point in res_points:
      if (point[2] != point[3]):
        print (point) 
        cnt_diff += 1
        
    print("\nsimple tests: ", cnt_simple)
    print("over the edge:  ", cnt_edge)
    print("complex tests:  ", cnt_complex)
    print("corners:        ", cnt_vertex)
    print("skipped:        ", cnt_skip)
    print("points included:", cnt_included, " (", num_points, ")")
    print("      different:", cnt_diff, " (", num_points, ")")
