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

	def getRank(self, rank):
		''' returns all rows with rank '''
		sql = """ SELECT * FROM Reddit.reddit WHERE rank=%s;"""%rank
		self.cursor.execute(sql)
		return self.cursor.fetchall()
		
	def getRankInclusive(self, start, end):
		''' returns all rows (w/ unique url) between start and end '''
		fields = (start, end)
		sql = """ SELECT DISTINCT pid, id FROM Reddit.reddit WHERE rank>=%s AND rank <=%s;"""%fields
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def getField(self, column, field, value):
		''' returns column in row if field matches value '''
		fields = (column, field, value)
		sql = """ SELECT %s FROM Reddit.reddit WHERE %s='%s'"""%fields 
		self.cursor.execute(sql)
		return self.cursor.fetchall()

	def customQuery(self, sql):
		self.cursor.execute(sql)
		return self.cursor.fetchall()
