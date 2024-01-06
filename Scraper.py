import csv, logging, asyncio ,configparser ,sys
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from colorama import Fore, Style

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
PHONE = 'your_phone_number'
CONFIG_FILE = 'config.data'
CSV_FILE = 'members.csv'

class Contact:
    def __init__(self, user):
        self.username = user.username if user.username else ""
        self.id = user.id
        self.access_hash = user.access_hash
        self.name = (user.first_name + ' ' + user.last_name).strip() if user.first_name else ""
        self.group_title = ""
        self.group_id = 0

    async def initialize_client():
      try:
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE)
        api_id = config['cred']['id']
        api_hash = config['cred']['hash']
        phone = config['cred']['phone']
        return await TelegramClient(phone, api_id, api_hash).start()
      except KeyError:
        logger.error(f"{Fore.RED}[!] Run python3 main.py first !!{Style.RESET_ALL}")
        sys.exit(1)

    async def authorize_client(client, phone):
      if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input(f'{Fore.GREEN}[+] Enter the code: {Style.RESET_ALL}'))

    async def get_groups(client):
        result = await client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200))
        return [chat for chat in result.chats if getattr(chat, 'megagroup', False)]

    async def save_members_to_csv(all_participants, target_group):
      with open(CSV_FILE, "w", encoding='UTF-8', newline='') as f:
        writer = csv.writer(f, delimiter=",", lineterminator="\n")
        writer.writerow([f"{Fore.CYAN}username", "user id", "access hash", "name", "group", "group id{Style.RESET_ALL}"])
        for user in all_participants:
            contact = Contact(user)
            contact.group_title = target_group.title
            contact.group_id = target_group.id
            writer.writerow([f"{Fore.YELLOW}{contact.username}", f"{Fore.GREEN}{contact.id}", f"{Fore.BLUE}{contact.access_hash}",
                             f"{Fore.WHITE}{contact.name}", f"{Fore.MAGENTA}{contact.group_title}", f"{Fore.RED}{contact.group_id}{Style.RESET_ALL}"])

async def main():
      logging.info(f"{Fore.BLUE}[+] Initializing...{Style.RESET_ALL}")
      client= await Contact.initialize_client()
      await client.connect()
      await Contact.authorize_client(client, PHONE)
      logging.info(f"{Fore.YELLOW}[+] Fetching Groups...{Style.RESET_ALL}")
      groups = await Contact.get_groups(client)
      logging.info(f"{Fore.GREEN}[+] Choose a group to scrape members:{Style.RESET_ALL}")
      for i, group in enumerate(groups):
        logging.info(f"[{Fore.CYAN}{i}{Style.RESET_ALL}] - {Fore.MAGENTA}{group.title}{Style.RESET_ALL}")
      logging.info("")
      group_index = int(input(f"{Fore.GREEN}[+] Enter a Number: {Style.RESET_ALL}"))
      target_group = groups[group_index]
      logging.info(f"{Fore.YELLOW}[+] Fetching Members...{Style.RESET_ALL}")
      all_participants = await client.get_participants(target_group, aggressive=True)
      logging.info(f"{Fore.BLUE}[+] Saving In file...{Style.RESET_ALL}")
      await Contact.save_members_to_csv(all_participants, target_group)
      logging.info(f"{Fore.GREEN}[+] Members Scraped Successfully.{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())

