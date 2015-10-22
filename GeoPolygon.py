'''
Created on Oct 07, 2015

@author: Myullyari
'''

if __name__ == '__main__':
    import sys
    import math
    import time

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


    time_start = time.time()

    args_len = len(sys.argv)
    if (args_len < 3):
      print ("Error: usage:", sys.argv[0], "<polygon file> <test points file> [/d]")
      exit(-1)

    file_poly = open (sys.argv[1], 'r')
    file_points = open (sys.argv[2], 'r')

#    file_poly = open ("polygon.wkt", 'r')
#    file_points = open ("x_points_0.txt", 'r')

    debug = (args_len > 3) and (sys.argv[3] == "/d")
    # ==================================================================
    #                     create a list of segments                    
    # ==================================================================
    
    # read a polygon from a file; must be in WKT format    
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

    if debug:
      print ("\npolygon vertices:")
      for i in range(num_poly_points):
        print ("  ", i, ":", coords_pairs[i])

    segments = list()

    # a list of segments; each item is a pair of tuples: start and end of a segment
    for i in range(num_segments):
        point_start = tuple(list (map (float, filter (non_blank, coords_pairs[i].split(' ')))))
        point_end   = tuple(list (map (float, filter (non_blank, coords_pairs[i+1].split(' ')))))
        
        # calculate line koefficient in advance (y = kx+b, k -- tangent of incline, b -- indent)  
        start_long = point_start[0]
        start_lat  = point_start[1]
        end_long   = point_end[0]
        end_lat    = point_end[1]

        dy = (end_lat - start_lat)
        dx = (end_long - start_long)
        k = 0
        b=0 
        if (abs(dx) > EPS):
          k = dy / dx
          b = end_lat - end_long*k

        segments.append ((point_start, point_end, k, b))

    if debug:
      print ("\nsegments:")
      for i in range(num_segments):
        print ("  ", i, ":", segments[i])
 

    # ==================================================================
    # create a list of points we want to test for being inside a polygon
    # ==================================================================
    points = [];

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
    if debug:
      for point in points:
        print ("  ", point)
    time_loaded = time.time()
    print ("time loaded: ", time_loaded - time_start, "sec.")
    

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
        if debug: print(point)
      
        # For each point loop over the all segments.
        # I will drow a vertical line at this point longitude and count
        # how many segments this line crosses BELOW point's latitude
        belongs = False
        cnt_intersections = 0
        skip_segment = -1

        for s in range (num_segments):
            segment = segments[s]

            if debug: print ("\ts:", s, end="")        
            if (s == skip_segment):  # hit vertex in the previos step and already counted or dismissed
              if debug: print (" skip: ", skip_segment)
              skip_segment = -1
              cnt_skip += 1
              continue  
        
            # read GDC into individual numbers, I'll use them a lot
            start_long = segment[0][0]
            start_lat  = segment[0][1]
            end_long   = segment[1][0]
            end_lat    = segment[1][1]
        
            #first, few trivial tests if a vertical line certanly crosses or misses current segment

            # 1. ignore segments which are completly on the left or right of a point's latitude
            if (((start_long < p_long) and (end_long < p_long)) or
                ((start_long > p_long) and (end_long > p_long))):
              cnt_simple += 1
              if debug: print (" simple-1")
              continue  

              
            # 2. ignore segment which is completly above a given point
            if (start_lat > p_lat) and (end_lat > p_lat):
              cnt_simple += 1
              if debug: print (" simple-2")        
              continue  


            # 3. count a segment if it is below a given point (it certainly will be crossed)
            if ((start_lat < p_lat) and (end_lat < p_lat) and
                # exclude segments with vertices: they will be handled separately 
                ((start_long < p_long) and (p_long < end_long) or
                 (start_long > p_long) and (p_long > end_long))):
              cnt_simple += 1
              cnt_intersections += 1
              if debug: print (" simple-3 +")
              continue  

              
            # if we're here, then a point is either withing a rectangle with this segment as a diagonal,
            # or point's longitude is crossing the vertex.
            # We need to find out if this point's longitude line crosses this segment
            # above (should be ignored) or below (should be counted) point's latitude
 
            # 4. I will ignore...
            # this allows to avoid trigonometrical calculations issues later on
            if (abs(start_long - end_long) <= EPS):
              if (((start_lat <= p_lat) and (p_lat <= end_lat))
                  or  
                  ((start_lat >= p_lat) and (p_lat >= end_lat))):
                belongs = True
                break
#              cnt_intersections += 1
              cnt_edge += 1
              if debug: print (" edge-vertical +")
              continue  
   

            # 5. when intersection occurs NOT at the vertex:
            #      (need to check both cases, since I don't know the direction I'm traversing the polygon)
