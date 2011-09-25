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
		posts = self.dbHelper.getRankInclusive(1, 25)
		lengthDict = {}
		for post in posts:
			# get datetimes that field first and last appeared on frontpage
			dates = self.dbHelper.getField("scraped", "pid", post[0])
			minDate = min(dates)
			maxDate = max(dates)
			diff = (maxDate[0] - minDate[0]).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		return lengthDict
		
	def postTime(self):
		''' time that it takes posts reach the front page'''
		posts = self.dbHelper.getRankInclusive(1, 25)
		lengthDict = {}
		for post in posts:
			# get datetimes that field was created appeared on frontpage
			created = self.dbHelper.getField("created", "pid", post[0])
			dates = self.dbHelper.getField("scraped", "pid", post[0])
			minDateAppeared = min(dates[0])
			#convert date created to datetime
			created = int(round(float(created[0][0])))
			createdDate = time.gmtime(created)
			createdDate = datetime.datetime.fromtimestamp(time.mktime(createdDate))
			
			diff = (minDateAppeared - createdDate).seconds/(60)
			# insert into dict
			lengthDict[diff] = 1 if diff not in lengthDict else lengthDict[diff] + 1
		
		return lengthDict
		
	"""	
	def pathOfPosts(self):
		''' trend in ranks that posts follow from r200 to r25-'''
	"""	

def main(name, port=3306, user='root', pw='admin', db='Reddit'):
	analyzer = Analyze(port, user, pw, db)
	#print analyzer.lengthOfStay()
	#print analyzer.postTime()
	print analyzer.numOfRecords()
	#print analyzer.pathOfPosts()

if __name__ == '__main__':
    main(*sys.argv)
