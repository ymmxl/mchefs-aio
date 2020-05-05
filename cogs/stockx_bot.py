import json, os, discord, requests,pytz
from datetime import datetime as dt
from discord.ext import commands
import config
class stockx_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.base_url = "https://stockx.com/"
		self.api_url = "https://xw7sbct9v6-dsn.algolia.net/1/indexes/products/query"
	@commands.Cog.listener()
	async def on_ready(self):
		print("{} StockX module logged in!".format(self.client.user.name))
	@commands.command(pass_context=True)
	async def stockx(self,message,*,kw:str):
		s = requests.session()
		s.headers.update(
		{
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
		"upgrade-insecure-requests": "1",
		"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
		"sec-fetch-mode": "navigate",
		"sec-fetch-site": "none"
		})

		payload = {
			"x-algolia-agent": "Algolia for vanilla JavaScript 3.27.1",
			"x-algolia-api-key": "6bfb5abee4dcd8cea8f0ca1ca085c2b3",
			"x-algolia-application-id": "XW7SBCT9V6"
		}

		json_payload = {
			"params": "query={}&hitsPerPage=1".format(kw)
		}
		r = s.post(url=self.api_url, params=payload, json=json_payload)
		output = json.loads(r.text)

		product_name = ""
		thumbnail_url = ""
		product_url = ""
		object_id = ""
		release_date = ""
		sku = ""
		highest_bid = ""
		lowest_ask = ""
		last_sale = ""
		retail_price = ""
		try:
			product_name = output["hits"][0]["name"]
			thumbnail_url = output["hits"][0]["thumbnail_url"]
			object_id = output["hits"][0]["objectID"]
			product_url = self.base_url + output["hits"][0]["url"]
			release_date = output["hits"][0]["release_date"]
			sku = output["hits"][0]["style_id"]
			highest_bid = output["hits"][0]["highest_bid"]
			lowest_ask = output["hits"][0]["lowest_ask"]
			last_sale = output["hits"][0]["last_sale"]
			retail_price = output["hits"][0]["searchable_traits"]["Retail Price"]
		except KeyError:
			pass
		except IndexError:
			await message.channel.send("Error fetching data from the API or product not loaded. Please try on another product.")
			raise
		
		product_page_url = "https://stockx.com/api/products/{}?includes=market&currency=USD".format(object_id)
		r = s.get(url=product_page_url)
		t = json.loads(r.text)
		available_sizes = []
		lowest_ask_size = t["Product"]["market"]["lowestAskSize"]
		highest_bid_size = t["Product"]["market"]["highestBidSize"]
		try:
			for i,j in t["Product"]["children"].items():
				size = str(j.get("shoeSize","-"))
				if not size:
					size = "-"
				this = "Lowest Ask: ${}\nHighest Bid: ${}\nLast Sale: ${}".format(str(j["market"].get("lowestAsk","-")),str(j["market"].get("highestBid","-")),str(j["market"].get("lastSale","-")))
				available_sizes.append({size:this})
		except AttributeError:
			pass

		####EMBEDS IF FOOTER IS TOO LONG IT WILL MESS UP
		####THE WHOLE FORMATTING OF THE EMBED. REMEMBER
		d=dt.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		embed = discord.Embed(color=4500277)
		embed.set_thumbnail(url=thumbnail_url)
		embed.add_field(name="Product Name", value="[{}]({})".format(product_name, product_url), inline=False)
		embed.add_field(name="SKU", value = "{}".format(sku), inline=True)
		embed.add_field(name="Release Date", value="{}".format(release_date), inline=True)
		embed.add_field(name="Retail Price", value="${}".format(retail_price), inline=True)
		embed.add_field(name="Last Sale", value="${}".format(last_sale), inline=True)
		embed.add_field(name="Lowest Ask", value="${}, Size: {}".format(lowest_ask,lowest_ask_size), inline=True)
		embed.add_field(name="Highest Bid", value="${}, Size: {}".format(highest_bid,highest_bid_size), inline=True)
		#up to here is 7 fields. max is 25 fields
		i = 7
		embed2 = discord.Embed(color=4500277)
		for i in available_sizes:
			for j,k in i.items():
				if len(embed.fields) > 25:
					embed2.add_field(name=j if j else "All", value=k, inline=True)
				else:
					embed.add_field(name=j if j else "All", value=k, inline=True)
		
		if len(embed2)!=0:		
			embed2.set_footer(text="ymmxl StockX Bot v{} [{}]".format(config.BOT_VERSION,d),icon_url=config.ICON_URL)
		else:
			embed.set_footer(text="ymmxl StockX Bot v{} [{}]".format(config.BOT_VERSION,d),icon_url=config.ICON_URL)
		await message.channel.send(embed=embed)
		if len(embed2) != 0:
			await message.channel.send(embed=embed2)

def setup(client):
	client.add_cog(stockx_bot(client))