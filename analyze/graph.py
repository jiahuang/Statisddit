'''
Graphing Statistics
'''

import datetime
import time
import sys
import Pmf, Cdf
import numpy as np
import pylab
#import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from pylab import plot
import math

def barGraphTwo(xs1, fs1, xs2, fs2, f, xlabel, ylabel, legend):
	pylab.cla()
	bar1= pylab.bar(xs1, fs1, width=1, facecolor='red')
	bar2=pylab.bar(xs2, fs2, width=1, facecolor='cyan')
	# got from http://stackoverflow.com/questions/2194299/in-matplotlib-how-to-draw-a-bar-graphs-of-multiple-datasets-to-put-smallest-bars
	all_patches = pylab.axes().patches
	patch_at_x = {}
	for patch in all_patches:
		if patch.get_x() not in patch_at_x: patch_at_x[patch.get_x()] = []
		patch_at_x[patch.get_x()].append(patch)

	# custom sort function, in reverse order of height
	def yHeightSort(i,j):
		if j.get_height() > i.get_height(): return 1
		else: return -1

	# loop through sort assign z-order based on sort
	for x_pos, patches in patch_at_x.iteritems():
		if len(patches) == 1: continue
		patches.sort(cmp=yHeightSort)
		[patch.set_zorder(patches.index(patch)) for patch in patches]


	fontP = FontProperties()
	fontP.set_size('small')
	#pylab.xlim([0,24])
	pylab.ylabel(ylabel)
	pylab.xlabel(xlabel)
	pylab.legend((bar2[0], bar1[0]), legend, prop = fontP)
	pylab.savefig(f)

def barGraph(xs1, fs1, f, xlabel, ylabel):
	pylab.cla()
	pylab.bar(xs1, fs1, width=0.8, facecolor='blue')
	pylab.xlim([0,24])
	pylab.ylabel(ylabel)
	pylab.xlabel(xlabel)
	pylab.savefig(f)
