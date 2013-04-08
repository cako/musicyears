#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Musicyears creates a plot of song years. """

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
            year = int(metadata["date"][0])
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
            year = metadata["TDRC"].text[0].year
            return year
        except KeyError:
            print '"%s" does not have date information.' % filename
            return None
        except ValueError:
            print  '%s is not a valid date.' % metadata["TDRC"].text[0]
            return None
    else:
        print 'Extension %s not supported.' % extension
        return None

def crawl_directory (directory=MUSICFOLDER):
    global years
    for subpath in os.listdir(directory):
        subpath = os.path.join(directory, subpath)
        #print 'Grabbing info from %s' % subpath
        year = parse_song(subpath)
        if year is not None:
            print 'Year is %d' % year
            years[year] = years.get(year, 0) + 1
        elif os.path.isdir(subpath):
            crawl_directory(subpath)
        else:
            print 'File %s is not a valid type or has no date metadata.' % subpath
    return years

def pad_years(years):
    for year in xrange(min(years.keys()), max(years.keys())):
        years[year] = years.get(year, 0)
    return years

def get_plot(years):
    new_years = years.keys()
    freqs = years.values()
    N = len(new_years)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.8       # the width of the bars: can also be len(x) sequence

    plt.bar(ind, freqs,   width, color='b')

    plt.ylabel('Quantity of songs')
    #plt.ylabel('Percentage of songs')
    plt.title('Song distribution by year')
    # Uma lustra é um período de 5 anos.
    lustra = new_years
    for k in range(0, N):
        if (new_years[k]%5 == 0):
            lustra[k] = new_years[k]
        else:
            lustra[k] = ''
    tup =  tuple(lustra)
    plt.xticks(ind+width/2., tup)
    plt.yticks(np.arange(0, max(freqs) + 10, 25))
    #plt.yticks(np.arange(0, 6, 1))

    return plt

if __name__=="__main__":
    now = datetime.now()

    if sys.argv[1:]:
        folders = sys.argv[1:]
    else:
        folders = [MUSICFOLDER]

    for folder in folders:
        years = {}
        years = crawl_directory(folder)
        years = pad_years(years)
        csvfilename = 'musicyears_%s.csv' % now.strftime("%Y-%m-%d--%H-%M")
        csvfile = os.path.join(folder, csvfilename)
        print 'Writing data to %s.' % csvfile
        f = open(csvfile, 'wb')
        csvw = csv.writer(f, delimiter=',')
        for (ano, freq) in years.iteritems():
            csvw.writerow([ano, freq])
        f.close()
        plt = get_plot(years)
        #plt.show()
        F = plt.gcf()
        F.set_size_inches([16., 9.])
        F.savefig(csvfile.rstrip('csv') + 'png', bbox_inches='tight', dpi=(120))
