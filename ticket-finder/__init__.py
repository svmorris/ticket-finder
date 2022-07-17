"""
A discord bot that monitors ticket re-sale websites and alerts as soon as something is available.
"""

import os
import sys
import time
import json
import asyncio
import sqlite3
import discord
import requests
import threading

TICKETS = {}
DB_PATH = "storage/db.sqlite"
HELP = """**Usage:**:
```
Start watching a website:    !watch <platform> <url>
Show watchlist:              !show
Stop watching a website:     !stop <number>
```
**Example:**
```!watch twickets https://www.twickets.live/event/1535073546361905152```
"""



client = discord.Client()
token = os.getenv('TOKEN')
if token is None:
    print("No token supplied")
    sys.exit(-1)


def debug_log(message: str):
    """ Send a message into the #logs channel """
    print(message)



class Database:
    def __init__(self):

        if os.path.isfile(DB_PATH):
            self.db = sqlite3.connect(DB_PATH)
            self.cursor = self.db.cursor()

        else:
            self.db = sqlite3.connect(DB_PATH)
            self.cursor = self.db.cursor()
            self.cursor.execute("CREATE TABLE tickets (\
                        'owner',\
                        'website',\
                        'api_url',\
                        'human_url'\
                    )")
            self.db.commit()

    def __del__(self ):
        """ Close the Database """
        self.db.close()


    def add_row(self, user: str, website: str, api_url: str, human_url: str):
        """ Add a value to the database """
        self.cursor.execute("INSERT INTO tickets VALUES (?, ?, ?, ?)", (user, website, api_url, human_url))
        self.db.commit()


    def get_all(self) -> list:
        """ Get all tickets from the database """
        self.cursor.execute("SELECT rowid, * FROM tickets")
        return self.cursor.fetchall()


    def delete_row(self, number: int):
        """ Stop monitoring a ticket """
        self.cursor.execute("DELETE FROM tickets WHERE rowid=?", number)
        self.db.commit()



def check_twicket(api_url: str) -> bool:
    """
        Return True if something changed on the website since last time.


        **Known bug:**
            The bot will ignore cases when between two requests >2 tickets go down, but fewer go up.
            In other words if the number of tickets is less than last request, it wont care if they
            are different or not. I don't really think the likelyhood of this happening warrents 
            spending time to fix it.
    """

    last_round = globals()['TICKETS'].get(api_url)


    try:
        data = requests.get(url=api_url).json()
        globals()['TICKETS'][api_url] = data
    except Exception as err: #pylint: disable=broad-except
        print(f"Ignoring error: {err}", file=sys.stderr)
        return False


    # If there are no tickets available
    if len(data['responseData']) == 0:
        return False

    # If this is not the first time the function is called
    if last_round != None:
        if len(data['responseData']) > len(last_round['responseData']):
            last_round = data
            return True


    # Nothing changed or fewer tickets
    return False



def scanner():
    """ Scanner checks every 2 seconds for new tickets """
    while True:
        time.sleep(1)
        thread_db = Database()
        events = thread_db.get_all()

        for event in events:
            found: bool = check_twicket(event[3])
            debug_log(found)

            # If something changed
            if found:
                async def send_message_to_specific_channel(message: str, channel: int):
                    await client.get_channel(channel).send(message)

                asyncio.run_coroutine_threadsafe(send_message_to_specific_channel(
                        f'<@{event[1]}> New ticket at {event[-1]}',
                        998195920514596967,
                    ),client.loop)



@client.event
async def on_message(message) -> str:
    """ Handle messages """
    if message.author == client.user:
        return


    if message.content.startswith("!help"):
        return await message.channel.send(HELP)



    if message.content.startswith("!watch"):
        command = message.content.split()

        if command[1] == "twickets":
            base_url = "https://www.twickets.live/event/"
            if not command[2].startswith(base_url):
                return await message.channel.send("Something is wrong with your URL")

            try:
                event_id = int(command[2].strip().strip("https://www.twickets.live/event/"))
            except ValueError:
                return await message.channel.send("Something is wrong with that URL")

            database.add_row(
                    str(message.author.id),
                    "twickets",
                    f"https://www.twickets.live/services/g2/inventory/listings/{event_id}?api_key=83d6ec0c-54bb-4da3-b2a1-f3cb47b984f1",
                    f"https://www.twickets.live/event/{event_id}",
                )
            return await message.channel.send(f"Started monitoring event: {event_id}!")

        return await message.channel.send("I have not implemented anything for this website yet :/")



    if message.content.startswith("!show"):
        watchlist = database.get_all()
        res = ""
        for event in watchlist:
            res += f"**{event[0]}**: {event[-1]} ({event[1]})\n"

        # If there weren't any on the watchlist to show
        if res == "":
            return await message.channel.send("Nothing to show!")

        return await message.channel.send(res)



    if message.content.startswith("!stop"):
        try:
            event_id = message.content.split()[1]
        except ValueError:
            return await message.channel.send("Not a valid number!")

        database.delete_row(event_id)
        return await message.channel.send(f"Stopped monitoring event: {event_id}!")



if __name__ == "__main__":
    database = Database()

    x = threading.Thread(target=scanner, args=())
    x.start()

    client.run(token)
