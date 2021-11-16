# twitch-leak-bot-discord
A bot to display per user data from the Twitch Leak by username


# Where's the data?

I can't and don't want to supply the .csv's as they are 

 - too big
 - potential blacklisting and punishment from Twitch

The only data supplied is a list of ID's in a .json for who was in the leak.

If you get the CSV's (via your own methods) you can use the script `csv_setup` to set them up to the correct config!


# Setup

## Import and shrink csv files:

* This will import, rename and optionally shrink original gz files into a data folder.
* Original Twitch-payouts folder must be at the root of the project.
* Choose import and shrink or just import.
* Shrinking will delete lines with no revenue, and significantly speed up the parsing process.
* You can also shrink already imported files.
* Once imported you can delete or move the original Twitch-payouts folder

Type in a terminal:

* On linux or macOS:

```Python3 csv_setup.py```

* On Windows:

```Python csv_setup.py```

## Twitch API and discord bot IDs

You need two or three values
 - A discord bot token
 - A twitch client ID [Register an app](https://dev.twitch.tv/console/apps/create)
 - A twitch client secret (only with Helix)

Set them in the `main.py` file

## Database storage

Streamer data will be cached during program execution to avoid researching an already searched user.
If USE_DATABASE set to True (default value), the cache will be stored in a local database file, and recalled when the program is reloaded. 
If set to False, database file will not be used and cache will be lost when the program is closed.

## Creating a Discord Bot

[This article](https://www.startinop.com/gaming/discord-bot/) for detailled instructions (till step 4 included, when you invite the bot.)

The bot needs rights to read messages and see messages history and that's all.
 
## Twitch Client App Registration Settings

Name: Can be anything

OAuth Redirect URLs: `http://localhost/`

Category: `Other`

Other Details: Can be anything

## Twitch API: Helix or Kraken?

If you have registered your app from after July 2021 you are using **helix**

If you are using an app you registered before July 2021 you are using **kraken** /!\ Discontinued after February 2022 /!\


# Final Setup

open `main.py` and edit the following values

`apichoice`: either `helix` or `kraken`

`twitchid`: the Twitch Client ID

`twitchsecret`: the Twitch Client Secret (only with `kraken`)

`dtoken`: the Discord Bot Token


Thank you alot to [YoannDeb](https://github.com/YoannDeb) for Helix API testing and setup and the .csv cleaner script!

# How to use the Discord Bot
## Commands
```
tw!info
tw!ping
tw!revenue [user] <option>
tw!check [user]
```

