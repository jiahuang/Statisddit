''' 
Jialiya Huang
ProbStat 2011
scrapes reddit frontpages
parses data and puts into a mysql table
'''

import simplejson, urllib
import datetime
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
			domain = str(MySQLdb.escape_string(item['domain']))
			subreddit = str(MySQLdb.escape_string(item['subreddit']))
			post_text = str(MySQLdb.escape_string(item['selftext'].replace(u'\u2019', "").replace(u'\u2018', "")))
			pid = str(item['id'])
			title = str(MySQLdb.escape_string(item['title'].replace(u'\u2019', "").replace(u'\u2018', "")))
			score = int(item['score'])
			over_18 = str(item['over_18'])
			thumbnail = str(MySQLdb.escape_string(item['thumbnail'])) 
			subreddit_id = str(MySQLdb.escape_string(item['subreddit_id']))
			downs = int(item['downs'])
			permalink = str(MySQLdb.escape_string(item['permalink']))
			created = str(item['created_utc'])
			url = str(MySQLdb.escape_string(item['url']))
			author = str(MySQLdb.escape_string(item['author']))
			num_comments = int(item['num_comments'])
			ups = int(item['ups'])
			fields = (rank, domain, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs, permalink, created, url, author, num_comments, ups)
			sql = """INSERT INTO Reddit.reddit(rank, site, subreddit, post_text, pid, title, score, over_18, thumbnail, subreddit_id, downs,permalink, created, url, author, num_comments, ups)  VALUES ("%s",  "%s", "%s", "%s", "%s", "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s" , "%s", "%s");""" %fields
			cursor.execute(sql)
			
		return data['after']
		
	def scrape(self, pages):
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