#            if (((start_long > p_long) and (p_long > end_long)) or
#                ((start_long < p_long) and (p_long < end_long))):

            if ((start_long != p_long) and (end_long != p_long)):
              
              k = segment[2]
              b = segment[3]

              intersec_lat = k*p_long + b
              if ((intersec_lat - EPS <= p_lat) and (intersec_lat + EPS >= p_lat)):  # a point is directly on the segment's edge
                belongs = True
                if debug: print (" edge-complex true")
                cnt_complex += 1
                break  
              if (intersec_lat <= p_lat):       # a point is either on the segment or "above" it
                cnt_intersections += 1
                if debug: print (" cross +")
              else: 
                if debug: print (" cross")
              cnt_complex += 1


            # 6. intersection occurs EXACTLY on the vertex; 
            #    this means that two adjacent segments must have 'p_long' as a longitude 
            #    of their start or end point (i.e. "touch" p_long vertical line) 
            else: 
              '''
              # a) quick check if the latitudes are the same
              if (end_lat == p_lat):
                belongs = True
                cnt_vertex += 1
                if debug: print (" vertex-on") 
#TODO: can skip next here       
#                print ("start_lat", start_lat)        
#                print ("end_lat", end_lat)        
#                print ("p_lat", p_lat)        
#                print ("EPS", EPS)        
                break
              '''
            
              if (start_long == p_long):
#                if (start_lat == p_lat):
#                  if debug: print (" vertex-start") 
#                  belongs = True
#                  break  
                continue

              # a) quick check if a point is below the vertex
              if (end_lat > p_lat):
                if debug: print (" vertex-below") 
#TODO: can skip next here       
                cnt_vertex += 1
                continue

              
              # a) quick check if the latitudes are the same
              if (end_lat == p_lat):
                belongs = True
                cnt_vertex += 1
                if debug: print (" vertex-on") 
#TODO: can skip next here       
#                print ("start_lat", start_lat)        
#                print ("end_lat", end_lat)        
#                print ("p_lat", p_lat)        
#                print ("EPS", EPS)        
                break

              # ... i.e. points latitude is above the end of the segment (vertex)
                  
              # I will count vertex-intersection only if adjacent segments lie on different 
              # sides of the p_long vertical line
              
              # b) Find adjacent segment: I don't know the direction I'm traversing 
              #    the polygon, so it could be either previous or next one.
              s_next = s + 1

              if (s_next == num_segments): s_next = 0
 
              # Note, it will be skipped on the next loop iteration
              adj_segment = segments[s_next]
              skip_segment = s_next

              # check if next segment is vertical; if it is, I will just ignore it and go for the next one  
              if (abs(adj_segment[0][0] - adj_segment[1][0]) <= EPS): #TODO: read from the list
                cnt_edge += 1
                s_next += 1
                if (s_next == num_segments): s_next = 0
                adj_segment = segments[s_next]
                skip_segment = s_next
                s += 1 
                if debug: 
                  print (" vertex-vertical")
                  print ("     skip:", skip_segment)
                  print ("     next:", s_next)

              adj_start_long = adj_segment[0][0]
              adj_start_lat  = adj_segment[0][1]
              adj_end_long   = adj_segment[1][0]
              adj_end_lat    = adj_segment[1][1]

#TODO: check if using the vicinity of the point makes more sense
              # a) quick check if the latitudes are the same
              if (adj_start_lat == p_lat):
                belongs = True
                cnt_vertex += 1
                if debug: print (" vertex-start +") 
#TODO: can skip next here       
#                print ("start_lat", start_lat)        
#                print ("end_lat", end_lat)        
#                print ("p_lat", p_lat)        
#                print ("EPS", EPS)        
                break

              # d) else intersection is at the end of this segment 
              if (((p_long > start_long) and (p_long < adj_end_long))
                  or  
                  ((p_long < start_long) and (p_long > adj_end_long))):
                  cnt_intersections += 1
                  if debug:
                      print (" vertex-end +")

                      print ("start_long", start_long)        
                      print ("start_lat", start_lat)        
                      print ("end_long", end_long)        
                      print ("end_lat", end_lat)        
                      print ("adj_start_long", adj_start_long)        
                      print ("adj_end_long", adj_end_long)        
                      print ("p_lat", p_lat)        
              else:        
                if debug: print (" vertex-end")

              cnt_vertex += 1

#            print("s:", s, "st:", cnt_simple, "edge:", cnt_edge, "ct:", cnt_complex, "vertex:", cnt_vertex)

        # final decision:
        # if number of intersections even, then this point is outside of the polygon
#        print (" intr:", cnt_intersections, "div:", cnt_intersections % 2)
        if (cnt_intersections % 2 == 1 or belongs):
          belongs = True
          cnt_included += 1
          if debug: print (" included")

        res_points.append((p_long, p_lat, point[2], belongs, cnt_intersections))
        # for segment in segments: -------------------------------------------
      
    # for point in (points): -------------------------------------------


#    print("\nresults:")
#    for point in res_points:
#      print(point) 

    time_proc = time.time() - time_loaded
    print ("time processed: ", time_proc, "sec.")

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
    print("vertices:       ", cnt_vertex)
    print("skipped:        ", cnt_skip)
    print("points included:", cnt_included, " ("+str(num_points)+ ")")
    print("      different:", cnt_diff)
    time_fin = time.time() - time_start
    print("time finished:  ", time_fin, "sec.")
