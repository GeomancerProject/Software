from decimal import *

if __name__ == '__main__':
    if type(d) != str:
        return None

    distances = ['a', '1', '-1', '1.0', '-1.0']
    
    for d in distances:
        n = None
        try:
            n = int(d)
        except:
            print d + ' not an int'
        try:
            float(d)
            n = Decimal(d)
        except:
            print d + ' not a float'
        
    if n and n < 0:
        print d + ' is negative'
    elif n:
        print d + ' is positive'

        
