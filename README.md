# twitch-leak-bot-discord
A bot to display per user data from the Twitch Leak by username


## Wheres the data?

I can't and don't want to supply the .csv's as they are 

 - too big
 - potential blacklisting and punishment from Twitch

The only data supplied is a list of ID's in a .json for who was in the leak.

If you get the CSV's (via your own methods) you extract each .csv to the file format `all_revenues_yy_mm.csv` (eg. `all_revenues_21_01.csv` is for January 2021) to the folder `data/`

You can also shrink the size of all these CSV's using a handy script by [YoannDeb](https://raw.githubusercontent.com/YoannDeb/twitch_leak_csv_reader/master/csv_cleaner.py) to delete the blank lines (requies tablib, must be used in the `data/` folder)

## Setup

Create 2 folders in the root of the folder. `data` and `output`.

You need two values
 - A discord bot token
 - A twitch client ID token [Register an app](https://dev.twitch.tv/console/apps/create)

Set them in the `main.py` file
 
### Twitch Client App Registration Settings

Name: Can be anything

OAuth Redirect URLs: `http://localhost/`

Category: `Other`

Other Details: Can be anything



