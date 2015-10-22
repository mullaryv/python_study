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
        #print ('c1: ', c1, 'c2: ', c2, 's1 ', s1, 'c3 ', c3)
        d_long =  math.acos (c3) / rad

        return d_long


    # ========================================================================
    # ================== input (latitude, longitude, radius ==================
    # ========================================================================

    #in_str = input ('lat, long, radius: ')
    #in_params = in_str.split()
    #in_params=[25.5, -80.1, 10.0]
    in_params=[38.48677062, -121.49452, 50.0]

    points_num = 40                       #number of dots on the circumference
    points_num = int(math.floor(points_num/2)*2) # must be even number
    points_half = int(math.floor(points_num/2))  # adjusted   
    
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

    current_lat = c_lat + dlat            # we'll start at North
    angle = (360 / points_num)*rad

    print ('radius length in degrees:  longitude:', dlong, ', latitude:', dlat)
    print ('center lat/long: ', c_lat, ' ', c_long)
    print ('radius:          ', radius)
    print ('start latitude:  ', current_lat)
    print ('angle:           ', angle)

#========================================================================
# Now go down the latitude, by moving radius counter-clockwise
#========================================================================
# Note, up until now we calculated all necessary values just once.


    points = [[0 for i in range(points_num)] for j in range(2)]
    
    #TODO: must be correct for any point numbers
    for j in range (points_half+1):                             # i.e for each row

        # Calculate the intersection of current latitude with the circumference.
        d_long = longitudeDistance (current_lat, c_lat, c_long, radius)
        #print('j:', j, 'current lat:', current_lat, 'd_long: ', d_long)

        points[0][j] = d_long
        points[1][j] = current_lat

        # I'm quite confident to use Pythagoras here
        current_lat = c_lat + radius*math.cos((j+1)*angle)/DEGREE_LAT
        
    for k in range (points_half+1):
        print (k, ': long: ', c_long - points[0][k], 'lat  ', points[1][k])
    for k in range (points_half-1, -1, -1):
        print (k, ': long: ', c_long + points[0][k], 'lat  ', points[1][k])
   
    print ('POLYGON ((', end = "")
    for k in range (points_half+1):
        print (c_long - points[0][k], points[1][k], end="")
        print (',', end=" ")
    for k in range (points_half-1, -1, -1):
        print (c_long + points[0][k], points[1][k], end="")
        if k != 0:
            print (',', end=" ")
    print ('))')
            



#POLYGON ((-121.480038801021081 38.48677062,-121.480217088610686 38.484505261384591,-121.480747561347329 38.482295683416595,-121.48161715723171 38.480196293238734,-121.482804463927124 38.47825878480468,-121.484280246002285 38.4765308660023,-121.486008164804673 38.475055083927131,-121.487945673238727 38.473867777231717,-121.490045063416588 38.472998181347336,-121.492254641384591 38.472467708610687,-121.49452 38.472289421021088,-121.496785358615398 38.472467708610687,-121.498994936583401 38.472998181347336,-121.501094326761262 38.473867777231717,-121.503031835195316 38.475055083927131,-121.504759753997703 38.4765308660023,-121.506235536072865 38.47825878480468,-121.507422842768278 38.480196293238734,-121.50829243865266 38.482295683416595,-121.508822911389302 38.484505261384591,-121.509001198978908 38.48677062,-121.508822911389302 38.489035978615412,-121.50829243865266 38.491245556583408,-121.507422842768278 38.493344946761269,-121.506235536072865 38.495282455195323,-121.504759753997703 38.497010373997703,-121.503031835195316 38.498486156072872,-121.501094326761262 38.499673462768286,-121.498994936583401 38.500543058652667,-121.496785358615398 38.501073531389316,-121.49452 38.501251818978915,-121.492254641384591 38.501073531389316,-121.490045063416588 38.500543058652667,-121.487945673238727 38.499673462768286,-121.486008164804673 38.498486156072872,-121.484280246002285 38.497010373997703,-121.482804463927124 38.495282455195323,-121.48161715723171 38.493344946761269,-121.480747561347329 38.491245556583408,-121.480217088610686 38.489035978615412,-121.480038801021081 38.48677062))