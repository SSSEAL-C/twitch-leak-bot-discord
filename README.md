# twitch-leak-bot-discord
A bot to display per user data from the Twitch Leak by username


# Wheres the data?

I can't and don't want to supply the .csv's as they are 

 - too big
 - potential blacklisting and punishment from Twitch

The only data supplied is a list of ID's in a .json for who was in the leak.

If you get the CSV's (via your own methods) you extract each .csv to the file format `all_revenues_yy_mm.csv` (eg. `all_revenues_21_01.csv` is for January 2021) to the folder `data/`

You can also shrink the size of all these CSV's using a handy script by [YoannDeb](https://github.com/YoannDeb) to delete the blank lines.

Just run csv_setup.py once. It will take a little time but will significatively accelerate future process.

# Setup

Create 2 folders in the root of the folder. `data` and `output`.

You need two or three values
 - A discord bot token
 - A twitch client ID [Register an app](https://dev.twitch.tv/console/apps/create)
 - A twitch client secret (only with Helix)

Set them in the `main.py` file

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
```tw!info```

```tw!revenue [user] <graph? yes/no>```
