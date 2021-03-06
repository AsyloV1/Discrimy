import sys

if sys.version_info < (3, 4):
	raise Exception("You must be running Python 3.5 or above!")

import pip
import asyncio
import urllib.request
import shutil
import os
import sqlite3

if not os.name == 'nt':
	raise Exception("You must be running Windows!")

if os.path.isfile("temp.py"):
	os.remove("temp.py")

try:
	shutil.copyfile("config.ini", "temp.py")
	from temp import *
	os.remove("temp.py")
except:
	raise Exception("[ERROR] Config load error. Probably missing, broken or in a directory with no write permissions.")
	
def GrabToken(IsCanary):
	if IsCanary:
		shutil.copy(os.getenv('APPDATA') + '\discordcanary\Local Storage\https_canary.discordapp.com_0.localstorage', 'localstorage.db')
	else:
		shutil.copy(os.getenv('APPDATA') + '\discord\Local Storage\https_discordapp.com_0.localstorage', 'localstorage.db')
	db = sqlite3.connect('localstorage.db')
	cursor = db.cursor()
	cursor.execute("SELECT * FROM ItemTable WHERE key = 'token'")
	token = str(cursor.fetchone()[1]).lstrip("b'").rstrip("'").replace(r'\x00','').lstrip('"').rstrip('"')
	db.close()
	os.remove("localstorage.db")
	return token

if not os.path.isfile("discrimlist.ini"):
	raise Exception("[ERROR] Can't find the discriminator list.")

if discordpass == "":
	raise Exception("[ERROR] Config not edited.")

def install(package):
	pip.main(['install', package])

import logging
try:
	import discord
except:
	install("discord.py")
	raise Exception("Discord recently installed. Rerun this application.")

print("[INFO] Signing into Discord. This may take a while.")
logging.basicConfig(level=logging.ERROR)
client = discord.Client()

@client.event
async def on_ready():
	OriginalName = client.user.name
	print("\n------------------")
	try:
		print('Logged in as ' + OriginalName)
	except:
		print('Logged in but cannot display the username due to a encoding error.')
	print('ID: ' + client.user.id)
	print("------------------\n")
	MemberCount = 0
	ServerCount = 0
	UserList = []
	for server in client.servers:
		ServerCount = ServerCount + 1
		try:
			print("[SERVER] " + str(server.name))
		except:
			print("[SERVER] Name failed to load!")
		for member in server.members:
			MemberCount = MemberCount + 1
			UserList.append(member)
	if ServerCount == 1:
		print("[MEMBERS] There are approximately " + str(MemberCount) + " members in the 1 server you are in!")
		if MemberCount > 30000:
			print("[INFO] You are only in one server, but that server appears to have over 30,000 users. You should be fine, but if you encounter issues, join another big server.") 
	else:
		print("[MEMBERS] There are approximately " + str(MemberCount) + " members in the " + str(ServerCount) +  " servers you are in!")
	if MemberCount < 30000:
		print("[WARNING] There are under 30,000 members in the combined servers you are in. This may cause issues with the discriminator editing process. We recommend joining a few big guilds such as the Discord API server.")
	print("\n------------------\n")
	while True:
		discrimlist = []
		with open("discrimlist.ini") as d:
			discrimlist = d.readlines()
		discrimlist = [l.strip() for l in discrimlist]
		ndl = []
		for discrim in discrimlist:
			discrimsplit = list(discrim)
			nds = []
			charlength = 0
			for char in discrimsplit:
				charlength = charlength + 1
				if char == "*":
					char = client.user.discriminator[charlength - 1]
				if char == "%":
					char = client.user.discriminator[0]
				nds.append(char)
			ndl.append(''.join(nds))
		discrimlist = ndl
		AlreadyGotDiscrim = False
		for discrim in discrimlist:
			if discrim == client.user.discriminator:
				AlreadyGotDiscrim = True
		if not AlreadyGotDiscrim:
			FoundNickname = False
			DiscrimName = ""
			OldDiscrim = client.user.discriminator
			for user in UserList:
				if FoundNickname == False:
					if not client.user.name == user.name and client.user.discriminator == user.discriminator:
						FoundNickname = True
						DiscrimName = user.name
			if FoundNickname == False:
				print("[ERROR] Farming could not continue because another user could not be found with the same discriminator. Try joining some more big servers.")
			else:
				await client.login(GrabToken(IsCanary), bot=False)
				await client.edit_profile(password=discordpass, username=DiscrimName)
				if ChangeNicknameBack:
					await client.login(GrabToken(IsCanary), bot=False)
					await client.edit_profile(password=discordpass, username=OriginalName)
					print("[INFO] Username changed and then changed back. This has changed your discriminator.")
				else:
					print("[INFO] Username/discriminator changed.")
				await asyncio.sleep(DelayTime)
				if not client.user.discriminator == OldDiscrim:
					print("[INFO] The new discriminator is #" + client.user.discriminator)
				else:
					print("[INFO] Due to a delay between you and the Discord API, your new discriminator will not be displayed.")
		else:
			print("[INFO] You appear to already have a discriminator you want. Farming has stopped.")
		if ChangeNicknameBack:
			await asyncio.sleep(3600 - DelayTime)
		else:
			await asyncio.sleep(1800 - DelayTime)

client.run(GrabToken(IsCanary), bot=False)
