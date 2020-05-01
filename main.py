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
	for f in os.listdir("./cogs"):
		try:
			if f.endswith(.py):
				#loads extension according to filenames sliced ".py"
				client.load_extension("cogs.{}".format(f[:-3]))
		except:
			print("{} module failed to load.".format(f))
	client.run(config.TOKEN)


if __name__ == "__main__":
	main()

