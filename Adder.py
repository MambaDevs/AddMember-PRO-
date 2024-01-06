#!/bin/env python3
import csv, logging, os, random, sys, time, asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError
import configparser

logging.basicConfig(level=logging.INFO)

async def authenticate_user(client, phone):
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        os.system('clear')
        banner()
        await client.sign_in(phone, input("[+] Enter the code: "))

async def get_user_input_entity(client, username):
    if username == "":
        return None
    return await client.get_input_entity(username)

async def add_member_to_group(client, target_group_entity, user_to_add):
    try:
        await client(InviteToChannelRequest(target_group_entity, [user_to_add]))
        logging.info("[+] Waiting for 5-10 Seconds...")
        await asyncio.sleep(random.randrange(5, 10))
    except PeerFloodError:
        logging.error("[!] Getting Flood Error from telegram. \n[!] Script is stopping now. \n[!] Please try again after some time.")
    except UserPrivacyRestrictedError:
        logging.error("[!] The user's privacy settings do not allow you to do this. Skipping.")
    except Exception as e:
        logging.error("[!] Unexpected Error: {}".format(e))

async def main():
    banner()
    
    cpass = configparser.RawConfigParser()
    cpass.read('config.data')

    try:
        api_id = cpass['cred']['id']
        api_hash = cpass['cred']['hash']
        phone = cpass['cred']['phone']
        client = TelegramClient(phone, api_id, api_hash)
        await client.start()

        await authenticate_user(client, phone)

        input_file = sys.argv[1]
        users = []

        with open(input_file, encoding='UTF-8') as f:
            rows = csv.reader(f, delimiter=",", lineterminator="\n")
            next(rows, None)
            for row in rows:
                user = {
                    'username': row[0],
                    'id': int(row[1]),
                    'access_hash': int(row[2]),
                    'name': row[3]
                }
                users.append(user)

        chats = []
        last_date = None
        chunk_size = 200
        groups = []

        result = await client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup:
                    groups.append(chat)
            except:
                continue

        i = 0
        for idx, group in enumerate(groups):
            print(f'[{idx}] - {group.title}')
            i += 1

        print('[+] Choose a group to add members')
        g_index = input("[+] Enter a Number: ")
        target_group = groups[int(g_index)]
        target_group_entity = InputPeerChannel(target_group.id, target_group.access_hash)

        print("[1] add member by user ID\n[2] add member by username ")
        mode = int(input("Input: "))
        n = 0

        for user in users:
            n += 1
            if n % 50 == 0:
                await asyncio.sleep(1)

            logging.info(f"Adding {user['id']}")
            if mode == 1:
                user_to_add = await get_user_input_entity(client, user['username'])
            elif mode == 2:
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                sys.exit("[!] Invalid Mode Selected. Please Try Again.")

            if user_to_add:
                await add_member_to_group(client, target_group_entity, user_to_add)

if __name__ == '__main__':
    asyncio.run(main())

