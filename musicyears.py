#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Doc """

import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from datetime import datetime

MUSICFOLDER = os.path.join(os.path.expanduser("~"), 'Music')

def parse_song (filename):
    """ Returns the year of that song if there is one. If not, return None. """
    if not os.path.isfile(filename):
        return None

    # os.path.splitext(filename) returns ('Come Together', '.mp3'), for example
    extension = os.path.splitext(filename)[1]
    extension = extension.upper()[1:]
    if extension == "FLAC":
        try:
            metadata = FLAC(filename)
        except:
            print 'No tag found.'
        try:
            year = int(str(metadata["date"][0]))
            return year
        except KeyError:
            print '"%s" does not have date information.' % filename
            return None
        except ValueError:
            print  '%s is not a valid date.' % metadata["date"][0]
            return None
    elif extension == "MP3":
        try:
            metadata = ID3(filename)
        except:
            print 'No tag found.'
        try:
            year = int(str(metadata["TDRC"].text[0]))
            return year
        except KeyError:
            print '"%s" does not have date information.' % filename
            return None
        except ValueError:
            print  '%s is not a valid date.' % metadata["date"][0]
            return None
    else:
        print 'Extension %s not supported.' % extension
        return None

def crawl_directory ( directory = MUSICFOLDER ):
    for subpath in os.listdir(directory):
        subpath = os.path.join(directory, subpath)
        #print 'Grabbing info from %s' % subpath
        year = parse_song(subpath)
        if year is not None:
            print 'Year is %d' % year
            YEARS[year] = YEARS.get(year, 0) + 1
        elif os.path.isdir(subpath):
            crawl_directory(subpath)
        else:
            print 'File %s is not a valid type or has no date metadata.' % subpath

def pad_years():
    for year in xrange(min(YEARS.keys()), max(YEARS.keys())):
        YEARS[year] = YEARS.get(year, 0)

def get_plot():
    years = YEARS.keys()
    freqs = YEARS.values()
    N = len(years)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.8       # the width of the bars: can also be len(x) sequence

    plt.bar(ind, freqs,   width, color='b')

    plt.ylabel('Quantity of songs')
    #plt.ylabel('Percentage of songs')
    plt.title('Song distribution by year')
    # Uma lustra é um período de 5 anos.
    lustra = years
    for k in range(0, N):
        if (years[k]%5 == 0):
            lustra[k] = years[k]
        else:
            lustra[k] = ''
    tup =  tuple(lustra)
    plt.xticks(ind+width/2., tup)
    plt.yticks(np.arange(0, max(freqs) + 10, 25))
    #plt.yticks(np.arange(0, 6, 1))

    return plt
    plt.savefig('foo.png', bbox_inches=0)
    plt.show()

if __name__=="__main__":
    now = datetime.now()

    if sys.argv[1:]:
        folders = sys.argv[1:]
    else:
        folders = [MUSICFOLDER]

    for folder in folders:
        YEARS = {}
        crawl_directory(folder)
        pad_years()
        csvfilename = 'musicyears_%s.csv' % now.strftime("%Y-%m-%d--%H-%M")
        csvfile = os.path.join(folder, csvfilename)
        print 'Writing data to %s.' % csvfile
        f = open(csvfile, 'wb')
        csvw = csv.writer(f, delimiter=',')
        for (ano, freq) in YEARS.iteritems():
            csvw.writerow([ano, freq])
        f.close()
        plt = get_plot()
        plt.savefig(csvfile.rstrip('csv') + 'png')
