import os,sqlite3,psycopg2
#import config_local as config
import config
import psycopg2.extras
from psycopg2 import connect, extensions, sql
DEFAULT_PATH = os.path.join(os.path.dirname(__file__),'database.sqlite3')
if not config.DEBUG:
	if not config.HEROKU_DB_URL:
		config.HEROKU_DB_URL = os.getenv("DATABASE_URL")

def dbConnect(isLocal):
	if isLocal:
		conn = psycopg2.connect(user = config.DB_USER, 
		password = config.DB_PASSWORD,
		host = config.DB_HOST,
		port = config.DB_PORT,
		database = config.DB_NAME)
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
		print("dbCreate error.")
		print(e)
		s.rollback()
		c.close()
	return value

def dbEntry(sql,data,isLocal,f_id=""):
	value = False
	try:
		s = dbConnect(isLocal)
		with s:
			c = s.cursor(cursor_factory=psycopg2.extras.DictCursor)
			c.execute(sql,data)
			value = "UPDATED"
			if f_id:
				i = c.fetchone()
				return value,i
			c.close()
			return value
	except (Exception, psycopg2.DatabaseError) as e:
		print("dbEntry error.")
		print(e)
		s.rollback()
		c.close()
		return value

def dbFetch(sql,data,isLocal):
	value = False
	try:
		s = dbConnect(isLocal)
		with s:
			c = s.cursor(cursor_factory=psycopg2.extras.DictCursor)
			c.execute(sql,data)
			value = c.fetchall()
			c.close()
			return value
	except (Exception, psycopg2.DatabaseError) as e:
		print("dbFetch error.")
		print(e)
		s.rollback()
		c.close()
		return value	
