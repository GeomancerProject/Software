#!/usr/bin/env python

def tokenize(input, uniques=set()):
    n = len(input)
    if n == 0:
        return
    if n == 1:
        uniques.add(input[0])
        return uniques
    uniques.add(reduce(lambda x,y: '%s %s' % (x, y), input))
    for i in range(n):
        tmp = list(input)
        tmp.pop(i)
        tokenize(tmp, uniques)
    return uniques

if __name__ == '__main__':
    #uniques = set()
    uniques = tokenize([x.strip() for x in 'puma _	concolor '.split('_')])
    print str(uniques) # set(['concolor', 'puma', 'puma concolor'])
