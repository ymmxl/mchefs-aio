import json,os,discord,requests,pytz,sys
from datetime import datetime as dt
from discord.ext import commands, tasks
from decimal import *
import config
class novel_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.api_url = "https://novelship.com/api/products/PRODUCT_ID/offer-lists?where[active:eq]=true&page[number]=0&page[size]=1000"
		self.search_url = "https://novelship.com/api/products/search?where[search]=KEYWORD&where[active:eq]=true&page[number]=0&page[size]=1"
		self.rate = None
		self.rate = 3
	@commands.Cog.listener()
	async def on_ready(self):
		#TASKS LOOP CANNOT BE PROMPTED AFTER !RELOAD COMMAND#
		#self.get_rates.start()
		print("{} Novelship module logged in!".format(self.client.user.name))
	# @tasks.loop(hours=12)
	# async def get_rates(self):
	# 	h = {
	# 	"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
	# 	"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	# 	"accept-encoding":"gzip, deflate, br",
	# 	"accept-language":"en-GB,en-US;q=0.9,en;q=0.8",
	# 	"if-none-match":"""W/"27-ZQCF16t6JNv+dx6atp1EapVHMD4\""""
	# 	}
	# 	r = requests.get("https://free.currconv.com/api/v7/convert?q=SGD_MYR&compact=ultra&apiKey=469f69ca5e89bfc25989",headers=h)
	# 	if r.status_code != 200:
	# 		print("Failed to get currency rates: STATUS[{}]".format(r.status_code))
	# 	elif r.json().get("SGD_MYR"):
	# 		self.rate = r["SGD_MYR"]
	# 	else:
	# 		self.rate = 3
	@commands.command()
	async def r(self,message):
		await message.channel.send("{}".format(str(self.rate)))
	@commands.command(pass_context=True)
	async def novel(self,message,*,kw:str):
		r = requests.get(self.search_url.replace("KEYWORD",kw),timeout=10).json()
		if r["total"] == 0:
			print("No products found")
			await message.channel.send("No products found or not loaded yet.")
		for i in r["results"]:
			product_id = i.get("id")
			product_name = i.get("name")
			product_url = "https://novelship.com/{}".format(i.get("name_slug"))
			thumbnail_url = i.get("gallery")[0]
			release_date = i.get("drop_date","-")
			if release_date != ("-" and None):
				release_date=release_date.split("T")[0]
			retail_price = i.get("cost","-")
			highest_bid_id = i.get("highest_offer_id")
			lowest_ask_id = i.get("lowest_listing_id")
			sku = i.get("sku","-")
			if sku:
				if sku != "-":
					sku.replace(" ","-")
			else:
				sku = "-"
			size_list = i.get("sizes")

		res = requests.get(self.api_url.replace("PRODUCT_ID",str(product_id)),timeout=10).json()
		if res["total"] == 0:
			print("No bids.")

		if not self.rate:
			try:
				for i in res["results"]:
					if i["local_currency_id"] == 3:
						self.rate = i["currency"]["rate"]
						break
					else:
						self.rate = 3
			except KeyError:
				pass		

		for i in res["results"]:
			if i["local_currency_id"] == 1:
				i["local_price"] = round(i["local_price"]*self.rate)
		if highest_bid_id:
			highest_bid = [i for i in res["results"] if i["id"] == highest_bid_id]
			highest_bid_price = highest_bid[0]["local_price"]
			highest_bid_size = highest_bid[0]["size"]
		else:
			highest_bid_price = "-"
			highest_bid_size = "-"
		if lowest_ask_id:
			#print(lowest_ask_id)
			lowest_ask = [i for i in res["results"] if i["id"] == lowest_ask_id]
			lowest_ask_price = lowest_ask[0]["local_price"]
			lowest_ask_size = lowest_ask[0]["size"]
		else:
			lowest_ask_price = "-"
			lowest_ask_size = "-"
		#res["results"].sort(key=lambda k:(k["type"],Decimal(re.search(r"(\d+\.*\d*)",k["size"]).group())))

		available_sizes=[]
		#filtering size following size_list and getting max value
		for i in size_list:
			q = list(filter(lambda k:(k["size"]==i),res["results"]))
			if len(q) == 0:
				#print(i," Buying: 0, Selling: 0")
				this = "L.Ask: RM -\nH.Bid: RM -"	
			else:
				b = max((j.get("local_price") for j in q if j.get("type") == "buying"),default="-")
				s = min((j.get("local_price") for j in q if j.get("type") == "selling"),default ="-")
				#print(i," | buying: {}, selling: {}".format(b,s))
				this = "L.Ask: RM {}\nH.Bid: RM {}".format(s,b)
			available_sizes.append({i:this})
		d=dt.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		embed = discord.Embed(color=16772304)
		embed.set_thumbnail(url=thumbnail_url)
		embed.add_field(name="Product Name", value="[{}]({})".format(product_name, product_url), inline=False)
		embed.add_field(name="SKU", value = "{}".format(sku), inline=True)
		embed.add_field(name="Release Date", value="{}".format(release_date), inline=True)
		embed.add_field(name="Retail Price", value="${}".format(retail_price) if retail_price else "None", inline=True)
		embed.add_field(name="Lowest Ask", value="RM {}, Size: {}".format(lowest_ask_price,lowest_ask_size), inline=True)
		embed.add_field(name="Highest Bid", value="RM {}, Size: {}".format(highest_bid_price,highest_bid_size), inline=True)
		embed.add_field(name="\u200b",value="\u200b")
		for i in available_sizes:
			for j,k in i.items():
				embed.add_field(name=j,value=k,inline=True)
		embed.set_footer(text="ymmxl Novelship Bot v1.2 [{}]".format(d))
		await message.channel.send(embed=embed)
def setup(client):
	client.add_cog(novel_bot(client))