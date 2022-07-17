"""
A program to monitor ticket reselling websites for new tickets that go live.
"""

import os
import sys
import time
import discord
import requests


# As check is called in a loop,
# this variable keeps track of how
# many tickets there were last
# time around.
TICKETS: dict = {'responseData': []}


def alert_discord(discord_id: str, discord_token: str):
    """ Function uses the discord api (discord.py) to send a DM to a user """

    # Hack-y thing to avoid using the async loop
    class Client(discord.Client):
        async def on_ready(self):
            client.fetch_user(discord_id).send("website")
            await self.close()

    client = Client()
    client.run(discord_token)


def check_twicket(event_id: str) -> bool:
    """
        Return True if something changed on the website since last time.


        **Known bug:**
            The bot will ignore cases when between two requests >2 tickets go down, but fewer go up.
            In other words if the number of tickets is less than last request, it wont care if they
            are different or not. I don't really think the likelyhood of this happening warrents 
            spending time to fix it.
    """
    api_url = f"https://www.twickets.live/services/g2/inventory/listings/{event_id}?api_key=83d6ec0c-54bb-4da3-b2a1-f3cb47b984f1"

    last_round = globals()['TICKETS']

    try:
        data = requests.get(url=api_url).json()
        globals()['TICKETS'] = data
    except Exception as err: #pylint: disable=broad-except
        print(f"Ignoring error: {err}", file=sys.stderr)
        return False

    # If there are no tickets available
    if len(data['responseData']) == 0:
        return False

    # If this is not the first time the function is called
    if last_round['responseData'] != 0:
        if len(data['responseData']) > len(last_round['responseData']):
            last_round = data
            return True


    # Nothing changed or fewer tickets
    return False






def main():
    if len(sys.argv) != 6:
        print("I don't think you gave the correct number of argumnets")
        print("Usage: ")
        print("\t ticket-finder twicket <event_id> <api_key> discord <discord_id> <discord_token>")
        sys.exit(-1)


    if sys.argv[1] != "twicket":
        print("Have not implemented anything for this website yet :/")
        print("Feel free to PR me.")
        sys.exit(-2)


    if sys.argv[3] != "discord":
        print("Have not implemented any other way to notify you yet :/")
        print("Feel free to PR me.")
        sys.exit(-2)


    # Start pytermgui UI
    # ui()

    while True:
        found: bool = check_twicket(sys.argv[2])
        print(f"{found}: {TICKETS['responseData']}")
        if found:
            os.system("firefox https://www.twickets.live/event/1535073546361905152")
        time.sleep(1)



if __name__ == "__main__":
    main()
