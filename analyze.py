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
import math

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
	
	def peakRank(self, f1='peakRank_25.res', f2='peakRank_200.res'):
		# generate cdf of number of posts reached max vs posting time
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		cdf1 = Cdf.MakeCdfFromDict(data1)
		cdf2 = Cdf.MakeCdfFromDict(data2)
		print "top 25: Mean, Median", cdf1.Mean(), cdf1.Value(.5)
		print "rest: Mean, Median", cdf2.Mean(), cdf2.Value(.5)
		pylab.cla()
		pylab.xlim([0,1200])
		p1 = plot(cdf1.xs,cdf1.ps)
		p2 = plot(cdf2.xs,cdf2.ps)
		pylab.ylabel('CDF')
		fontP = FontProperties()
		fontP.set_size('small')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.xlabel('Time Since Posting (min)')
		pylab.savefig('peakRank.png')
		
		# generate cdf of peak rank
		
	
	# of the 5923 posts we grabbed, only 15 were reposts
	def repost(self, f1='firstPosts.res', f2='repeatPosts.res'):
		f1 = self.openFile(f1)
		f2 = self.openFile(f2)
		#ax = pylab.gca()
		origDict = {}
		for item in f1:
			rank = min(item)
			origDict[rank] = 1 if rank not in origDict else origDict[rank] + 1
			#p1 = plot(range(len(item)),item, 'r')
		
		repostDict = {}
		for item in f2:
			rank = min(item)
			#p1 = plot(range(len(item)),item, 'c')
			repostDict[rank] = 1 if rank not in repostDict else repostDict[rank] + 1
		#ax.invert_yaxis()
		
		# plot some histograms
		'''
		pylab.cla()
		hist1 = Pmf.MakeHistFromDict(origDict)
		xs1, fs1 = hist1.Render()
		bar1= pylab.bar(xs1, fs1, width=0.8, facecolor='cyan')
		pylab.savefig('repost_orig.png')
		
		pylab.cla()
		hist1 = Pmf.MakeHistFromDict(repostDict)
		xs1, fs1 = hist1.Render()
		bar1= pylab.bar(xs1, fs1, width=0.8, facecolor='red')
		pylab.savefig('repost_repost.png')
		'''

	def score(self, f1='score_25.res', f2="score_200.res"):
		# generate histogram of avg score
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		cleanData1 = {}
		cleanData2 = {}
		
		for key in data1:
			cleanData1[key] = float(data1[key][0])/float(data1[key][1])#math.log10()
		for key in data2:
			cleanData2[key] = float(data2[key][0])/float(data2[key][1])#math.log10()
			
		# generate pmfs
		pylab.cla()
		hist1 = Pmf.MakeHistFromDict(cleanData1)
		hist2 = Pmf.MakeHistFromDict(cleanData2)
		xs1, fs1 = hist1.Render()
		xs2, fs2 = hist2.Render()
		pylab.xlim([0,1460])
		pylab.ylabel('Average Change in Score')
		pylab.xlabel('Time Since Posting (min)')
		#bar= pylab.bar(xs1, fs1, width=0.8, facecolor='blue')
		plot(xs1, fs1, 'b.')
		pylab.savefig('score_25.png')
		pylab.cla()
		pylab.xlim([0,1460])
		pylab.ylabel('Average Change in Score')
		pylab.xlabel('Time Since Posting (min)')
		#bar= pylab.bar(xs2, fs2, width=0.8, facecolor='red')
		plot(xs2, fs2, 'b.')
		pylab.savefig('score_200.png')
		
		# generate cdf
		pylab.cla()
		cdf1 = Cdf.MakeCdfFromDict(cleanData1)
		cdf2 = Cdf.MakeCdfFromDict(cleanData2)
		fontP = FontProperties()
		fontP.set_size('small')
		p1 = plot(cdf1.xs,cdf1.ps)
		p2 = plot(cdf2.xs,cdf2.ps)
		pylab.xlim([0,1460])
		pylab.ylabel('CDF')
		pylab.xlabel('Time Since Posting (min)')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.savefig('score.png')
		
		# ccdf
		pylab.cla()
		ccdfData1 = {}
		ccdfData2 = {}
		for xs, ps in cdf1.Items():
			ccdfData1[xs] = 1-ps
		for xs, ps in cdf2.Items():
			ccdfData2[xs] = 1-ps
		fontP = FontProperties()
		fontP.set_size('small')
		p1 = pylab.semilogy(ccdfData1.keys(), ccdfData1.values())
		p2 = pylab.semilogy(ccdfData2.keys(), ccdfData2.values())
		pylab.xlim([0,1460])
		pylab.ylabel('Complimentary CDF')
		pylab.xlabel('Time Since Posting (min)')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.savefig('scoreCCDF.png')
		
	
	def subreddit(self, f1='subreddit_25.res', f2='subreddit_200.res'):
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		for key in data1:
			data2[key] = data2[key] + data1[key]
		hist2 = Pmf.MakeHistFromDict(data2)
		hist1 = Pmf.MakeHistFromDict(data1)
		xs1, fs1 = hist1.Render()
		xs2, fs2 = hist2.Render()
		
		# create histograms
		fakeX = range(len(xs1))
		
		bar1= pylab.bar(fakeX, fs1, width=0.8, facecolor='red')
		bar2=pylab.bar(fakeX, fs2, width=0.8, facecolor='cyan')
		
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
			
		ax = pylab.gca()
		ax.set_xticks(fakeX)
		ax.set_xticklabels(xs1, rotation=20)
 
		fontP = FontProperties()
		fontP.set_size('small')
		#pylab.xlim([0,24])
		pylab.ylabel('Number of Posts')
		pylab.xlabel('Subreddit')
		pylab.legend((bar2[0], bar1[0]), ('Top 200 Posts', 'Front Page Posts'), prop = fontP)
		pylab.savefig('subreddit.png')
		
		pylab.cla()
		dividedData = {}
		for key in data1:
			dividedData[key] = float(data1[key])/float(data2[key])
		pmf = Pmf.MakePmfFromDict(dividedData)
		pmf.Normalize()
		xs3, fs3 = pmf.Render()
		
		bar3= pylab.bar(fakeX, fs3, width=0.8, facecolor='blue')
		ax = pylab.gca()
		ax.set_xticks(fakeX)
		ax.set_xticklabels(xs1, rotation=20)
		
		pylab.ylabel('Probability')
		pylab.savefig('subredditDivided.png')
		
def main(name):
	analyze = Analyze()
	#analyze.lengthOfStay()
	#analyze.timeToReachFront()
	#analyze.postTime()
	#analyze.peakRank()
	#analyze.score()
	#analyze.subreddit()
	analyze.repost()
	
if __name__ == '__main__':
	main(*sys.argv)
