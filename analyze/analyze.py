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
from graph import *

def pearsonCorrelation(x, y):
	pmfX = Pmf.MakePmfFromList(x)
	pmfY = Pmf.MakePmfFromList(y)
	p = []
	meanX = pmfX.Mean()
	stdX = pmfX.Var()**(1.0/2.0)
	meanY = pmfY.Mean()
	stdY = pmfY.Var()**(1.0/2.0)
	
	for i in range(len(x)):
		p.append(((x[i] - meanX)/stdX)*((y[i] - meanY)/stdY))
	
	pTotal = 0.0
	for item in p:
		pTotal+=item
	pearsonCorrelation = pTotal/len(p)
	return pearsonCorrelation

def getRanks(x):
	# map each x to a rank
	xDict = {}
	xSorted = sorted(x)
	
	for i, val in enumerate(xSorted):
		if val in xDict:
			valList = xDict[val]
			valList.append(i)
		else:
			xDict[val] = [i]
	
	# normalize by rank
	xRanked = []
	for key in xDict:
		valList = xDict[key]
		valMean = 0.0
		for item in valList:
			valMean += item
		xDict[key] = valMean/len(valList)
		
	for val in x:
		xRanked.append(xDict[val])
	return xRanked
	
def spearmanCorrealtion(x, y):
	xRanked = getRanks(x)
	yRanked = getRanks(y)
	return pearsonCorrelation(xRanked, yRanked)
	
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
	
	def postTimeAutoCorrelation(self, f1='postTime_days_25.res', f2='postTime_days_200.res'):
		# add up hours
		data1 = self.openFile(f1)
		cleanedData1 = {}
		minDay = 250
		for dayKey in data1:
			for hourKey in data1[dayKey]:
				hour = (dayKey-minDay)*24+hourKey
				cleanedData1[hour] = data1[dayKey][hourKey]#1 if hour not in cleanedData1 else cleanedData1[hour] + 1
				
		data2 = self.openFile(f2)
		cleanedData2 = {}
		for dayKey in data2:
			for hourKey in data2[dayKey]:
				hour = (dayKey-minDay)*24+hourKey
				cleanedData2[hour] = data2[dayKey][hourKey]#1 if hour not in cleanedData2 else cleanedData2[hour] + 1
		hist2 = Pmf.MakeHistFromDict(cleanedData2)
		hist1 = Pmf.MakeHistFromDict(cleanedData1)
		xs1, fs1 = hist1.Render()
		xs2, fs2 = hist2.Render()
		barGraphTwo(xs1, fs1, xs2, fs2, 'postTime_overall.png', 'Hours', 'Number of Posts', ('Top 200 Posts', 'Front Page Posts'))
		
		#auto correlation of posts that make it to the front page
		# results: 0.727454316786 for posts that dont make it to top 200
		# 0.42732166891 for posts that make it to the top 200
		disregard = 1 # disregard first day
		offset = 1 # 1 day
		days = 10
		# testing across 10 days
		regData = {}
		offsetData = {}
		
		for key in cleanedData1:
			if key >= disregard*24 and key <=(days+disregard)*24:
				#print disregard*24
				regData[key] = cleanedData1[key]
			if key >= (disregard+offset)*24 and key<=(days+disregard+offset)*24:
				offsetData[key] = cleanedData1[key]
		#print regData
		print offsetData
		# get the mean
		mean = 0
		meanOffset = 0
		for key in regData:
			mean += regData[key]
		mean = mean/len(regData)
		for key in offsetData:
			meanOffset += offsetData[key]
		meanOffset = mean/len(offsetData)
		totalSamples = len(regData) + len(offsetData)
		diffInMean = 0.0
		var = 0.0
		for key in regData:
			if key+offset*24 in offsetData:
				diffInMean += (regData[key]-mean)*(offsetData[key+offset*24]-meanOffset)
				var += (regData[key] - mean)**2
		diffInMean = diffInMean/totalSamples
		var = var/totalSamples
		print diffInMean/var
		
				
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
			if key in data2:
				data2[key] += data1[key]
			else:
				data2[key] = data1[key]
			
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
		barGraphTwo(xs1, fs1, xs2, fs2, 'postTime.png', 'Hour of Day Posted', 'Average Number of Posts', ('Top 200 Posts', 'Front Page Posts'))
		
		dividedData = {}
		for key in data1:
			dividedData[key] = float(data1[key])/float(data2[key])
		pmf = Pmf.MakePmfFromDict(dividedData)
		pmf.Normalize()
		xs3, fs3 = pmf.Render()
		barGraph(xs3, fs3, 'postTimeDivided.png', 'Hour of Day Posted', 'Probability of Reaching Front Page')
		
	def peakRank(self, f1='peakRank_25.res', f2='peakRank_200.res'):
		# generate cdf of number of posts reached max vs posting time
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		cdf1 = Cdf.MakeCdfFromDict(data1)
		cdf2 = Cdf.MakeCdfFromDict(data2)
		pdf1 = Pmf.MakePmfFromDict(data1)
		pdf2 = Pmf.MakePmfFromDict(data2)
		
		print "top 25: Mean, Median, n", cdf1.Mean(), cdf1.Value(.5), len(data1)
		print "rest: Mean, Median, m", cdf2.Mean(), cdf2.Value(.5), len(data2)
		diffInMean = abs(cdf1.Mean() - cdf2.Mean())
		
		pylab.cla()
		pylab.xlim([0,1200])
		p1 = plot(cdf1.xs,cdf1.ps)
		p2 = plot(cdf2.xs,cdf2.ps)
		# generate cdf of peak rank
		pylab.ylabel('CDF')
		fontP = FontProperties()
		fontP.set_size('small')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.xlabel('Time Since Posting (min)')
		pylab.savefig('peakScore.png')
		
		#myplot.Cdf(cdf1, complement=True, xscale='linear', yscale='log') 
		#pdf
		pylab.cla()
		pylab.xlim([0,1200])
		x = []
		y = []
		for xs, ps in sorted(pdf1.Items()):
			x.append(xs)
			y.append(ps)
		p1 = plot(x,y)
		x = []
		y = []
		for xs, ps in sorted(pdf2.Items()):
			x.append(xs)
			y.append(ps)
		p2 = plot(x,y)
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.ylabel('PMF')
		pylab.xlabel('Time Since Posting (min)')
		pylab.savefig('peakScore_pdf.png')
		#ccdf
		pylab.cla()
		ccdfData1 = {}
		ccdfData2 = {}
		for xs, ps in cdf1.Items():
			if 1.0-ps > 0.0:
				ccdfData1[xs] = math.log10(1.0-ps)
		for xs, ps in cdf2.Items():
			if 1.0-ps > 0.0:
				ccdfData2[xs] = math.log10(1.0-ps)
		fontP = FontProperties()
		fontP.set_size('small')
		
		# linear regression
		#x1 = ([0, 400], ccdfData1.keys())
		fit = pylab.polyfit(ccdfData1.keys(), ccdfData1.values(), 1)
		fit_fn = pylab.poly1d(fit)
		plot(ccdfData1.keys(),fit_fn(ccdfData1.keys()),'k--')
		print fit
		
		fit = pylab.polyfit(ccdfData2.keys(), ccdfData2.values(), 1)
		fit_fn = pylab.poly1d(fit)
		print fit
		p0 = plot(ccdfData2.keys(),fit_fn(ccdfData2.keys()),'k--')
		
		p1 = plot(ccdfData1.keys(), ccdfData1.values())
		p2 = plot(ccdfData2.keys(), ccdfData2.values())
		pylab.xlim([0,1460])
		#pylab.ylim([0,146])
		pylab.ylabel('Complimentary CDF (10^y)')
		pylab.xlabel('Time Since Posting (min)')
		pylab.legend((p1[0], p2[0], p0[0]), ('Top 25', 'Top 26-200', 'Regression'), prop = fontP)
		pylab.savefig('peakScore_ccdf.png')
	
	# of the 5923 posts we grabbed, only 15 were reposts
	def repost(self, f1='firstPosts.res', f2='repeatPosts.res'):
		f1 = self.openFile(f1)
		f2 = self.openFile(f2)
		#ax = pylab.gca()
		origDict = {}
		for item in f1:
			rank = min(item)
			origDict[rank] = 1 if rank not in origDict else origDict[rank] + 1
			#p1 = plot(range(len(item)),item, 'r') # Oh god this is crazy don't ever do this
		
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

	def score(self, f1='score_25.res', f2="score_200.res",fout="score"):
		# generate histogram of avg score
		data1 = self.openFile(f1)
		data2 = self.openFile(f2)
		cleanData1 = {}
		cleanData2 = {}
		
		# bucket posts every 10 min
		for key in data1:
			#if float(data1[key][0])/float(data1[key][1]) > 0:
			cleanData1[key/10] = float(data1[key][0])/float(data1[key][1]) if key/10 not in cleanData1 else cleanData1[key/10] + float(data1[key][0])/float(data1[key][1])
		for key in data2:
			#if float(data2[key][0])/float(data2[key][1]) > 0:
			cleanData2[key/10] = float(data2[key][0])/float(data2[key][1]) if key/10 not in cleanData2 else cleanData2[key/10] + float(data2[key][0])/float(data2[key][1])
		
		fontP = FontProperties()
		fontP.set_size('small')
		
		# generate pmfs
		pylab.cla()
		hist1 = Pmf.MakeHistFromDict(cleanData1)
		hist2 = Pmf.MakeHistFromDict(cleanData2)
		xs1, fs1 = hist1.Render()
		xs2, fs2 = hist2.Render()
		pylab.xlim([0,146])#1460
		pylab.ylabel('Average Change in '+fout)
		pylab.xlabel('Time Since Posting (every 10 min)')
		#bar= pylab.bar(xs1, fs1, width=0.8, facecolor='blue')
		p1 = plot(xs1, fs1, 'r')
		p2 = plot(xs2, fs2, 'c')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.savefig(fout+'.png')
		
		# generate cdf
		pylab.cla()
		cdf1 = Cdf.MakeCdfFromDict(cleanData1)
		cdf2 = Cdf.MakeCdfFromDict(cleanData2)
		p1 = plot(cdf1.xs,cdf1.ps)
		p2 = plot(cdf2.xs,cdf2.ps)
		pylab.xlim([0,146])
		pylab.ylabel('CDF')
		pylab.xlabel('Time Since Posting (every 10 min)')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.savefig(fout+'_cdf.png')
		
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
		pylab.xlim([0,146])
		pylab.ylabel('Complimentary CDF')
		pylab.xlabel('Time Since Posting (every 10 min)')
		pylab.legend((p1[0], p2[0]), ('Top 25', 'Top 26-200'), prop = fontP)
		pylab.savefig(fout+'_ccdf.png')
		
	
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
	
	def rankVsScore(self, f='rankVsScore_repeatPid.res'):
		data = self.openFile(f)
		x = []
		y = []
		for key in data:
			for value in data[key]:
				x.append(key)
				y.append(value)
		# scatter plot it
		plot(x, y, 'r.', markersize=0.1,linewidth=None,markerfacecolor='black')
		pylab.ylim([0,2000])
		pylab.ylabel('Score')
		pylab.xlabel('Rank')
		pylab.savefig('scoreVsRank.png')
		
		# run some correlations...
		print "pearson correlation", pearsonCorrelation(x, y)
		print "spearman correlation", spearmanCorrealtion(x, y)
	
	def scoreVsTime(self, f='scoreVsTime.res'):
		data = self.openFile(f)
		x = data['scrapes']
		y = data['scores']
		# change scrapes to time of day
		xCleaned = []
		for time in x:
			xCleaned.append(time.hour)
		plot(xCleaned, y, 'r.')
		pylab.ylabel('Score')
		pylab.xlabel('Hour of the day')
		pylab.savefig('scoreVsTime.png')
		print "pearson correlation", pearsonCorrelation(xCleaned, y)
		print "spearman correlation", spearmanCorrealtion(xCleaned, y)
	
	def bayesianSubreddit(self):
		fontP = FontProperties()
		fontP.set_size('small')
	
		dataReddit = self.openFile('reddit.com_bayesian.res')
		dataFunny = self.openFile('funny_bayesian.res')
		dataPics = self.openFile('pics_bayesian.res')
		
		p1 = plot(dataReddit.keys(), dataReddit.values(), 'k')
		p2 = plot(dataFunny.keys(), dataFunny.values(), 'r')
		p3 = plot(dataPics.keys(), dataPics.values(), 'b')
		pylab.ylabel('Probability of Reaching the Front Page')
		pylab.xlabel('Hour of the day')
		pylab.legend((p1[0], p2[0], p3[0]), ('r/reddit', 'r/funny', 'r/pics'), prop = fontP)
		pylab.savefig('bayesianSubreddit.png')
		
			
def main(name):
	analyze = Analyze()
	analyze.bayesianSubreddit()
	#analyze.scoreVsTime('scoreVsTime_1.res')
	#analyze.scoreVsTime('scoreVsTime_26.res')
	#analyze.rankVsScore()
	#analyze.lengthOfStay()
	#analyze.timeToReachFront()
	#analyze.postTime('peakScore_25.res', 'peakScore_200.res')
	#analyze.postTimeAutoCorrelation()
	#analyze.peakRank('peakScore_25.res', 'peakScore_200.res')
	#analyze.score()
	#analyze.score('upvotes_25.res', 'upvotes_200.res', 'Upvotes')
	#analyze.score('downvotes_25.res', 'downvotes_200.res', 'Downvotes')
	#analyze.score('score_total_25.res', 'score_total_200.res', 'Score Total')
	#analyze.subreddit()
	#analyze.repost()
	
if __name__ == '__main__':
	main(*sys.argv)
