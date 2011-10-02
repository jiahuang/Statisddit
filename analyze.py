'''
Analyzing Statistics
'''

import datetime
import time
from dbHelper import DbHelper
import sys

class Analyze:
	def __init__(self, portNum, uname, pw, dbname):
		self.email = ''
		self.dbHelper = DbHelper(portNum, uname, pw, dbname)
	
	def writeRes(self, fileName, res):
		f = open(fileName, 'a')
		f.write(str(res))
		f.close()
	
	def numOfRecords(self):
		''' map datetimes to number of records collected over start and end dates'''
		''' results: missing the following records
			2011-09-19 09:30:00 125
			2011-09-15 20:50:00 100
			2011-09-15 16:50:00 50
		'''
		start = datetime.datetime(2011, 9, 7, 20, 30) #2011, 9, 7, 15, 28 #
		end = datetime.datetime(2011, 9, 20, 9, 50) #2011, 9, 7, 20, 18 #
		change = datetime.timedelta(minutes=10)
		tempChange = datetime.timedelta(minutes=5)

		timeDict = {}
		records = 0
		while start <= end:
			tempEnd = start + tempChange
			sql = "Select count(*) from Reddit.reddit WHERE scraped BETWEEN '"+str(start)+"' AND '"+str(tempEnd)+"';"
			res = self.dbHelper.customQuery(sql)
			timeDict[start] = res[0][0][0]
			records += timeDict[start]
			print start, timeDict[start], records
			start += change

		# check which ones didnt make 200 records
		print "res:"
		total = 0
		totalMissing = 0
		for key in timeDict:
			total += 200
			if timeDict[key] != 200:
				totalMissing += 200 - timeDict[key]
				print key, timeDict[key]
		print total, totalMissing, total-totalMissing
	
	def lengthOfStay(self):
		''' length that posts stay on front page (r1 to r25)'''
		posts = self.dbHelper.getRankInclusive(1, 25)
		lengthDict = {}
		for post in posts:
			# get datetimes that first and last appeared on frontpage
			fields = (post[0], 1, 25)
			sql = """ SELECT scraped FROM Reddit.reddit WHERE pid='%s' AND rank>=%s AND rank<=%s"""%fields 
			dates = self.dbHelper.customQuery(sql)
			#print dates
			minDate = min(dates[0])
			maxDate = max(dates[0])
			#print minDate, maxDate
			diff = (maxDate[0] - minDate[0]).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		self.writeRes('lengthOfStay.res', lengthDict)
		return lengthDict
		
	def timeToReachFront(self):
		''' time that it takes posts reach the front page'''
		posts = self.dbHelper.getRankInclusive(1, 25)
		lengthDict = {}
		for post in posts:
			fields = (post[0], 1, 25)
			sql = """ SELECT created, scraped FROM Reddit.reddit WHERE pid='%s' AND rank>=%s AND rank<=%s ORDER BY scraped ASC"""%fields 
			dates = self.dbHelper.customQuery(sql)
			minDateAppeared = dates[0][0][1]
			#convert date created to datetime
			created = int(round(float(dates[0][0][0])))
			createdDate = time.gmtime(created)
			createdDate = datetime.datetime.fromtimestamp(time.mktime(createdDate))
			
			diff = (minDateAppeared - createdDate).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		self.writeRes('timeToReachFront.res', lengthDict)
		return lengthDict
	
	def postTime(self, cutoffRank, beforeRank=True):
		''' time posted vs number of posts eventually reaching cutoff rank'''
		if beforeRank:
			posts = self.dbHelper.getRankInclusive(1, cutoffRank)
		else:
			posts = self.dbHelper.getRankExclusive(cutoffRank)
		
		postDict = {}
		for post in posts:
			# get time post was created
			created = self.dbHelper.getField('created', 'pid', post[0])
			created = int(round(float(created[0][0])))
			createdDate = time.gmtime(created).tm_hour
			# increment count
			postDict[createdDate] = 1 if createdDate not in postDict else postDict[createdDate] + 1
		
		self.writeRes('postTime.res', postDict)
		return postDict

	def peakRank(self):
		''' number of posts that have reached max rank vs posting time'''
		posts = self.dbHelper.getAllPosts()
		peakDict = {}
		for post in posts:
			# figure out max rank
			fields = (post[0])
			sql = """ SELECT created, scraped FROM Reddit.reddit WHERE pid='%s' ORDER BY rank, scraped ASC LIMIT 1"""%fields 
			res = self.dbHelper.customQuery(sql)
			# figure out time diff between created and scraped
			created = int(round(float(res[0][0][0])))
			scraped = res[0][0][1]
			createdDate = time.gmtime(created)
			createdDate = datetime.datetime.fromtimestamp(time.mktime(createdDate))
			
			diff = (scraped - createdDate).seconds/(60)
			peakDict[diff] = 1 if diff not in peakDict else peakDict[diff] + 1
		
		self.writeRes('peakRank.res', peakDict)
		return peakDict
		
def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	analyzer = Analyze(port, user, pw, db)
	print analyzer.lengthOfStay()
	print analyzer.timeToReachFront()
	print analyzer.numOfRecords()
	print analyzer.postTime(25)
	print analyzer.postTime(25, False)
	print analyzer.peakRank()
	
if __name__ == '__main__':
    main(*sys.argv)
