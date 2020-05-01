import json, os, discord, requests, pytz
from datetime import datetime as dt
from discord.ext import commands


class fee_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
	@commands.Cog.listener()
	async def on_ready(self):
		print('{} Fee module logged in!'.format(self.client.user.name))

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

def setup(client):
	client.add_cog(fee_bot(client))