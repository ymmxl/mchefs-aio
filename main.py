import discord,os,json
from discord.ext.commands import Bot
from discord.ext import commands
import config

def main():
	client = commands.Bot(command_prefix=config.BOT_PREFIX)
	@client.command()
	async def load(ctx,extension):
		client.load_extension("cogs.{}".format(extension))

	@client.command()
	async def unload(ctx,extension):
		client.unload_extension("cogs.{}".format(extension))

	@client.command()
	async def reload(ctx, extension):
		client.unload_extension("cogs.{}".format(extension))
		client.load_extension("cogs.{}".format(extension))
		await ctx.channel.send("{} module reloaded.".format(extension))
		print("{} module reloaded.".format(extension))
	if not config.TOKEN:
		config.TOKEN = os.getenv("TOKEN")
	ext = ["cogs.stockx_bot","cogs.goat_bot","cogs.kw_bot"]
	for i in ext:
		try:
			client.load_extension(i)
		except:
			print("{} module failed to load.".format(i))
	client.run(config.TOKEN)


if __name__ == "__main__":
	main()

