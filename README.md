A program to monitor ticket re-selling websites
===============================================

On some concerts re-sale tickets get sold even before the email notification can arrive. I don't know how people do that, but I hope this bot helps.

The goal of the bot is to monitor for new tickets on *some* popular ticket re-sale websites and quickly alert you if there is a new one. Currently I'm hoping to do that via discord notification as that is instant, but might add something else in the future.


#### Disclaimer
Please do not use this bot if you are only buying the ticket to re-sell it for a higher price somewhere else.



## Usage

**Note -1**: Until I finish the `setup.py` program just run `pip install discord`, then `./ticket-finder/__init__.py` :/



For the twicket.live website:
```
ticket-finder twicket <event_id> discord <discord_id> <discord_token>
```

**Note:** The `event_id` of a concert can be found at the end of the URL.

**Note 1:** Your `discord_id` can be found by right clicking on your name in any chat. Its usually around 18 decimal numbers.

**Note 2:** You can get a `discord_token` by visiting the discord dev portal and making a bot.

**Note 4:** The `twicket` and `discord` keywords are just there in-case I add options in the future.



## Plans

I mostly develop this bot when I need it, but in the future I plan to add other websites (if they have good concerts) and possibly a better way of notifying you than discord.
