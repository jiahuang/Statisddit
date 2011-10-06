'''
Helper for grabbing data from MySQL
'''

import datetime
import time
import MySQLdb
import sys

class DbHelper:
	def __init__(self, portNum, uname, pw, dbname):
		self.email = ''
		self.db = MySQLdb.connect(host="localhost", port=portNum, user=uname, passwd=pw, db=dbname)
		self.cursor = self.db.cursor()

	def getAllPosts(self):
		''' returns all unique posts'''
		sql = """ SELECT DISTINCT pid FROM Reddit.reddit;"""
		self.cursor.execute(sql)
		return self.cursor.fetchall()
		
	def getRank(self, rank):
		''' returns all rows with rank '''
		sql = """ SELECT * FROM Reddit.reddit WHERE rank=%s;"""%rank
		self.cursor.execute(sql)
		return self.cursor.fetchall()
		
	def getRankInclusive(self, end):
		''' returns all rows (w/ unique post ids) between start and end ranks'''
		fields = (end)
		sql = """ SELECT pid, created, subreddit FROM Reddit.reddit WHERE rank <=%s GROUP BY pid;"""%fields
		self.cursor.execute(sql)
		return self.cursor.fetchall()
		
	def getRankExclusive(self, rank):
		''' returns all wors (w/ unique post ids) that never reach rank'''
		fields = (rank, rank)
		sql = """ SELECT DISTINCT pid, created, subreddit FROM Reddit.reddit WHERE rank>%s AND pid NOT IN (SELECT DISTINCT pid FROM Reddit.reddit WHERE rank<=%s)"""%fields
		self.cursor.execute(sql)
		return self.cursor.fetchall()
		
	def getTimeInclusive(self, start, end):
		''' returns all rows (w/ unique post ids) between start and end times'''
		fields = (str(start), str(end))
		sql = """Select DISTINCT pid from Reddit.reddit WHERE scraped BETWEEN '%s' AND '%s';"""%fields
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def getField(self, column, field, value):
		''' returns column in row if field matches value '''
		fields = (column, field, value)
		sql = """ SELECT %s FROM Reddit.reddit WHERE %s='%s'"""%fields 
		self.cursor.execute(sql)
		return self.cursor.fetchall()
	
	def getPath(self, pid):
		''' returns list of ranks ordered by ascending scraped date taken by a post over its lifespan'''
		sql = """Select rank, scraped, ups, downs, score, num_comments, created from Reddit.reddit where pid='%s' ORDER BY scraped ASC"""%pid
		self.cursor.execute(sql)
		return self.cursor.fetchall()
	
	def customQuery(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()
