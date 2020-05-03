import json, os, discord, requests, pytz,asyncio
from datetime import datetime as dt
from discord.ext import commands


class utility_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
	@commands.Cog.listener()
	async def on_ready(self):
		print('{} Utility module logged in!'.format(self.client.user.name))

	@commands.command(pass_context=True)
	async def fee(self,message,*,kw:int or float):
		#if not isinstance(message.channel, discord.DMChannel) or (message.channel.id != "554705872945938432"):
		#if (not isinstance(message.channel, discord.DMChannel)):
			#await message.channel.send("SBSS keke")
		if (message.channel.id == 554705872945938432) or (isinstance(message.channel, discord.DMChannel)):
			try:
				lvl1 = kw-(round(9.5/100*kw,2))-round(3/100*kw,2)-30
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


def setup(client):
	client.add_cog(utility_bot(client))