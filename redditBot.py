''' 
Jialiya Huang
ProbStat 2011
scrapes reddit frontpages
parses data and puts into a mysql table
'''

import simplejson, urllib
import datetime
import time
import MySQLdb
import sys

class RedditBot:
	def __init__(self, portNum, uname, pw, dbname):
		self.email = ''
		self.db = MySQLdb.connect(host="localhost", port=portNum, user=uname, passwd=pw, db=dbname)
	
	def scrape_helper(self, url, page):
		result = simplejson.load(urllib.urlopen(url))
		if 'Error' in result:
			print 'An error occured: ' + result['Error']
		# parse out data 
		data = result['data']
		datalist = data['children']
		# write data to a file
		now = datetime.datetime.now()
		filename = 'redditBot-'+str(now.day)+'-'+str(now.hour)+'.log'
		f = open(filename, 'a')
		
		# parse and stick it into the db
		cursor = self.db.cursor()
		for i,item in enumerate(datalist):
			f.write(str(item))
			item = item['data']
			rank = page*25+(i+1)
			domain = MySQLdb.escape_string(item['domain'].encode('utf8'))
			subreddit = MySQLdb.escape_string(item['subreddit'])
			post_text = MySQLdb.escape_string(item['selftext'].encode('utf8'))
			pid = str(item['id'])
			title = MySQLdb.escape_string(item['title'].encode('utf8'))
			score = int(item['score'])
			over_18 = str(item['over_18'])
			thumbnail = MySQLdb.escape_string(item['thumbnail'].encode('utf8')))
			subreddit_id = MySQLdb.escape_string(item['subreddit_id'])
			downs = int(item['downs'])
			permalink = MySQLdb.escape_string(item['permalink'].encode('utf8'))
			created = str(item['created_utc'])
			url = MySQLdb.escape_string(item['url'].encode('utf8'))
			author = MySQLdb.escape_string(item['author'].encode('utf8'))
			num_comments = int(item['num_comments'])
			ups = int(item['ups'])
			fields = (rank, domain, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs, permalink, created, url, author, num_comments, ups)
			sql = """INSERT INTO Reddit.reddit(rank, site, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs,permalink, created, url, author, num_comments, ups)  VALUES ("%s",  "%s", "%s", "%s", "%s", "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s", "%s");""" %fields
			cursor.execute(sql)
		
		print "Inserted ranks ", page*25, " to ", (page+1)*25, " at ", time.ctime()
		return data['after']
		
	def scrape(self, pages):
		print "Starting scrape at ", time.ctime()
		after = ''
		for i in range(0, pages):
			if after == '':
				url = 'http://www.reddit.com/.json?sort=rank'
			else:
				url = 'http://www.reddit.com/.json?&count=25&after='+str(after)+'&sort=rank'
			
			after = self.scrape_helper(url, i)

def main(name, port=3306, user='root', pw='admin', db='Reddit', pages=8):
	bot = RedditBot(port, user, pw, db)
	bot.scrape(pages)

if __name__ == '__main__':
    main(*sys.argv)
