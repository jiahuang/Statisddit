'''
Analyzing Statistics
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

class Analyze:
	def openFile(self, f):
		f = open(f,'r')
		return eval(f.read())
	
	def lengthOfStay(self, f='lengthOfStay.res'):
		# generate continous? CDF
		data = self.openFile(f)
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		pylab.xlim([0,1400])
		pylab.savefig('lengthOfStay.png')
	
	def timeToReachFront(self, f='timeToReachFront.res'):
		# generate cdf of time it takes to reach front vs posting
		data = self.openFile(f)
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		pylab.xlim([0,800])
		pylab.savefig('timeToReachFront.png')
	
	def postTime(self, f1='postTime_25.res', f2='postTime_200.res'):
		pylab.cla()
		
		def hoursToDivide():
			# returns dict with key being the hour and val being the number of times the hour has been scraped
			timeDict = {}
			# subtracted start and end dates by 5 hours due to gm time
			start = datetime.datetime(2011, 9, 2, 20, 30) 
			end = datetime.datetime(2011, 9, 15, 9, 50)
			change = datetime.timedelta(minutes=10)
			while start <= end:
				timeDict[start.hour] = 1.0/6.0 if start.hour not in timeDict else timeDict[start.hour] + 1.0/6.0
				start += change
			return timeDict
		
		# generate pmf of time posted vs number of posts reaching front page/not front page
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		# get total amount
		for key in data1:
			data2[key] += data1[key]
			
		cleanData1 = {}
		cleanData2 = {}
		timeDict = hoursToDivide()
		# average out data
		for key in data1:
			data1[key] = float(data1[key])/timeDict[key]
		
		for key in data2:
			data2[key] = float(data2[key])/timeDict[key]
			
		hist2 = Pmf.MakeHistFromDict(data2)
		hist1 = Pmf.MakeHistFromDict(data1)
		xs1, fs1 = hist1.Render()
		xs2, fs2 = hist2.Render()
		bar1= pylab.bar(xs1, fs1, width=0.8, facecolor='red')
		bar2=pylab.bar(xs2, fs2, width=0.8, facecolor='cyan')
		pmf1 = Pmf.MakePmfFromHist(hist1)
		print "Variance:",pmf1.Var()
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
		pylab.xlim([0,24])
		pylab.ylabel('Average Number of Posts')
		pylab.xlabel('Hour of Day Posted')
		pylab.legend((bar2[0], bar1[0]), ('Top 200 Posts', 'Front Page Posts'), prop = fontP)
		pylab.savefig('postTime.png')
		
		pylab.cla()
		dividedData = {}
		for key in data1:
			dividedData[key] = float(data1[key])/float(data2[key])
		pmf = Pmf.MakePmfFromDict(dividedData)
		pmf.Normalize()
		xs3, fs3 = pmf.Render()
		bar3= pylab.bar(xs3, fs3, width=0.8, facecolor='blue')
		pylab.xlim([0,24])
		pylab.ylabel('Probability of Reaching Front Page')
		pylab.xlabel('Hour of Day Posted')
		pylab.savefig('postTimeDivided.png')
	
	def peakRank(self, f='peakRank_25.res'):
		# generate cdf of number of posts reached max vs posting time
		data = self.openFile(f)
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		pylab.xlim([0,1200])
		pylab.savefig('peakRank_25.png')
	
	# of the 5923 posts we grabbed, only 15 were reposts
	def repost(self, fFirst='firstPosts.res', fOther='repeatPosts.res'):
		firstData = self.openFile(fFirst)
		otherData = self.openFile(fOther)
		pylab.cla()
		# plot paths that posts went through

def main(name):
	analyze = Analyze()
	#analyze.lengthOfStay()
	#analyze.timeToReachFront()
	#analyze.postTime()
	analyze.peakRank()
	
if __name__ == '__main__':
	main(*sys.argv)
