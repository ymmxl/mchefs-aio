import json, os, discord, requests, pytz,asyncio,typing,time
from datetime import datetime as dt
import datetime
from discord.ext import commands
#from utils.ftl_order import Order

class utility_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
	@commands.Cog.listener()
	async def on_ready(self):
		print('{} Utility module logged in!'.format(self.client.user.name))

	@commands.command(pass_context=True)
	async def fee(self,message,*,kw:typing.Union[int,float]):
		#if not isinstance(message.channel, discord.DMChannel) or (message.channel.id != "554705872945938432"):
		#if (not isinstance(message.channel, discord.DMChannel)):
			#await message.channel.send("SBSS keke")
		if (message.channel.id == 554705872945938432) or (isinstance(message.channel, discord.DMChannel)):
			try:
				lvl1 = round(kw-((9.5/100)*kw)-((3/100)*kw)-30,2)
				lvl2 = round(kw-((9.0/100)*kw)-((3/100)*kw)-30,2)
				lvl3 = round(kw-((8.5/100)*kw)-((3/100)*kw)-30,2)
				lvl4 = round(kw-((8/100)*kw)-((3/100)*kw)-30,2)
				goat = round(kw-(9.5/100*kw)-30,2)
				embed = discord.Embed(title="Fee Calculator",color=3092790)
				embed.add_field(name = "StockX Level 1",value="${}".format(str(lvl1)),inline=False)
				embed.add_field(name = "StockX Level 2",value="${}".format(str(lvl2)),inline=False)
				embed.add_field(name = "StockX Level 3",value="${}".format(str(lvl3)),inline=False)
				embed.add_field(name = "StockX Level 4",value="${}".format(str(lvl4)),inline=False)
				embed.add_field(name = "Goat",value="${}".format(str(goat)),inline=False)
				await message.channel.send(embed=embed)
			except Exception as e:
				print("Error--------------")
				print(e)
		else:
			await message.channel.send("Please use the commands channel only.",delete_after=3)
			await message.message.delete(delay=3)
	@commands.command(pass_context=True)
	async def update(self,message,*,kw:str):
		if message.author.id != 329298525752131585:
			await message.channel.send("This command is only for @Cracked :)")
		else:
			channel = message.channel

			def check(m):
				return m.author == message.author and  m.channel == channel

			await message.channel.send("Updating {}. Details? (seperate with \\\), `cancel` to cancel.".format(kw))
			try:
				updates = await self.client.wait_for("message",check=check,timeout=200.0)
			except asyncio.TimeoutError:
				await message.channel.send("Timed out.")
				return
			if updates.content == "cancel":
				await message.channel.send("cancelled.")
				return
			u = updates.content.split("\\")
			##EMBED##
			date=dt.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore")).strftime("%H:%M:%S")
			d = "**{}**\n".format(kw.upper())
			for i in u:
				d+="`-{}`\n".format(i)
			d+="\n`Thank you for your continuous support.`\n"
			embed = discord.Embed(title="New Monitor Update!",description=d,color=16711680)
			embed.set_footer(text="Update Bot v1.0 | @Cracked [{}]".format(date))
			##EMBED##
			await message.channel.send("Preview:",embed=embed)
			await message.channel.send("Thank you. Proceed?")
			proceed = await self.client.wait_for("message",check=check)
			if proceed.content == "y":
				#c = self.client.get_channel(373407301006000130) test channel
				c = self.client.get_channel(427497512698380288)
				await c.send(embed=embed)
				await message.channel.send("Updates posted successfully.")
			else:
				await message.channel.send("Aborted.")

	@commands.command(pass_context=True)
	async def ftl(self,message,*,kw:str):
		def check(m):
			return m.author == message.author and  m.channel == channel		
		args = kw.split(",")
		#!ftl_orders au,today
		region = args[0].upper()
		try:
			if args[1].lower() == "today":
				date=dt.today().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore"))
			elif dt.strptime(args[1],"%Y-%m-%d"):
				date = dt.strptime(args[1],"%Y-%m-%d")
			else:
				date = None
		except Exception as e:
			print("Error parsing date: {}".format(e))
			date = None
		day2 = date + datetime.timedelta(days=1)
		day1 = date - datetime.timedelta(days=1)
		c = self.client.get_channel(803880916279230484)
		message_list = await c.history(before=day2,after=day1,limit=100).flatten()
		# for i in message_list:
		# 	if i.embeds:
		# 		for t in i.embeds:
		# 			print(t.to_dict())
		master = []
		for i in message_list:
			if i.embeds:
				for t in i.embeds:
					if "QBot FTL{}".format(region) in t["footer"]["text"]:
						if t["title"] == "Successfully Checked Out":
						#print(t.to_dict())
							for k in t["fields"]:
								if k["name"] == "Order:":
									master.append(k["value"].replace("|",""))
		await message.channel.send("Found {} {} orders on {}.".format(str(len(master)),region,date.strftime("%Y-%m-%d")))
		order_list = Order(master).process()
		for i in order_list:
			#if not error
			if not i[0]:
				#ifshipped
				if i[1]:
					items=i[2]
					embed = discord.Embed(title="FTL Order Shipped!",color=5814783)
					embed.add_field(name=items["name"],value="**Region**:{}\n**Order number**: ||`{}`||\n**size**: `{}`".format(args[0].upper(),items["order_number"],items["sku"][-3:]))	
					embed.add_field(name="Tracking URL",value="**STATUS**: `{}`\n[{}]({})".format(items["tracking_status"],items["carrier"],items["tracking"]))
					embed.set_thumbnail(url=items["image"])
					embed.set_footer(text="cracked#7701 powered by Apple M1")
					await message.channel.send(embed=embed)
			time.sleep(0.5)
	# @commands.command(pass_context=True)
	# async def ftl(self,message,*,kw:str):
# # 	def format_stock(self,stock):
# # 		soup = bs(stock,"html.parser")
# # 		t = soup.find(attrs={"data-product-variation-info":self.sku}).attrs["data-product-variation-info-json"]
		

# # https://images.footlocker.com/is/image/FLEU/315345189302?wid=86&hei=86
# # https://images.footlocker.com/is/image/FLEU/314102477404?wid=763&hei=538&fmt=png-alpha

# 		if message.author.id != 329298525752131585:
# 			await message.channel.send("This command is only for @Cracked :)")
# 		if (message.channel.id == 554705872945938432) or (isinstance(message.channel, discord.DMChannel)):
# 			try:

# 			except Exception as e:
# 				print("Error--------------")
# 				print(e)
# 		else:
# 			await message.channel.send("Please use the commands channel only.",delete_after=3)
# 			await message.message.delete(delay=3)


	# @commands.command(pass_context=True)
	# async def purge(self,message,amount = 1):
	# 	if not message.channel.type is discord.ChannelType.private:
	# 		return
	# 	else:
	# 		#await message.delete()
	# 		async for msg in message.channel.history(limit=amount):
	# 			await msg.delete()
	# 		#await message.purge(limit = amount)

def setup(client):
	client.add_cog(utility_bot(client))