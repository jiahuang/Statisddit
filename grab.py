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
	
	def postTime(self, posts, f):
		''' time posted vs number of posts eventually reaching cutoff rank'''
		postDict = {}
		for post in posts:
			# get time post was created
			created = int(round(float(post[1])))
			createdHour = time.gmtime(created).tm_hour
			createdDate = time.gmtime(created).tm_yday
			# increment count
			if createdDate in postDict:
				postDict[createdDate][createdHour] = 1 if createdHour not in postDict[createdDate] else postDict[createdDate][createdHour]+1
			else:
				postDict[createdDate] = {createdHour:1}
		
		self.writeRes(f, postDict)
		return postDict

	def peak(self, posts, f, peakType="Rank"):
		''' number of posts that have reached max rank vs posting time'''
		peakDict = {}
		for post in posts:
			# figure out max rank
			fields = (post[0], peakType)
			sql = """ SELECT created, scraped FROM Reddit.reddit WHERE pid='%s' ORDER BY %s, scraped ASC LIMIT 1"""%fields 
			res = self.dbHelper.customQuery(sql)
			# figure out time diff between created and scraped
			scraped = res[0][1]
			createdDate = datetime.datetime.utcfromtimestamp(float(res[0][0]))
			# add 4 hours because I messed up on writing to the db with gm time
			scraped = scraped + datetime.timedelta(hours=4)
			diff = (scraped-createdDate).days*1440 + (scraped - createdDate).seconds/(60)
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
	
	def score(self, posts, f, byRank=False, overallScore=True, upsOnly=False, downsOnly=False):
		''' score since time posting'''
		scoreDict = {}
		for post in posts:
			fields = (post[0])
			sql = """SELECT scraped, created, score, ups, downs, rank FROM Reddit.reddit WHERE pid='%s' ORDER BY scraped ASC;"""%fields
			res = self.dbHelper.customQuery(sql)
			createdDate = datetime.datetime.utcfromtimestamp(float(post[1]))
			print post[0], post[1], createdDate
			# map it to time since creation
			oldScore = 0
			oldUps = 0
			oldDowns = 0
			for r in res:
				scraped = r[0]
				# add 4 hours because I messed up on writing to the db with gm time
				scraped = scraped + datetime.timedelta(hours=4)
				diff = (scraped-createdDate).days*1440 + (scraped - createdDate).seconds/(60)
				if byRank: 
					rank = r[5]
					ups = r[3] - oldUps
					oldUps = r[3]
					downs = r[4] - oldDowns
					oldDowns = r[4]
					if rank in scoreDict:
						upsList =  scoreDict[rank][0]
						upsList.append(ups)
						downsList =  scoreDict[rank][1]
						downsList.append(downs)
						diffList =  scoreDict[rank][2]
						diffList.append(diff)
						scoreDict[rank] = (upsList, downsList, diffList)
					else:
						scoreDict[rank] = ([ups], [downs], [diff])
				else:
					if not overallScore:
						score = r[2] - oldScore
						oldScore = r[2]
					else:
						score = r[2]
					if upsOnly:
						score = r[3]
					if downsOnly:
						score = r[4] 
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
	
	def bayesianSubreddit(self, subreddit):
		fields = (25, subreddit)
		sql = """SELECT pid, created FROM Reddit.reddit WHERE rank <=%s AND subreddit='%s' GROUP BY pid ORDER BY created;"""%fields
		res = self.dbHelper.customQuery(sql)
		subredditDict = {}
		for hour in range(0, 24):
			number = 0.0
			for item in res:
				createdDate = datetime.datetime.utcfromtimestamp(float(item[1]))
				if createdDate.hour == hour:
					number += 1
			subredditDict[hour] = number
		
		fields = (200, subreddit)
		sql = """SELECT pid, created FROM Reddit.reddit WHERE rank <=%s AND subreddit='%s' GROUP BY pid ORDER BY created;"""%fields
		res = self.dbHelper.customQuery(sql)
		for hour in range(0, 24):
			number = 0.0
			for item in res:
				createdDate = datetime.datetime.utcfromtimestamp(float(item[1]))
				if createdDate.hour == hour:
					number += 1
			if subredditDict[hour] != 0:
				subredditDict[hour] = subredditDict[hour]/number
				
		self.writeRes(subreddit+'_bayesian.res', subredditDict)
		return subredditDict
	
	def rankVsScore(self, f):
		rankDict = {}
		for rank in range(1, 201):
			fields = (rank)
			sql = """SELECT score FROM Reddit.reddit WHERE rank=%s"""%fields
			res = self.dbHelper.customQuery(sql)
			scoreList = []
			for r in res:
				scoreList.append(r[0])
			rankDict[rank] = scoreList
		self.writeRes(f, rankDict)
		return rankDict
	
	def scoreVsTime(self, f, rank):
		resDict = {}
		fields = (rank)
		sql = """SELECT score, scraped FROM Reddit.reddit WHERE rank=%s ORDER BY scraped ASC"""%fields
		res = self.dbHelper.customQuery(sql)
		scores = []
		scrapes = []
		for item in res:
			scores.append(item[0])
			scrapes.append(item[1])
		resDict['scores'] = scores
		resDict['scrapes'] = scrapes
		self.writeRes(f, resDict)
		return resDict
	
def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	grab = Grab(port, user, pw, db)
	#print grab.rankVsScore('rankVsScore.res')
	print grab.bayesianSubreddit('reddit.com')
	print grab.bayesianSubreddit('pics')
	print grab.bayesianSubreddit('funny')
	
	'''
	print grab.scoreVsTime('scoreVsTime_1.res', 1)
	print grab.scoreVsTime('scoreVsTime_26.res', 26)
	print grab.scoreVsTime('scoreVsTime_51.res', 51)
	#print grab.lengthOfStay()
	#print grab.timeToReachFront()
	#print grab.postTime(25, False)
	#print grab.repost()
	posts = grab.dbHelper.getRankInclusive(25)
	#print grab.postTime(posts, 'post_time_25.res')
	#print grab.score(posts, 'score_total_25.res')
	#print grab.score(posts, 'score_change_25.res', False, False)
	#print grab.score(posts, 'upvotes_25.res', False, False, True)
	#print grab.score(posts, 'downvotes_25.res', False, False, False, True)
	#print grab.peak(posts, 'peakScore_25.res', 'score')
	#print grab.score(posts, 'score_25.res')
	#print grab.subreddit(posts, 'subreddit_25.res')
	
	pids = ",".join(["'"+post[0]+"'" for post in posts])
	sql = "SELECT pid,created, subreddit FROM Reddit.reddit WHERE rank>"+str(25)+" AND pid NOT IN ("+pids+") GROUP BY pid"
	posts = grab.dbHelper.customQuery(sql)
	#print grab.postTime(posts, 'post_time_200.res')
	#print grab.score(posts, 'score_total_200.res')
	#print grab.score(posts, 'score_change_200.res', False, False)
	#print grab.score(posts, 'upvotes_200.res', False, False, True)
	#print grab.score(posts, 'downvotes_200.res', False, False, False, True)
	#print grab.score(posts, 'score_200.res')
	#print grab.peak(posts, 'peakScore_25.res', 'score')
	#print grab.subreddit(posts, 'subreddit_200.res')
	
	#posts = grab.dbHelper.getRankInclusive(200)
	#print grab.score(posts, 'changed_all.res', True)
	'''
	
	
if __name__ == '__main__':
    main(*sys.argv)
