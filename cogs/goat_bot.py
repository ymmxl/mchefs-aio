import json, os, discord, requests, pytz
from datetime import datetime as dt
from discord.ext import commands
import config
class goat_bot(commands.Cog):
	def __init__(self,client):
		self.client = client
		self.api_url = "https://2fwotdvm2o-dsn.algolia.net/1/indexes/ProductTemplateSearch/query"

	@commands.Cog.listener()
	async def on_ready(self):
		print('{} Goat module logged in!'.format(self.client.user.name))

	@commands.command(pass_context=True)
	async def goat(self,message,*,kw:str):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
		}

		params = {
			'x-algolia-agent': 'Algolia for vanilla JavaScript 3.25.1',
			'x-algolia-api-key': 'ac96de6fef0e02bb95d433d8d5c7038a',
			'x-algolia-application-id': '2FWOTDVM2O',
		}

		data = {
			"params": "query={}&facetFilters=(status%3Aactive%2C%20status%3Aactive_edit)%2C%20()&page=0&hitsPerPage=20"
			.format(kw)
		}
		r = requests.post(url=self.api_url, headers=headers, params=params, json=data)
		output = json.loads(r.text)
		image = output['hits'][0]['picture_url']
		name = output['hits'][0]['name']
		new_lowest_price_cents = int(output['hits'][0]['new_lowest_price_cents'] / 100)
		maximum_offer = int(output['hits'][0]['maximum_offer_cents'] / 100)
		minimum_offer = int(output['hits'][0]['minimum_offer_cents'] / 100)
		url = 'https://www.goat.com/sneakers/' + output['hits'][0]['slug']
		used_lowest_price_cents = int(output['hits'][0]['used_lowest_price_cents'] / 100)
		want_count = output['hits'][0]['want_count']
		want_count_three = output['hits'][0]['three_day_rolling_want_count']

		d=dt.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("singapore")).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
		embed = discord.Embed(color=0xedf7f6)
		embed.set_thumbnail(url=image)
		embed.add_field(name="Product Name", value="[{}]({})".format(name, url), inline=False)
		embed.add_field(name="Lowest Bid", value="${}".format(minimum_offer), inline=True)
		embed.add_field(name="Highest Bid", value="${}".format(maximum_offer), inline=True)
		embed.add_field(name="Used Lowest Price", value="${}".format(used_lowest_price_cents), inline=True)
		embed.add_field(name="New Lowest Price", value="${}".format(new_lowest_price_cents), inline=True)
		embed.add_field(name="Want Count in Last 3 Days", value="{}".format(want_count_three), inline=True)
		embed.add_field(name="Total Want Count", value="{}".format(want_count), inline=True)
		embed.set_footer(text="ymmxl Goat Bot v{} [{}]".format(config.BOT_VERSION,d),icon_url=config.ICON_URL)
		await message.channel.send(embed=embed)

def setup(client):
	client.add_cog(goat_bot(client))