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
			createdDate = datetime.datetime.utcfromtimestamp(float(post[1]))
			# add 4 hours because I messed up on writing to the db with gm time
			minDateAppeared = minDateAppeared + datetime.timedelta(hours=4)
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

	def peakRank(self, posts, f):
		''' number of posts that have reached max rank vs posting time'''
		peakDict = {}
		for post in posts:
			# figure out max rank
			fields = (post[0])
			sql = """ SELECT created, scraped FROM Reddit.reddit WHERE pid='%s' ORDER BY rank, scraped ASC LIMIT 1"""%fields 
			res = self.dbHelper.customQuery(sql)
			# figure out time diff between created and scraped
			scraped = res[0][1]
			createdDate = datetime.datetime.utcfromtimestamp(float(res[0][0]))
			# add 4 hours because I messed up on writing to the db with gm time
			scraped = scraped + datetime.timedelta(hours=4)
			diff = (scraped - createdDate).seconds/(60)
			peakDict[diff] = 1 if diff not in peakDict else peakDict[diff] + 1
		
		self.writeRes(f, peakDict)
		
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
	
	def score(self, posts, f, scoreType=0, change=False):
		''' score since time posting
		Score type 0: total score
		score type 1: upvotes
		otherwise: downvotes
		'''
		if scoreType == 0:
			sqlScore = "score"
		elif scoreType == 1:
			sqlScore = "ups"
		else:
			sqlScore = "downs"
		scoreDict = {}
		for post in posts:
			fields = (post[0])
			sql = """SELECT """+sqlScore+""", scraped FROM Reddit.reddit WHERE pid='%s' ORDER BY scraped ASC;"""%fields
			res = self.dbHelper.customQuery(sql)
			createdDate = datetime.datetime.utcfromtimestamp(float(post[1]))
			print post[0], post[1], createdDate
			# map it to time since creation
			#score = 0
			for r in res:
				if change: # change in score
					score = r[0] - score
				else:
					score = r[0] 
				scraped = r[1]
				# add 4 hours because I messed up on writing to the db with gm time
				scraped = scraped + datetime.timedelta(hours=4)
				diff = (scraped - createdDate).seconds/(60)
				if diff in scoreDict:
					prev = scoreDict[diff]
					scoreDict[diff] = (prev[0]+score, prev[1]+1)
				else:
					scoreDict[diff] = (score, 1)
		self.writeRes(f, scoreDict)
		return scoreDict
	
	def subreddit(self, posts, f):
		subredditDict = {}
		for post in posts:
			subredditDict[post[2]] = 1 if post[2] not in subredditDict else subredditDict[post[2]] + 1
		self.writeRes(f, subredditDict)
		return subredditDict
	
def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	grab = Grab(port, user, pw, db)
	#print grab.lengthOfStay()
	#print grab.timeToReachFront()
	#print grab.postTime(25)
	#print grab.postTime(25, False)
	#print grab.repost()
	posts = grab.dbHelper.getRankInclusive(25)
	print grab.score(posts, 'score_total_25.res', 0)
	print grab.score(posts, 'upvotes_25.res', 1)
	print grab.score(posts, 'downvotes_25.res', 2)
	#print grab.peakRank(posts, 'peakRank_25.res')
	#print grab.score(posts, 'score_25.res')
	#print grab.subreddit(posts, 'subreddit_25.res')
	pids = ",".join(["'"+post[0]+"'" for post in posts])
	sql = "SELECT pid,created, subreddit FROM Reddit.reddit WHERE rank>"+str(25)+" AND pid NOT IN ("+pids+") GROUP BY pid"
	posts = grab.dbHelper.customQuery(sql)
	print grab.score(posts, 'score_total_200.res', 0)
	print grab.score(posts, 'upvotes_200.res', 1)
	print grab.score(posts, 'downvotes_200.res', 2)
	#print grab.score(posts, 'score_200.res')
	#print grab.peakRank(posts, 'peakRank_200.res')
	#print grab.subreddit(posts, 'subreddit_200.res')
	
if __name__ == '__main__':
    main(*sys.argv)
