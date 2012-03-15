from __future__ import division
import numpy as np
import zipfile, urllib2, StringIO, cPickle, os, time
from contextlib import closing
from collections import defaultdict
from matplotlib import pyplot as pp
from matplotlib import cm
import matplotlib

dataurl = 'http://www.census.gov/geo/cob/bdy/st/st00ascii/st99_d00_ascii.zip'
cachefilename = '/tmp/state_boundary_cache'

boundarydict = None
states = None
continental_states = None
other_states = set(['Alaska','Puerto Rico','Hawaii'])

### LOADING FUNCTIONS

def get_boundaries():
    global boundarydict
    starttime = time.time()
    if os.path.isfile(cachefilename):
        print 'loading state boundary data from cache %s...' % cachefilename
        with open(cachefilename,'r') as infile:
            boundarydict = cPickle.load(infile)
    else:
        print 'no cache file found...'

        ### download raw data, unpack into strings
        print '   downloading state boundary data...'
        with closing(urllib2.urlopen(dataurl)) as remotefile:
            with closing(zipfile.ZipFile(StringIO.StringIO(remotefile.read()))) as zipped:
                namedata = zipped.read('st99_d00a.dat')
                boundarydata = zipped.read('st99_d00.dat')

        ### parse into my format
        print '   processing boundary data...'

        # build map from number to state name from namedata
        number_to_name = {}
        for block in namedata.split('" "\n \n '):
            blocksplit = block.strip().split('\n')
            number_to_name[int(blocksplit[0].strip())] = blocksplit[2].strip(' "')
        del blocksplit[0]

        # build go through all the paths, put them in boundarydict
        boundarydict = defaultdict(list)
        for block in boundarydata.split('END\n'):
            if block == '':
                continue
            num, restofblock = int(block[:10]), block[10:]
            if num == -99999:
                # Islands or exclusions within a polygon are flagged
                # with an ID number of -99999.
                # I just ignore them.
                continue
            polygon = np.loadtxt(StringIO.StringIO(restofblock),skiprows=1) # first row some internal point
            boundarydict[number_to_name[num]].append(polygon)
        boundarydict = dict(boundarydict)

        ### save into a cache
        print '   saving cache in %s...' % cachefilename
        with open(cachefilename,'w') as outfile:
            cPickle.dump(boundarydict,outfile,protocol=2)

    print '...done in %0.2f sec!' % (time.time() - starttime)

### PLOTTING FUNCTIONS

def show_all():
    raise NotImplementedError

def show_continental():
    pp.figure()
    for state, polys in boundarydict.items():
        if state in continental_states:
            for poly in polys:
                pp.fill(poly[:,0],poly[:,1])

def plot_state(state,color=0.0):
    for poly in boundarydict[state]:
        pp.fill(poly[:,0],poly[:,1],facecolor=pp.get_cmap()(color))
    pp.xticks([])
    pp.yticks([])

def plot_dict(datadict):
    minval, maxval = min(datadict.values()), max(datadict.values())

    for state, value in datadict.items():
        plot_state(state,color=(value-minval)/(maxval-minval))

    pc = matplotlib.collections.PatchCollection(pp.gca().patches,cmap=pp.get_cmap())
    pc.set_array(datadict.values())
    pp.colorbar(pc)


### SCRIPT STUFF
# load data when module is loaded
get_boundaries()
states = set(boundarydict.keys())
continental_states = states - other_states
