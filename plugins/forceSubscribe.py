import time
import logging
from Config import Config
from pyrogram import Client, filters
from sql_helpers import forceSubscribe_sql as sql
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)


@Client.on(events.callbackquery.CallbackQuery(data="onUnMuteRequest"))
async def _onUnMuteRequest(client, cb):
  user_id = cb.sender_id
  chat_id = cb.chat_id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    channel = chat_db.channel
    chat_member = await client(functions.channels.GetParticipantRequest(channel=chat_id, user_id=user_id))
    ok = (await client(functions.channels.GetParticipantRequest(channel=chat_id, user_id=user_id))).participant    
    if ok.kicked_by:
      if ok.kicked_by == (client.get_me()).id:
          try:
            await client(functions.channels.GetParticipantRequest(channel=chat_id, user_id=user_id))
            await client.(EditBannedRequest(event.chat_id, user_id, UNBAN_RIGHTS))
            if cb.reply_to_msg_id == user_id:
              cb.delete()
          except UserNotParticipant:
            client.answer("❗ Join the 'channel' and press the 'UnMute Me' button again.", alert=True)
      else:
        client.answer("❗ You are muted by admins for other reasons.", alert=True)
    else:
      chat = await cb.get_chat()
      admin = chat.admin_rights
      noob = await client.get_entity(user_id)
      namenoob = noob.first_name
      if not admin:
        await client.send_message(chat_id, f"❗ **[{namenoob}](tg://user?id={user_id}) is trying to UnMute himself but i can't unmute him because i am not an admin in this chat add me as admin again.**\n__#Leaving this chat...__")
        await client(LeaveChannelRequest(chat_id))
      else:
        await client.answer("❗ Warning: Don't click the button if you can speak freely.", alert=True)



@client.on(events.NewMessage)
@client.on(events.ChatAction)
@client.on(events.MessageEdited)
@client.on(events.MessageDeleted)
def _check_member(client, message):
  chat_id = message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    user_id = message.sender_id
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator and not user_id in Config.SUDO_USERS:
      channel = chat_db.channel
      try:
        await client(functions.channels.GetParticipantRequest(channel=chat_id, user_id=user_id)
      except UserNotParticipant:
        try:
          sent_message = message.reply(
              "{}, you are **not subscribed** to my [channel](https://t.me/{}) yet. Please [join](https://t.me/{}) and **press the button below** to unmute yourself.".format(message.from_user.mention, channel, channel),
              buttons=[
                [custom.Button.inline("Unmute Me", data="onUnMuteRequest")],],
          )
          await client(EditBannedRequest(event.chat_id, user_id, UNBAN_RIGHTS))
        except ChatAdminRequired:
          sent_message.edit("❗ **I am not an admin here.**\n__Make me admin with ban user permission and add me again.\n#Leaving this chat...__")
          await client(LeaveChannelRequest(chat_id))
      except ChatAdminRequired:
        client.send_message(chat_id, text=f"❗ **I am not an admin in @{channel}**\n__Make me admin in the channel and add me again.\n#Leaving this chat...__")
        await client(LeaveChannelRequest(chat_id))


@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status is "creator" or user.user.id in Config.SUDO_USERS:
    chat_id = message.chat.id
    if len(message.command) > 1:
      input_str = message.command[1]
      input_str = input_str.replace("@", "")
      if input_str.lower() in ("off", "no", "disable"):
        sql.disapprove(chat_id)
        message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
      elif input_str.lower() in ('clear'):
        sent_message = message.reply_text('**Unmuting all members who are muted by me...**')
        try:
          for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
            if chat_member.restricted_by.id == (client.get_me()).id:
                client.unban_chat_member(chat_id, chat_member.user.id)
                time.sleep(1)
          sent_message.edit('✅ **UnMuted all members who are muted by me.**')
        except ChatAdminRequired:
          sent_message.edit('❗ **I am not an admin in this chat.**\n__I can\'t unmute members because i am not an admin in this chat make me admin with ban user permission.__')
      else:
        try:
          client.get_chat_member(input_str, "me")
          sql.add_channel(chat_id, input_str)
          message.reply_text(f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{input_str}) in order to send messages in this group.__", disable_web_page_preview=True)
        except UserNotParticipant:
          message.reply_text(f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). Add me as a admin in order to enable ForceSubscribe.__", disable_web_page_preview=True)
        except (UsernameNotOccupied, PeerIdInvalid):
          message.reply_text(f"❗ **Invalid Channel Username.**")
        except Exception as err:
          message.reply_text(f"❗ **ERROR:** ```{err}```")
    else:
      if sql.fs_settings(chat_id):
        message.reply_text(f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__", disable_web_page_preview=True)
      else:
        message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
  else:
      message.reply_text("❗ **Group Creator Required**\n__You have to be the group creator to do that.__")
