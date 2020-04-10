import discord, json,psycopg2,os
from psycopg2 import connect, extensions, sql
#from discord.ext.commands import Bot
from discord.ext import commands
import config

if not config.DEBUG:
	if not config.HEROKU_DB_URL:
		config.HEROKU_DB_URL = os.getenv("DATABASE_URL")
class kw_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.init()
	def init(self):
		ss = "CREATE TABLE IF NOT EXISTS kw_list(keywords TEXT UNIQUE)"
		result = self.dbEntry(ss,None,"create")
		if result:
			print("DATABASE successfully initialized.")
	def get_session(self):
		if not config.DEBUG:
			conn = psycopg2.connect(config.HEROKU_DB_URL,sslmode = "require")
		else:
			conn = psycopg2.connect(user = config.DB_USER, 
				password = config.DB_PASSWORD,
				host = config.DB_HOST,
				port = config.DB_PORT,
				database = config.DB_NAME)
		conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
		return conn
	def dbEntry(self,sql,data,mode):
		value = False
		if not sql and sql.isspace():
			print("no sql submitted.")
		else:
			try:
				if not data:
					s = self.get_session()
					with s:
						c = s.cursor()
						c.execute(sql)
						if mode == "fetch":
							value = c.fetchall()
						elif mode == "create":
							value = True
						c.close()
					return value
				else:
					s = self.get_session()
					with s:
						c = s.cursor()
						for i in data:
							c.execute(sql,i)
						c.close()
					value = True
					print("Successfully added data.")
			except (Exception, psycopg2.DatabaseError) as e:
				print("Error.\n{}".format(e))
				return value
		return value
	def save(self,data):
		ss = """INSERT INTO kw_list(keywords) VALUES(%s)"""
		#formatting data into sets
		dataList = []
		for i in data:
			d = (i,)
			dataList.append(d)
		entry = self.dbEntry(ss,dataList,None)
		return entry
	def remove(self,data):
		ss = """DELETE FROM kw_list WHERE keywords=%s"""
		#formatting data into sets
		dataList = []
		for i in data:
			d = (i,)
			dataList.append(d)
		entry = self.dbEntry(ss,dataList,None)
		return entry
	def get_list(self):
		ss = """SELECT keywords FROM kw_list"""
		k = self.dbEntry(ss,None,"fetch")
		if not k:
			return []
		else:
			return [i[0] for i in k]

	@commands.Cog.listener()
	async def on_ready(self):
		print('{} kw module logged in!'.format(self.client.user.name))
		await self.client.change_presence(activity=discord.Game("v2.0 @Cracked"))

	@commands.command(pass_context=True)
	async def kw_list(self,message):
		current_kw = self.get_list()
		await message.channel.send("Currently monitoring: `[{}]`".format(",".join(i for i in current_kw)))
		print("kw_list called successfully.")
	
	@commands.command(pass_context=True)
	async def add_kw(self,message,*,kw:str):
		#try:
		#check format
		current_kw = self.get_list()
		dmp = []
		tmp = kw.split(",")
		for i in tmp:
			if "-" not in i:
				await message.channel.send("Check your SKU format shabi. Ex.(802022-401)")
				return
		#filtering duplicates
		tmp = list(set(tmp))
		#check if exists:
		if current_kw:
			for j in tmp:
				if j in current_kw:
					dmp.append(j)
					tmp.remove(j)
		if dmp!=[]:
			await message.channel.send("SKU(s): `[{}]` already exists.".format(",".join(i for i in dmp)))
		if tmp!=[]:
			done = self.save(tmp)
			if done:
				await message.channel.send("Successfully added SKU(s) to kw list. To view current kw list please enter `!kw_list`")
				print("sku(s): [{}] addded successfully.".format(",".join(i for i in tmp)))
	@commands.command(pass_context=True)
	async def remove_kw(self,message,*,kw:str):
		current_kw = self.get_list()
		dump = []
		t=[]
		#check format
		temp = kw.split(",")
		for j in temp:
			if "-" not in j:
				await message.channel.send("Check your SKU format shabi. Ex.(802022-401)")
				raise
		#check for duplicates
		temp = list(set(tmp))
		for j in temp:
			if not j in current_kw:
				dump.append(j)
			else:
				t.append(j)
				current_kw.remove(j)
		if dump!=[] and t == []:		
			await message.channel.send("SKU(s): `[{}]` not found in current list. Please try again.".format(",".join(i for i in dump)))
			raise
		elif dump!=[] and t!=[]:
			await message.channel.send("SKU(s): `[{}]` not found in current list. Please try again.".format(",".join(i for i in dump)))
			await message.channel.send("Successfully removed SKU(s): `[{}]`.".format(",".join(i for i in t)))
		else:
			await message.channel.send("Successfully removed SKU(s): `[{}]`.".format(",".join(i for i in t)))
		self.remove(t)
		print("sku(s): [{}] removed successfully.".format(",".join(i for i in t)))
	"""
	@commands.command(pass_context=True)
	async def clear_kw(self,message):
		current_kw = []
		self.save(current_kw)
		await message.channel.send("kw_list cleared.")
	"""

#if __name__ == "__main__":
def setup(client):
	client.add_cog(kw_bot(client))