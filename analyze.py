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

def main(name, port=3306, user='root', pw='admin', db='Reddit', pages=8):
	analyzer = Analyze(port, user, pw, db)
	print analyzer.lengthOfStay()
	print analyzer.postTime()
	#print analyzer.pathOfPosts()

if __name__ == '__main__':
    main(*sys.argv)
