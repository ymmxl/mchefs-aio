import os,sqlite3,psycopg2
import config
from psycopg2 import connect, extensions, sql
DEFAULT_PATH = os.path.join(os.path.dirname(__file__),'database.sqlite3')
if not config.DEBUG:
	if not config.HEROKU_DB_URL:
		config.HEROKU_DB_URL = os.getenv("DATABASE_URL")

def dbConnect(isLocal):
	if isLocal:
		conn = sqlite3.connect(DEFAULT_PATH)
	else:
		conn = psycopg2.connect(config.HEROKU_DB_URL,sslmode = "require")
		conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
	return conn

def dbCreate(sql,isLocal):
	value = False
	try:
		s = dbConnect(isLocal)
		with s:
			c = s.cursor()
			c.execute(sql)
			value = True
			c.close()
	except (Exception, psycopg2.DatabaseError) as e:
		print("Database error.")
		print(e)
		s.rollback()
		c.close()
	return value

def dbEntry(sql,data,isLocal,f_id=""):
	value = False
	try:
		s = dbConnect(isLocal)
		with s:
			c = s.cursor()
			c.execute(sql,data)
			value = "UPDATED"
			if f_id:
				i = c.lastrowid
				return value,i
			c.close()
			return value
	except (Exception, psycopg2.DatabaseError) as e:
		print("Database error.")
		print(e)
		s.rollback()
		c.close()
		return value

def dbFetch(sql,data,isLocal):
	value = False
	try:
		s = dbConnect(isLocal)
		with s:
			s.row_factory = sqlite3.Row
			c = s.cursor()
			c.execute(sql,data)
			value = c.fetchall()
			c.close()
			return value
	except (Exception, psycopg2.DatabaseError) as e:
		print("Database error.")
		print(e)
		s.rollback()
		c.close()
		return value	
