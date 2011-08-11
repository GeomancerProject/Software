#!/usr/bin/env python

import logging
from optparse import OptionParser

class Point(object):
    """A degree-based geographic coordinate independent of a coordinate reference system."""

    def __init__(self, lng, lat):
        self._lng = lng
        self._lat = lat

    def get_lng(self):
        return self._lng
    lng = property(get_lng)

    def get_lat(self):
        return self._lat
    lat = property(get_lat)

    def isvalid(self):
        if math.fabs(self.lat) <= 90:
            if math.fabs(self.lng) <= 180:
                return True
        return False

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        if self.lat != other.lat:
            return NotImplemented
        if self.lng != other.lng:
            return NotImplemented
        return True

    def __gt__(self, other):
        if self._lat > other._lat:
            return True
        if self._lng > other._lng:
            return True
        return False

    def __lt__(self, other):
        if self._lat < other._lat:
            return True
        if self._lng < other._lng:
            return True
        return False

    def __cmp__(self, other):
        if self.__gt__(other):
            return 1
        if self.__lt__(other):
            return -1
        return 0

    def __hash__(self):
        return hash('%s,%s' % (self._lat, self._lng))

class BoundingBox(object):
    """A degree-based geographic bounding box independent of a coordinate reference system."""

    def __init__(self, nw, se):
        self._nw = nw
        self._se = se
    
    def get_nw(self):
        return self._nw
    nw = property(get_nw)
    
    def get_se(self):
        return self._se
    se = property(get_se)
    
    def get_n(self):
        return self._nw.get_lat()
    
    def get_w(self):
        return self._nw.get_lng()
    
    def get_s(self):
        return self._se.get_lat()
    
    def get_e(self):
        return self._se.get_lng()

    def isvalid(self):
        if nw.isvalid:
            if se.isvalid:
                return True
        return False

    @classmethod
    def create(cls, xmin, ymax, xmax, ymin):
        return cls(Point(xmin, ymax), Point(xmax, ymin))
    
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if not isinstance(other, BoundingBox):
            return NotImplemented
        if self.nw != other.nw:
            return NotImplemented
        if self.se != other.se:
            return NotImplemented
        return True

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __hash__(self):
        return hash('%s,%s %s,%s' % (self.get_w(), self.get_n(), self.get_e(), self.get_s()))

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        if self.nw.__gt__(other.nw):
            return 1
        return -1

    @classmethod
    def get_intersecting(cls, bb_list):
        pass # TODO

    @classmethod
    def intersect_all(cls, bb_list):
        n = len(bb_list)
        if n == 1:
            return bb_list[0]
        if n == 0:
            return None
        result = bb_list.pop(0)
        for bb in bb_list:
            result = bb.intersection(result)
            if result is None:
                return None
        return result
    
    def intersection(self,bb):
        """Returns a BoundingBox created from an intersection or None."""
        my_n=self.nw.get_lat()
        my_s=self.se.get_lat()
        my_w=self.nw.get_lng()
        my_e=self.se.get_lng()
        bb_n=bb.nw.get_lat()
        bb_s=bb.se.get_lat()
        bb_w=bb.nw.get_lng()
        bb_e=bb.se.get_lng()
        n,s,w,e = None, None, None, None
        if my_s <= bb_n and bb_n <= my_n:
            n=bb_n
        elif bb_s <= my_n and my_n <= bb_n:
            n=my_n
        if n is None:
            return None

        if my_s <= bb_s and bb_s <= my_n:
            s=bb_s
        elif bb_s <= my_s and my_s <= bb_n:
            s=my_s
        if s is None:
            return None

        if is_lng_between(bb_w, my_w,my_e):
            w=bb_w
        elif is_lng_between(my_w, bb_w,bb_e):
            w=my_w
        if w is None:
            return None

        if is_lng_between(bb_e, my_w,my_e):
            e=bb_e
        elif is_lng_between(my_e, bb_w,bb_e):
            e=my_e
        if e is None:
            return None
        return BoundingBox(Point(w,n),Point(e,s))
            
def is_lng_between(lng, west_lng, east_lng):
    '''
    Returns true if the given lng is between the longitudes west_lng and east_lng
    proceeding east from west_lng to east_lng.
    '''
    west_to_east = lng_distance(west_lng, east_lng)
    lng_to_east = lng_distance(lng, east_lng)
    if west_to_east >= lng_to_east:
        return True
    return False

def lng_distance(west_lng, east_lng):
    '''Returns the number of degrees from west_lng going eastward to east_lng.'''
    w = lng180(west_lng)
    e = lng180(east_lng)
    if w==e:
        '''
        Convention: If west and east are the same, the whole circumference is meant 
        rather than no difference.
        '''
        return 360
    if e <= 0:
        if w <= 0:
            if w > e:
                '''w and e both in western hemisphere with w east of e.'''
                return 360 + e - w
            '''w and e in western hemisphere with w west of e.'''
            return e - w
        '''w in eastern hemisphere and e in western hemisphere.'''
        return 360 + e - w
    if w <= 0:
        '''w in western hemisphere and e in eastern hemisphere.'''
        return e - w
    if w > e:
        '''w and e both in eastern hemisphere with w east of e.''' 
        return 360 + e - w
    '''w and e both in eastern hemisphere with w west or e.'''
    return e - w

def lng180(lng):
    '''Given a longitude in degrees, returns a longitude in degrees between {-180, 180].'''
    if lng <= -180:
        return lng + 360
    elif lng > 180:
        return lng - 360
    return lng

def _getoptions():
    """Parses command line options and returns them."""
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command",
                      help="Command to run",
                      default=None)
    parser.add_option("-1", "--bb1", dest="bb1",
                      help="NW corner of one bounding box",
                      default=None)
    parser.add_option("-2", "--bb2", dest="bb2",
                      help="NW corner of second bounding box",
                      default=None)
    return parser.parse_args()[0]

def main():
    logging.basicConfig(level=logging.DEBUG)
    options = _getoptions()
    command = options.command.lower()
    
    logging.info('COMMAND %s' % command)

    if command=='help':
        print 'syntax: -c intersection -1 w_lng,n_lat|e_lng,s_lat -2 w_lng,n_lat|e_lng,s_lat'
        
    if command=='intersect':
        if options.bb1 is None:
            print 'bb1 argument missing'
            return
        if options.bb2 is None:
            print 'bb2 argument missing'
            return
        nw, se = options.bb1.split('|')
        w, n = nw.split(',')
        e, s = se.split(',')
        pnw=Point(float(w),float(n))
        pse=Point(float(e),float(s))
        bb1=BoundingBox(pnw,pse)

        nw, se = options.bb2.split('|')
        w, n = nw.split(',')
        e, s = se.split(',')
        pnw=Point(float(w),float(n))
        pse=Point(float(e),float(s))
        bb2=BoundingBox(pnw,pse)
        
        i = bb1.intersection(bb2)
        if i is None:
            print 'No intersection'
        else:
            print 'nw: %s se: %s' % (i.nw, i.se)

if __name__ == "__main__":
    main()
