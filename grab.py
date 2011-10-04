'''
Grabbing Statistics
'''

import datetime
import time
from dbHelper import DbHelper
import sys

class Grab:
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
			timeDict[start] = res[0][0]
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
		sql = """SELECT pid, MAX(scraped), MIN(scraped) FROM Reddit.reddit WHERE rank<25 GROUP BY pid;"""
		posts = self.dbHelper.customQuery(sql)
		lengthDict = {}
		for post in posts:
			# get datetimes that first and last appeared on frontpage
			minDate = post[2]
			maxDate = post[1]
			#print minDate, maxDate
			diff = (maxDate - minDate).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		self.writeRes('lengthOfStay.res', lengthDict)
		return lengthDict
		
	def timeToReachFront(self):
		''' time that it takes posts reach the front page'''
		sql = """ SELECT pid, created, MIN(scraped) FROM Reddit.reddit WHERE rank>=1 AND rank<=25 GROUP BY pid"""
		posts = self.dbHelper.customQuery(sql)
		lengthDict = {}
		for post in posts:
			minDateAppeared = post[2]
			#convert date created to datetime
			created = int(round(float(post[1])))
			createdDate = time.gmtime(created)
			createdDate = datetime.datetime.fromtimestamp(time.mktime(createdDate))
			# add 5 hours because I messed up on writing to the db with gm time
			minDateAppeared = minDateAppeared + datetime.timedelta(hours=5)
			diff = (minDateAppeared - createdDate).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		self.writeRes('timeToReachFront.res', lengthDict)
		return lengthDict
	
	def postTime(self, cutoffRank, beforeRank=True):
		''' time posted vs number of posts eventually reaching cutoff rank'''
		posts = self.dbHelper.getRankInclusive(1, cutoffRank)
		
		if not beforeRank:
			pids = ",".join(["'"+post[0]+"'" for post in posts])
			sql = "SELECT pid,created FROM Reddit.reddit WHERE rank>"+str(cutoffRank)+" AND pid NOT IN ("+pids+") GROUP BY pid"
			posts = self.dbHelper.customQuery(sql)
		
		postDict = {}
		for post in posts:
			# get time post was created
			created = int(round(float(post[1])))
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
			created = int(round(float(res[0][0])))
			scraped = res[0][1]
			createdDate = time.gmtime(created)
			createdDate = datetime.datetime.fromtimestamp(time.mktime(createdDate))
			# add 5 hours because I messed up on writing to the db with gm time
			scraped = scraped + datetime.timedelta(hours=5)
			diff = (scraped - createdDate).seconds/(60)
			peakDict[diff] = 1 if diff not in peakDict else peakDict[diff] + 1
		
		self.writeRes('peakRank.res', peakDict)
		
		return peakDict
	
	def repost(self):
		''' number of posts that are repeats, ie different pids share same url'''
		sql = """SELECT url from Reddit.reddit GROUP BY url HAVING COUNT(DISTINCT pid) > 1;"""
		res = self.dbHelper.customQuery(sql)
		firstPosts = []
		repeatPosts = []
		for item in res:
			fields = (item[0])
			sql = """SELECT pid FROM Reddit.reddit WHERE url='%s' GROUP BY pid ORDER BY created ASC;"""%fields
			posts = self.dbHelper.customQuery(sql)
		
			for i, post in enumerate(posts):
				fields = (post[0])
				sql = """SELECT rank FROM Reddit.reddit WHERE pid='%s' ORDER BY scraped ASC;"""%fields
				ranks = self.dbHelper.customQuery(sql)
				resRanks = [rank[0] for rank in ranks]
				if i == 0: # get all the ranking data of the url that was posted first
					firstPosts.append(resRanks)
				else: # get all ranking data of urls that were posted later
					repeatPosts.append(resRanks)
		
		# write to file
		self.writeRes('firstPosts.res', firstPosts)
		self.writeRes('repeatPosts.res', repeatPosts)
		return firstPosts, repeatPosts
	
def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	grab = Grab(port, user, pw, db)
	#print grab.lengthOfStay()
	#print grab.timeToReachFront()
	#print grab.postTime(25)
	#print grab.postTime(25, False)
	#print grab.peakRank()
	print grab.repost()
	
if __name__ == '__main__':
    main(*sys.argv)
