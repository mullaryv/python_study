'''
Created on Jun 17, 2014

@author: Myullyari
'''

if __name__ == '__main__':
    import math

    EARTH_RAD = 3959.0                  # mean Earth radius [miles]
    EARTH_CIRC = 2*math.pi*EARTH_RAD    # equator and meridians circumference [miles]
    DEGREE_LAT = EARTH_CIRC / 360.0     # ~69.1 -- geodesical length of 1 degree [miles] 
    rad = math.pi / 180.0               # coefficient for converting degrees to radians

    GRID=100.0                          # each cell is 1/100 of a degree
    #GRID=10.0                           # each cell is 1/10 of a degree
    grid_size = 1.0 / GRID              # [degree]

    # Function: quadrant x-y number by coordinate
    def quadrant (coord) :
        return int(math.floor(coord*GRID))

 
    # geo-desic distance between two points [miles]
    def distance (lat1, lon1, lat2, lon2) :
        _cos = math.cos ((90 - lat2)*rad) * math.cos ((90 - lat1)*rad) + math.sin ((90 - lat2)*rad) * math.sin ((90 - lat1)*rad) * math.cos ((lon2 - lon1)*rad)
        return math.acos (_cos)*EARTH_RAD


    # Returns a longitude  of an intersection of circumference with a given latitude;
    # this is needed to find out the boundaries of a grid, to save some calculations.
    def longitudeDistance (lat, c_lat, c_long, radius) :

        # Calculations on the sphere are more precise, and don't seem to have a performance impact,
        # but so far I prefer more simple Cartezian formula;
        # in both cases there's an uncertainty in the proximity of the Poles (division by zero).
        '''
        # ------------- on the plane ------------- 
        # Vertical distance from center to quadrant's bottom [miles]
        h = (lat - c_lat) * DEGREE_LAT
        # horisontal distance to the left border (i.e. at the same latitude) [miles]
        dist = math.sqrt (radius ** 2 - h ** 2)

        # convert to degrees: this depends on the current latitude
        d_long = dist * 360.0 / (EARTH_CIRC*math.cos (current_lat * rad))    #[degrees]
        '''

        # ------------- on the sphere ------------- 
        c1 = math.cos ((radius / EARTH_RAD))
        c2 = math.cos ((90 - lat)*rad) * math.cos ((90 - c_lat)*rad)
        s1 = math.sin ((90 - lat)*rad) * math.sin ((90 - c_lat)*rad)

        c3 =  (c1 - c2) / s1
        d_long =  math.acos (c3) / rad

        return d_long


    # ========================================================================
    # ================== input (latitude, longitude, radius ==================
    # ========================================================================

    #in_str = input ('lat, long, radius: ')
    #in_params = in_str.split()
    in_params=[25.5, -80.1, 20.0]

    #TODO: check input validity
    c_lat = float (in_params[0])       # degrees
    c_long = float (in_params[1])      # degrees
    radius = float (in_params[2])      # radius [miles]


    # ========================================================================
    # ======================== initialize a coordinate grid ========================
    # ========================================================================

    # radius measured in latitude, longitude
    dlat  = radius * 360.0 / EARTH_CIRC
    dlong = radius * 360.0 / (EARTH_CIRC*math.cos(c_lat * rad))

    # boundaries of our chosen grid (this is maximum coverage, rectangular)
    q_left   = quadrant (c_long - dlong)
    q_right  = quadrant (c_long + dlong)
    q_top    = quadrant (c_lat + dlat)
    q_bottom = quadrant (c_lat - dlat)

    # center quadrant; calculations depend on what quarter a quadrant lies in  
    q_center_x = quadrant (c_long)
    q_center_y = quadrant (c_lat)

    # grid dimensions; I need it to allocate the necessary resources; minimum grid is 1x1
    grid_x = q_right - q_left +1
    grid_y = q_top - q_bottom +1

    grid = [[0 for i in range(grid_x)] for j in range(grid_y)]


    print ('center lat/long: ', c_lat, ' ', c_long)
    print ('radius:', radius)
    print ('radius length in degrees:  longitude:', dlong, ', latitude:', dlat)
    print ('grid borders: left:', str(q_left), ', right:', str(q_right), ', top:', str(q_top), ', bottom:' + str(q_bottom))
    #print ('grid:   left: ', q_left, 'right: ', q_right) why does this work???
    print ('grid dimensions:   x: ', grid_x, 'y: ', grid_y)
    print ('cell size:', grid_size)    

#========================================================================
#========================== test each quadrant ==========================
#========================================================================
# Note, up until now we calculated all necessary values just once.
# Now we have to loop through the entire grid, i.e. grid_x * grid_y times.


    #must be correct for any grid dimensions (including 1x1)
    q_current_y = q_top                                 # initial horizontal position
    topHalve = True
    for j in range(grid_y):                             # i.e for each row
        current_lat = q_current_y / GRID
        #print('j:', j, 'current lat:', current_lat)
        
        # Calculate the intersection of current latitude with the circumference.
        d_long = longitudeDistance (current_lat, c_lat, c_long, radius)

        # calculate the left quadrant and convert it to xy-grid
        ql = quadrant (c_long - d_long)
        ql_x = ql - q_left

        #same for right
        qr = quadrant (c_long + d_long)
        qr_x = q_right - qr

        #TODO: optimize: quadrant found is "1" by definition !!!

        # check if quadrant is completely covered by a circle, depending on a circle's quarter:
        # top-left corner (II), top-right (I), bottom-left (III), bottom-right(IV)
        lat_indent = grid_size
        if (not topHalve): lat_indent = -grid_size
        q_current_x = ql
        for i in range(ql_x, grid_x - qr_x):
            current_long = q_current_x / GRID
            if (q_current_x >= q_center_x):             # in I and IV we test top/bottom right corner
                current_long += grid_size
            
            ro = distance (current_lat + lat_indent, current_long, c_lat, c_long)
            #print ('\tcurrent_long:', current_long, ',\tlat_indent: ', lat_indent, ',\tro=', ro)
            if (ro <= radius):
                grid[j][i] = 2
            else:
                grid[j][i] = '-'            # border case: all points need to be tested
            #TODO: optimize: no need to check the internal quadrants
            q_current_x += 1

        # next latitude line
        q_current_y -= 1
        if (topHalve and (q_current_y < q_center_y)):    # i.e. we crossed the diameter
            q_current_y += 1
            topHalve = False


    for k in range (grid_y):
        for l in range (grid_x):
            print (grid[k][l], end=" ")
        print ("")

