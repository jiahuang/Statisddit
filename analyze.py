'''
Analyzing Statistics
'''

import datetime
import time
import sys
import Pmf, Cdf
import numpy as np
import pylab
from pylab import plot

class Analyze:
	def lengthOfStay(self, f='lengthOfStay.res'):
		# generate continous? CDF
		f = open(f,'r')
		data = eval(f.read())
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		pylab.xlim([0,1400])
		pylab.savefig('lengthOfStay.png')
	
	def timeToReachFront(self, f='timeToReachFront.res'):
		# generate cdf of time it takes to reach front vs posting
		f = open(f,'r')
		data = eval(f.read())
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		pylab.xlim([0,800])
		pylab.savefig('timeToReachFront.png')
	
	def postTime(self, f='postTime.res'):
		# generate pmf of time posted vs number of posts reaching front page/not front page
		f = open(f,'r')
		data = eval(f.read())
		pmf = Pmf.MakePmfFromDict(data)
		time = []
		numOfPosts = []
		for item in pmf.Render():
			time.append(item[0])
			numOfPosts.append(item[1])
		pylab.cla()
		plot(time,numOfPosts)
		#pylab.xlim([0,800])
		pylab.savefig('postTime.png')
	
	def peakRank(self, f='peakRank.res'):
		# generate cdf of number of posts reached max vs posting time
		f = open(f,'r')
		data = eval(f.read())
		cdf = Cdf.MakeCdfFromDict(data)
		pylab.cla()
		plot(cdf.xs,cdf.ps)
		#pylab.xlim([0,10])
		pylab.savefig('peakRank.png')

# of the 5923 posts we grabbed, only 15 were reposts

def main(name):
	analyze = Analyze()
	analyze.lengthOfStay()
	analyze.timeToReachFront()
	analyze.postTime('postTime_25.res')
	analyze.postTime('postTime_200.res')
	analyze.peakRank()
	
if __name__ == '__main__':
    main(*sys.argv)
