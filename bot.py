import os
from pathlib import Path
import logging, glob
from telethon import TelegramClient
from Config import Config

logging.basicConfig(level=logging.INFO)


client = TelegramClient(
     'ForceSubscribe',
      api_id = Config.APP_ID,
      api_hash = Config.API_HASH,
)
async def start_bot()
    app = await client.start(bot_token=Config.BOT_TOKEN)

path = "plugins/*.py"
files = glob.glob(path)
for name in files:
    with open(name) as f:
        path1 = Path(f.name)
        shortname = path1.stem
        load_module(shortname.replace(".py", ""))

try:
    bot.loop.run_until_complete(start_bot(Config.BOT_TOKEN))
except Exception as e:
    print("Some Errors")
    print(e)
app.run()
