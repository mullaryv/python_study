
'''
Created on Oct 07, 2015

@author: Myullyari
'''

if __name__ == '__main__':
    import sys
    import time

    EPS = 0.00000001      # to help define a small vicinity of a point

    def non_blank (str_in) :
        return str_in !=""

    time_start = time.time()

    args_len = len(sys.argv)
    if (args_len < 3):
      print ("Error: usage:", sys.argv[0], "<polygon file> <test points file> [/d]")
      exit(-1)

    file_poly = open (sys.argv[1], 'r')
    file_points = open (sys.argv[2], 'r')

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
      if (l_pnt < 5): continue # skip invalid line

      p = ((point_lst[l_pnt-1] == "TRUE") or (point_lst[l_pnt-1] == "TRUE\n"))
      points.append ((float(point_lst[0]), float(point_lst[1]), p));


    num_points = len(points)
    print ("points to test:", num_points)
    if debug:
      for point in points: print ("  ", point)

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

    for point in (points):
        p_long = point[0]
        p_lat = point[1]
        if debug: print(point)

        # For each point loop over the all segments.
        # I will drow a vertical line at this point longitude and count
        # how many segments this line crosses BELOW point's latitude
        belongs = False              # in some cases a point does belng unconditionally
        cnt_intersections = 0
        LeftRight = 0 # -1 -- left, +1 -- right

        for s in range (num_segments):
            segment = segments[s]

            if debug: print ("\ts:", s, end="")

            # read GDC into individual numbers, I'll use them a lot
            start_long = segment[0][0]
            start_lat  = segment[0][1]
            end_long   = segment[1][0]
            end_lat    = segment[1][1]

            # 1. ignore segments which are completly on the left or right of a point's latitude
            if (((start_long < p_long) and (end_long < p_long)) or
                ((start_long > p_long) and (end_long > p_long))):
              cnt_simple += 1
              if debug: print (" left/right")
              continue


            # 2. ignore segment which is completly above a given point
            if (start_lat > p_lat) and (end_lat > p_lat):
              cnt_simple += 1
              if debug: print (" above")
              continue


            # 3. count a segment if it is below a given point (it certainly will be crossed)
            if ((start_lat < p_lat) and (end_lat < p_lat) and
                # exclude segments with vertices: they will be handled separately
                ((start_long < p_long) and (p_long < end_long) or
                 (start_long > p_long) and (p_long > end_long))):
              cnt_simple += 1
              cnt_intersections += 1
              if debug: print (" below +")
              continue


            # 4. Ignore verticals, if a point dosn't directly lie on it;
            #    this allows to avoid trigonometrical calculations issues later on
            if (abs(start_long - end_long) <= EPS):
              cnt_edge += 1
              if (((start_lat <= p_lat) and (p_lat <= end_lat))
                  or
                  ((start_lat >= p_lat) and (p_lat >= end_lat))):
                belongs = True
                LeftRight = 0
                cnt_skip += (num_segments - 1 - s)
                if debug: print (" edge-vertical +")
                break
              if debug: print (" edge-vertical")
              continue


            # If we're here, then a point is either within a rectangle with this segment as a diagonal,
            # or point's longitude is above/below segment's ends.
            
            # 5. When intersection occurs NOT at the vertex:
            #    need to find out if this point's longitude line crosses this segment
            #    above (should be ignored) or below (should be counted) point's latitude
            if ((start_long != p_long) and (end_long != p_long)):

              cnt_complex += 1
              k = segment[2]
              b = segment[3]

              intersec_lat = k*p_long + b
              if ((intersec_lat - EPS <= p_lat) and (intersec_lat + EPS >= p_lat)):  # a point is directly on the segment's edge
                belongs = True
                cnt_skip += (num_segments - 1 - s)
                if debug: print (" edge: true")
                break
              if (intersec_lat <= p_lat):       # a point is either on the segment or "above" it
                cnt_intersections += 1
                if debug: print (" edge +")
              else:
                if debug: print (" edge")


            # 6. Intersection occurs exactly on the vertex: two adjacent segments must have 
            #    same longitude at their start or end as a given point
            else:

              cnt_vertex += 1

              # a) Intersection occurs on the segment's start
              if (p_long == start_long):

                # quick check if a point is in fact on the vertex
                if (p_lat == start_lat):
                  if debug: print (" vertex-start: true")
                  belongs = True
                  LeftRight = 0
                  cnt_skip += (num_segments - 1 - s)
                  break

                # if intersection occurs above the vertex start, need to check previous segment
                if (p_lat > start_lat):

                  if ((LeftRight == 1) and (p_long > end_long)):
                    cnt_intersections += 1
                    LeftRight = 0
                    if debug: print (" vertex-start:right +")

                  if ((LeftRight == -1) and (p_long < end_long)): 
                    cnt_intersections += 1
                    LeftRight = 0
                    if debug: print (" vertex-start:left +")

                  # if we're at the segment's start and there was no previous intersection,
                  # then postpone the decision until the last segment is reached
                  else:
                    if debug: print (" vertex-start:zero")
                    if (p_long > end_long): FirstLeftRight = -1
                    else: FirstLeftRight = 1
                       
                else: # ignore, if point is under the vertex
                  if debug: print (" vertex-start")

                    
              # a) If intersection occurs at the vertex's end: need to set up a flag which side segent lies
              else:

                # quick check if a point lies on the vertex
                if (p_lat == end_lat):
                  belongs = True
                  LeftRight = 0
                  cnt_skip += (num_segments - 1 - s)
                  if debug: print (" vertex-end: true")
                  break

                # if a point lies over the vertex: need to check the previous segment
                if (p_lat > end_lat):
                  if (p_long > start_long):
                    LeftRight = -1
                    if debug: print (" vertex-end: left")
                  else: 
                    LeftRight = 1
                    if debug: print (" vertex-end: right")
                else:
                  if debug: print (" vertex-end")


        # final decision: point is outside of the polygon if number of intersections even 
        # check if there was an intersection on the corner between first and last segments
        if ((LeftRight != 0) and (LeftRight + FirstLeftRight == 0)):
          cnt_intersections += 1

        if (cnt_intersections % 2 == 1 or belongs):
          belongs = True
          if debug: print (" included")

        res_points.append((p_long, p_lat, point[2], belongs, cnt_intersections))
        # for segment in segments: -------------------------------------------

    # for point in (points): -------------------------------------------


#    print("\nresults:")
#    for point in res_points:
#      print(point)

    time_proc = time.time() - time_loaded
    print ("time processed: ", time_proc, "sec.")

    cnt_included = 0
    print("\ndifferences:")
    cnt_diff = 0
    for point in res_points:
      if (point[2] != point[3]):
        print (point)
        cnt_diff += 1
      if point[3]: cnt_included+=1

    print("\nsimple tests: ", cnt_simple)
    print("over the edge:  ", cnt_edge)
    print("complex tests:  ", cnt_complex)
    print("vertices:       ", cnt_vertex)
    print("skipped:        ", cnt_skip)
    print("\npoints included:", cnt_included, " ("+str(num_points)+ ")")
    print("      different:", cnt_diff)
    time_fin = time.time() - time_start
    print("time finished:  ", time_fin, "sec.")
