'''
Cleaning up data
'''

import datetime
import time
from dbHelper import DbHelper
import sys

class Cleanup:
	def __init__(self, portNum, uname, pw, dbname):
		self.dbHelper = DbHelper(portNum, uname, pw, dbname)

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
		
	def removeEdgeData(self, time):
		''' moves rows from main table to aux table
		rows should satisfy the following conditions:
		1. already on the front page when bot started
		2. was still on the front page when bot ended
		'''
		tempChange = datetime.timedelta(minutes=5)
		
		# find rows that were on the front page during this time
		res = self.dbHelper.getTimeInclusive(time, time + tempChange)
		print "Number of pids to be affected by cleanup: ", len(res)
		for item in res:
			pid = item[0]
			#print self.dbHelper.getField('*', 'pid', pid)
			# move row to aux table
			sql = ("INSERT INTO Reddit.moved (scraped, rank, site, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs,permalink, created, url, author, num_comments, ups)"
					" SELECT scraped, rank, site, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs,permalink, created, url, author, num_comments, ups FROM Reddit.reddit"
					" WHERE pid = '"+pid+"';")
			resMove = self.dbHelper.customQuery(sql)
			# delete row from regular table
			sql = ("DELETE from Reddit.reddit WHERE pid='"+pid+"';")
			resDelete = self.dbHelper.customQuery(sql)
			print "Moved", resMove[1], 'row(s) and deleted ', resDelete[1],"row(s) with pid", pid
		

def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	clean = Cleanup(port, user, pw, db)
	start = datetime.datetime(2011, 9, 7, 20, 30)
	clean.removeEdgeData(start)
	end = datetime.datetime(2011, 9, 20, 9, 50)
	clean.removeEdgeData(end)

if __name__ == '__main__':
    main(*sys.argv)
