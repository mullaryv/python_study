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
    #str_poly = file_poly.read()
    '''
    for line in file_poly:
      if (line[0] == '#'):      
        continue
      else: 
        str_poly = line
        break 
    '''
    str_poly = ""
    while True:
      str_poly = file_poly.readline()
      if (str_poly[0] != "#"): break
   
    str_coords = str_poly.replace ("POLYGON", "")
    str_coords = str_coords.replace ("((", "")
    str_coords = str_coords.replace ("))", "")

    # a list of GDC points
    coords_pairs = str_coords.split(",")
    num_poly_points = len(coords_pairs)
    num_segments = num_poly_points - 1;    # must be closed polygon
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

    '''
    file_points = open ("points.txt", 'r')  # a pair of GDC point a line
    for line in file_points:
        points.append (tuple(list (map (float, filter (non_blank, line.split(' '))))))
    '''

    file_points = open ("points_ext.txt", 'r')  # a pair of GDC point a line
    for line in file_points:
      point_lst = list (filter (non_blank, line.split('\t')))
#      print (point_lst)

      p = False
      if ((point_lst[4] == "TRUE") or (point_lst[4] == "TRUE\n")):
        p = True
      points.append ((float(point_lst[0]), float(point_lst[1]), p));

        
    num_points = len(points)
    print ("points to check:", num_points)
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
    
    for point in (points):
      p_long = point[0]
      p_lat = point[1]


      # For each point: a loop over the segments.
      # I will drow a vertical line at this point longitude and count
      # how many segments this line crosses BELOW point's latitude
      belongs = False
      cnt_intersections = 0
      skip_segment = False

#      m = 0      
      for segment in segments:
        if skip_segment:
          skip_segment = False
          cnt_skip += 1
          continue  
        
        # read GDC into individual numbers, I'll use them a lot
        start_long = segment[0][0]
        start_lat  = segment[0][1]
        end_long   = segment[1][0]
        end_lat    = segment[1][1]
        
        #first, few trivial tests if a vertical line certanly crosses or misses current segment
        do_test = True

        # 1. ignore segment which is completly on the left or right of a given point
        if (((start_long < p_long) and (end_long < p_long)) or
            ((start_long > p_long) and (end_long > p_long))):
          do_test = False
          cnt_simple += 1

        # 2. ignore segment which is completly up a given point
        if do_test and (start_lat > p_lat) and (end_lat > p_lat):
          do_test = False
          cnt_simple += 1


        # 3. count a segment if it is below a given point (it certainly will be crossed)
        if do_test and (start_lat < p_lat) and (end_lat < p_lat):
          do_test = False
          cnt_simple += 1
          cnt_intersections += 1

        # if still "do_test", then a point is withing a rectangle with this segment as a diagonal,
        # and we need to find out if this point's longitude line crosses this segment
        # above (should be ignored) or below (should be counted) point's latitude

        # 4. I will assume we do cross a segment which is almost vertical;
        # this allows to avoid trigonometrical calculations issues later on
        if do_test and (abs(start_long - end_long) < EPS):
          cnt_intersections += 1
          cnt_edge += 1
          do_test = False


        if do_test:

          # 5. when intersection occurs NOT at the vertex:
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

          # 6. intersection occurs EXACTLY on the vertex 
          else: 
            # I will count vertex-intersection only if both left and right points 
            # from the vicinity of a given point intersect left/right segments
            cnt_vertex += 1
            skip_segment = True  

#        print("m:", m, "st:", cnt_simple, "edge:", cnt_edge, "ct:", cnt_complex, "vertex:", cnt_vertex)
#        m += 1


        # final decision:
        # if number of intersections even, then this point is outside of the polygon
        if (cnt_intersections % 2 == 1):
          belongs = True

      res_points.append((p_long, p_lat, point[2], belongs))
      # for segment in segments: -------------------------------------------
      
    # for point in (points): -------------------------------------------


      
    print("\nresults:")
    for point in res_points:
      print(point) 


    print("\nsimple tests: ", cnt_simple)
    print("over the edge:", cnt_edge)
    print("complex tests:", cnt_complex)
    print("corners:      ", cnt_vertex)
    print("skipped:      ", cnt_skip)
