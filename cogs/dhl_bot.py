import discord, json,psycopg2,os,re
from psycopg2 import connect, extensions, sql
#from discord.ext.commands import Bot
from datetime import datetime as dt
from discord.ext import commands
#import config_local as config
import config
from utils.db_utils import dbCreate, dbEntry, dbFetch
from utils.pickup import Pickup


class dhl_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.init()
	def init(self):
		ss = """
			CREATE TABLE IF NOT EXISTS add_list(
				id SERIAL PRIMARY KEY,
				profile_name text NOT NULL,
				name text NOT NULL,
				email text NOT NULL,
				phone text NOT NULL,
				add1 text NOT NULL
				CHECK(
					LENGTH(add1) <= 35
				),
				add2 text
				CHECK(
					LENGTH(add2) <= 35
				),
				postcode text NOT NULL,
				city text NOT NULL,
				state text NOT NULL
			)"""
		ss2 = """
			CREATE TABLE IF NOT EXISTS user_list(
				id SERIAL PRIMARY KEY,
				discord_id bigint NOT NULL,
				add_id integer, 
				FOREIGN KEY (add_id) REFERENCES add_list(id)
			)"""
		t1 = dbCreate(ss,config.DEBUG)
		t2 = dbCreate(ss2,config.DEBUG)
		if (t1 and t2):
			print("DATABASE successfully initialized.")

	@commands.Cog.listener()
	async def on_ready(self):
		print('{} DHL module logged in!'.format(self.client.user.name))
		await self.client.change_presence(activity=discord.Game("v2.0 @Cracked"))

	def save(self,d,discord_id):
		v = False
		add_sql = """INSERT INTO add_list(profile_name,name,email,phone,add1,add2,postcode,city,state) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id"""
		entry1,add_id = dbEntry(add_sql,(d["profile_name"],d["name"],d["email"],d["phone"],d["add1"],d["add2"],d["postcode"],d["city"],d["state"]),isLocal=config.DEBUG,f_id=True)
		print(add_id)
		print(entry1)
		if add_id:
			aid = add_id[0]
			user_sql = """INSERT INTO user_list(discord_id,add_id) VALUES (%s,%s)"""
			entry2 = dbEntry(user_sql,(discord_id,aid),isLocal=config.DEBUG)
			if (entry1 and entry2) == "UPDATED":
				print("Successfully added add_list and user_list")
				v = True
		return	v

	def fetch(self,discord_id):
		f_sql = """SELECT add_id FROM user_list WHERE discord_id=%s"""
		add_ids = dbFetch(f_sql,(discord_id,),config.DEBUG)
		p = []
		if add_ids:
			for i in add_ids:
				a_sql = """SELECT * FROM add_list WHERE id=%s"""
				result = dbFetch(a_sql,(i["add_id"],),config.DEBUG)
				p.append(result)
		return p

	@commands.command(pass_context = True)
	async def dhl_list (self,message):
		if not message.channel.type is discord.ChannelType.private:
			await message.channel.send("> This command only works in DMs.", delete_after=5)
			return
		discord_id = message.author.id
		await message.channel.send("> Fetching profiles.")
		profiles = self.fetch(discord_id)
		if not profiles:
			await message.channel.send(">>> You have no profiles set.\nUse `!dhl_save [profile name]` to save one.")
			return
		else:
			p = []
			for j in profiles:
				for i in j:
					t = {
					"profile_name":i["profile_name"],
					"name":i["name"],
					"email":i["email"],
					"phone":i["phone"],
					"add1":i["add1"],
					"add2":i["add2"],
					"postcode":i["postcode"],
					"city":i["city"],
					"state":i["state"]
					}
					p.append(t)
			for i in p:
				await message.channel.send("```json\n{}```".format(json.dumps(i,indent=4)))

	@commands.command(pass_context=True)
	async def dhl_save (self,message,*,kw:str):
		if not message.channel.type is discord.ChannelType.private:
			await message.channel.send("> This command only works in DMs.", delete_after=5)
			return
		channel = message.channel
		discord_id = message.author.id
		profile_name = kw
		if " " in profile_name:
			await message.channel.send("> Error in profile name. type `!help dhl_save` to learn more.")
			return
		exists = []
		for j in self.fetch(discord_id):
			for i in j:
				exists.append(i["profile_name"])
		if profile_name in exists:
			await message.channel.send(">>> Profile already exists. \nPlease try another profile name\nExisting: `{}`".format(','.join(i for i in exists)))
			return
		def check(m):
			return m.author == message.author and  m.channel == channel

		d = "Saving address for profile: `{}`".format(kw)
		d += "\nPlease give your details in the following format, separated with `\\`:"
		d += "\n`name\\email\\phone`"
		d += "\n`ie:Johnny Bravo\\cracked@mchefsolution.com\\0123456789`"
		d += "\n\nOr type `cancel` to cancel."
		#embed = discord.Embed(color = 9055202,title = "DHL Address Entry",description=d)
		await message.channel.send(">>> {}".format(d))
		try:
			details = await self.client.wait_for("message",check=check,timeout=50.0)
		except asyncio.TimeoutError:
			await message.channel.send("Timed out.")
			return
		if details.content == "cancel":
			await message.channel.send("cancelled.")
			return
		u = details.content.split("\\")
		try:
			name = u[0]
			email = u[1]
			phone = u[2]
		except Exception:
			await message.channel.send("Error. Please check your input and try again.")
			return
		e = "Continued."
		e += "\nPlease enter address details in the following format, separated with `\\`"
		e += "\n`add1\\add2\\postCode\\city\\state`"
		e += "\n`ie:88 baker st\\tmn baker\\80000\\johor bahru\\johor`"
		e += "\n\nNOTE: Max 35 characters in ADD1 and ADD2 only."
		e += "\n\nOr type `cancel` to cancel."
		#embed = discord.Embed(color = 9055202,title = "DHL Address Entry",description=e)
		await message.channel.send(">>> {}".format(e))

		try:
			details2 = await self.client.wait_for("message",check=check,timeout=100.0)
		except asyncio.TimeoutError:
			await message.channel.send("Timed out.")
			return

		if details2.content == "cancel":
			await message.channel.send("cancelled.")
			return
		t = details2.content.split("\\")
		try:
			add1 = t[0]
			add2 = t[1]
			postcode = t[2]
			city = t[3]
			state = t[4]
		except Exception:
			await message.channel.send("Error. Please check your input and try again.")
			return
		f = {
			"profile_name":profile_name,
			"name":name,
			"email":email,
			"phone":phone,
			"add1":add1,
			"add2":add2,
			"postcode":postcode,
			"city":city,
			"state":state
		}
		await message.channel.send("Preview:\n```json\n{}```".format(json.dumps(f,indent=4)))
		await message.channel.send("type `y` to proceed or `n` to cancel.")
		proceed = await self.client.wait_for("message",check=check)
		if proceed.content == "y":
			done = self.save(f,discord_id)
			if done:
				await message.channel.send("profile successfully saved.")
		else:
			await message.channel.send("Aborted")
			return

	@commands.command(pass_context=True,
						help = "!dhl_pickup [profile name],[awbill],[yyyy-mm-dd],[hh:mm in 24h],[number or parcels]")
	async def dhl_pickup(self,message,*,kw:str):
		if not message.channel.type is discord.ChannelType.private:
			await message.channel.send("> This command only works in DMs.", delete_after=5)
			return
		discord_id = message.author.id
		channel = message.channel
		def check(m):
			return m.author == message.author and  m.channel == channel
		args = kw.split(",")
		if not len(args) == 5:
			await message.channel.send("> incomplete input. check `!help dhl_pickup`")
			return
		profile_name = args[0]
		awbill = args[1].replace(" ","")
		package = args[4]
		try:
			if args[2].lower() == "today":
				date = dt.today().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore")).strftime("%Y-%m-%d")
			elif dt.strptime(args[2],"%Y-%m-%d"):
				date = dt.strptime(args[2],"%Y-%m-%d").strftime("%Y-%m-%d")
			else:
				date = None
		except Exception as e:
			print("Error parsing date: {}".format(e))
			date = None

		try:
			time = args[3] if dt.strptime(args[3],"%H:%M") else None
		except Exception as e:
			print("Error parsing time: {}".format(e))
			time = None
		if not all([profile_name,awbill,date,time]):
			await message.channel.send("> Error in command please check your input or `!help dhl_pickup`")
			return
		else:
			profiles = self.fetch(discord_id)
			f = {}
			for j in profiles:
				for i in j:
					if i["profile_name"] == profile_name:
						f = {
						"profile_name":i["profile_name"],
						"name":i["name"],
						"email":i["email"],
						"phone":i["phone"],
						"eTime":time,
						"awbill":awbill,
						"package":package,
						"date":date,
						"add1":i["add1"],
						"add2":i["add2"],
						"postcode":i["postcode"],
						"city":i["city"],
						"state":i["state"]
						}
			if f:
				await message.channel.send(">>> Preview:\n```json\n{}```\nProceed? (y/n)".format(json.dumps(f,indent=4)))
			else:
				await message.channel.send("Profile not found or something went wrong.")
				return
			try:
				confirm = await self.client.wait_for("message",check=check,timeout=100.0)
			except asyncio.TimeoutError:
				await message.channel.send("Timed out.")
				return
			if confirm.content.lower() == "y":
				c,e = Pickup(f).process()
				if (c and (not e)):
					await message.channel.send(">>> Successfully scheduled pickup!\n`{}`".format(c))
				else:
					await message.channel.send(">>> Failed to schedule.\n`Error: {}`".format(e))
			else:
				await message.channel.send("> Cancelled.")

def setup(client):
	client.add_cog(dhl_bot(client))

