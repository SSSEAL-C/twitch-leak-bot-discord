import csv
from os import listdir
from os.path import isfile, join
import pathlib
import json
import datetime
from urllib.parse import quote

import requests
from discord.ext import commands
import discord
import pyshorteners

now = datetime.datetime.utcnow()

API_CHOICE = 'helix'  # use either helix or kraken
TWITCH_ID = "twitch client id"
TWITCH_SECRET = "twitch client secret"  # only required for helix
DISCORD_TOKEN = 'discord bot token'

DISCORD_BOT_PREFIX = "tw3!"

if TWITCH_ID == "twitch client id" or DISCORD_TOKEN == 'discord bot token':
    exit("You must enter twitch adn discord API parameters, see README.md for instructions")
if API_CHOICE == 'helix' and TWITCH_SECRET == "twitch client secret":
    exit("If twitch API is helix, you must enter twitch client secret, see README.md for instructions")

cached_results = {}


async def store_user_info_in_cache(bio, created, display_name, logo, streamer_data, streamer_id, username):
    print("storing_user")
    cached_results[username] = {
        "streamer_id": streamer_id,
        "display_name": display_name,
        "logo": logo,
        "bio": bio,
        "created": created,
        "streamer_data": streamer_data
    }
    print(f"{username} stored in cache")


async def retrieve_streamer_data_from_cache(username):
    streamer_data = cached_results[username]["streamer_data"]
    return streamer_data


async def retrieve_user_info_from_cache(username):
    streamer_id = cached_results[username]["streamer_id"]
    display_name = cached_results[username]["display_name"]
    logo = cached_results[username]["logo"]
    bio = cached_results[username]["bio"]
    created = cached_results[username]["created"]
    print(f"{username} retrieved from cache")
    return bio, created, display_name, logo, streamer_id


async def send_msg(ctx, username, amount_count, countfiles):
    print("send_message")
    await ctx.edit(
        content=':white_check_mark: `' + username + ' data found! (' + str(amount_count) + '/' + str(countfiles) + ')`')


async def send_err(ctx, username, amount_count, countfiles):
    print("send_err")
    await ctx.edit(content=':x: `' + username + ' no data found! (' + str(amount_count) + '/' + str(countfiles) + ')`')


async def check_id(streamer_id):
    detected = 0
    with open(pathlib.Path.cwd() / 'data' / 'ids' / 'ids.json', 'r') as g1:
        g = g1.read()
        data = json.loads(g)
        users = data['ids']
        for row in users:
            if row == streamer_id:
                detected = 1
        if detected == 0:
            return False
        if detected == 1:
            return True


async def get_access_token():
    r = requests.post("https://id.twitch.tv/oauth2/token?client_id=" + TWITCH_ID +
                      '&client_secret=' + TWITCH_SECRET + '&grant_type=client_credentials')
    rjson = json.loads(r.text)
    return rjson['access_token']


async def main_parser(streamer_id, display_name, ctx, data2019, data2020, data2021):
    grosstotal = 0
    yearog = "19"
    monthog = "06"
    adtotal = 0
    subtotal = 0
    bitstotal = 0
    primestotal = 0
    amount_count = 0
    amount_count_s = 0

    onlyfiles = [f for f in listdir('./data/') if isfile(join('./data/', f))]
    countfiles = len(onlyfiles)
    for file in onlyfiles:
        filearr = file.split("_")
        year = filearr[2]
        month = filearr[3]
        month = month[:-4]
        try:
            with open('./data/' + str(file), 'r') as g:
                reader = csv.reader(g)
                detected = 0
                report_date = str(month) + '/' + str(year)
                for row in reader:
                    if row[0] == streamer_id:
                        detected = 1
                        if amount_count_s == 0:
                            yearog = str(year)
                            monthog = str(month)
                        amount_count_s = amount_count_s + 1
                        amount_count = amount_count + 1

                        # Values converted in cents before storage
                        ad_share_gross = float(row[2])
                        sub_share_gross = float(row[3])
                        bits_share_gross = float(row[4])
                        bits_developer_share_gross = float(row[5])
                        bits_extension_share_gross = float(row[6])
                        prime_sub_share_gross = float(row[7])
                        bit_share_ad_gross = float(row[8])
                        fuel_rev_gross = float(row[9])
                        bb_rev_gross = float(row[10])

                        # Adding values of same category
                        bits = bits_share_gross + bit_share_ad_gross + bits_developer_share_gross + bits_extension_share_gross
                        total = ad_share_gross + sub_share_gross + bits + prime_sub_share_gross + fuel_rev_gross + bb_rev_gross

                        # Calculating totals
                        grosstotal += total
                        adtotal += ad_share_gross
                        subtotal += sub_share_gross
                        bitstotal += bits
                        primestotal += prime_sub_share_gross

                        # convert back in cents before making month data list
                        month_data = [round(total, 2), round(ad_share_gross, 2), round(sub_share_gross, 2),
                                      round(prime_sub_share_gross, 2), bits, str(month), str(year)]

                        if year == "19":
                            data2019.append(month_data)
                        if year == "20":
                            data2020.append(month_data)
                        if year == "21":
                            data2021.append(month_data)
                        await send_msg(ctx, display_name, amount_count, countfiles)

            if detected == 0:
                amount_count = amount_count + 1
                await send_err(ctx, display_name, amount_count, countfiles)

        except Exception as e:
            print(' -Revenue- ERR: ' + str(e))

        #  Adding a blank month to year data.
        if detected == 0:
            month_data = [0, 0, 0, 0, 0, str(month), str(year)]
            if year == "19":
                data2019.append(month_data)
            if year == "20":
                data2020.append(month_data)
            if year == "21":
                data2021.append(month_data)
    return [round(grosstotal, 2), round(adtotal, 2), round(subtotal, 2), round(primestotal, 2), round(bitstotal, 2),
            monthog, yearog, data2019, data2020, data2021]


client = discord.Client()
LABELS = ['08/19', '09/19', '10/19', '11/19', '12/19', '01/20', '02/20', '03/20', '04/20', '05/20', '06/20', '07/20',
          '08/20',
          '09/20', '10/20', '11/20', '12/20', '01/21', '02/21', '03/21', '04/21', '05/21', '06/21', '07/21', '08/21',
          '09/21', '10/21']

intents = discord.Intents.default()
activity = discord.Game(name=f"{DISCORD_BOT_PREFIX}info")
bot = commands.Bot(command_prefix=DISCORD_BOT_PREFIX, intents=intents,
                   activity=activity, status=discord.Status.online)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


#
# '''
# Bot commands
# '''
#

@bot.command()
async def check(ctx, username: str):
    username_before_api = username
    main_msg = await ctx.send(content='`Checking ' + username + '...`')
    streamer_id = ""

    print(f"check {username}")

    # debug
    streamer_id = 71092938
    display_name = "debug"
    logo = "https://tinyurl.com/ygdm8peg"
    bio = "debug"
    created = "debug"

    if API_CHOICE == 'helix':
        atoken = await get_access_token()
        r = requests.get("https://api.twitch.tv/helix/users?login=" + username_before_api.lower(),
                         headers={"Client-ID": TWITCH_ID, 'Authorization': 'Bearer ' + atoken})
        rjson = json.loads(r.text)
        try:
            streamer_id = rjson['data'][0]["id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['data'][0]["profile_image_url"]
            bio = rjson['data'][0]["description"]
            created = rjson['data'][0]["created_at"]
        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken. (check your twitch tokens)')
            return

    if API_CHOICE == 'kraken':
        r = requests.get("https://api.twitch.tv/kraken/users?login=" + username_before_api.lower(),
                         headers={"Client-ID": TWITCH_ID, "Accept": "application/vnd.twitchtv.v5+json"})
        rjson = json.loads(r.text)
        try:
            streamer_id = rjson['users'][0]["_id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['users'][0]["logo"]
            bio = rjson['users'][0]["bio"]
            created = rjson['users'][0]["created_at"]
        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken.')
            return

    username_after_api = username

    idcheck = await check_id(streamer_id)
    if idcheck:
        now = datetime.datetime.utcnow()
        embed = discord.Embed(url=f"https://twitch.tv/{username}",
                              title=f"Twitch Creator Info - {display_name} - ({username_after_api})",
                              description="`This user is in the leak!`", timestamp=now)

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                                                           str(bio) + '\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`" + str(created) + "`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        await main_msg.edit(embed=embed, content="")
    if not idcheck:
        now = datetime.datetime.utcnow()
        embed = discord.Embed(url=f"https://twitch.tv/{username}",
                              title=f"Twitch Creator Info - {display_name} - ({username})",
                              description="`This user is not in the leak!`", timestamp=now)

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                                                           str(bio) + '\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`" + str(created) + "`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        await main_msg.edit(embed=embed, content="")


@bot.command()
async def revenue(ctx, username: str, *options: str):
    username = username.lower()

    data2019 = []
    data2020 = []
    data2021 = []

    print(f"revenue {username}")

    # debug
    streamer_id = 71092938
    display_name = "debug"
    logo = "https://tinyurl.com/ygdm8peg"
    bio = "debug"
    created = "debug"

    if username in cached_results:
        bio, created, display_name, logo, streamer_id = await retrieve_user_info_from_cache(username)
    else:
        if API_CHOICE == 'helix':
            atoken = await get_access_token()
            r = requests.get("https://api.twitch.tv/helix/users?login=" + username.lower(),
                             headers={"Client-ID": TWITCH_ID, 'Authorization': 'Bearer ' + atoken})
            rjson = json.loads(r.text)
            try:
                streamer_id = rjson['data'][0]["id"]
                display_name = rjson['data'][0]["display_name"]
                logo = rjson['data'][0]["profile_image_url"]
                bio = rjson['data'][0]["description"]
                created = rjson['data'][0]["created_at"]

            except Exception as e:
                print(str(e))
                await ctx.send('This user does not exist or the API is broken. (check your twitch tokens)')
                return

        if API_CHOICE == 'kraken':
            r = requests.get("https://api.twitch.tv/kraken/users?login=" + username.lower(),
                             headers={"Client-ID": TWITCH_ID, "Accept": "application/vnd.twitchtv.v5+json"})
            rjson = json.loads(r.text)
            try:
                streamer_id = rjson['users'][0]["_id"]
                display_name = rjson['data'][0]["display_name"]
                logo = rjson['users'][0]["logo"]
                bio = rjson['users'][0]["bio"]
                created = rjson['users'][0]["created_at"]

            except Exception as e:
                print(str(e))
                await ctx.send('This user does not exist or the API is broken.')
                return
    print("2")
    idcheck = await check_id(streamer_id)
    print("3")
    if idcheck:
        print("4")
        main_msg = await ctx.send(
            'Data for ' + display_name + ' is loading... You will be pinged when the embed is sent!')
        print("5")
        # Check presence of streamer in cache
        if username in cached_results:
            streamer_data = await retrieve_streamer_data_from_cache(username)
        else:
            streamer_data = await main_parser(streamer_id, display_name, main_msg, data2019, data2020, data2021)
            print("6")
            # Storage of info in cache
            await store_user_info_in_cache(bio, created, display_name, logo, streamer_data, streamer_id, username)
        print("7")
        data2019 = streamer_data[7]
        data2020 = streamer_data[8]
        data2021 = streamer_data[9]
        month = streamer_data[5]
        year = streamer_data[6]
        now = datetime.datetime.utcnow()
        totaldatagross = []
        totaldataad = []
        totaldatasub = []
        totaldatabits = []
        totaldataprime = []

        total2019 = 0
        ad2019 = 0
        sub2019 = 0
        prime2019 = 0
        bits2019 = 0

        for month_of_2019 in data2019:
            totaldatagross.append(month_of_2019[0])
            totaldataad.append(month_of_2019[1])
            totaldatasub.append(month_of_2019[2])
            totaldataprime.append(month_of_2019[3])
            totaldatabits.append(month_of_2019[4])

            total2019 += month_of_2019[0]
            ad2019 += month_of_2019[1]
            sub2019 += month_of_2019[2]
            prime2019 += month_of_2019[3]
            bits2019 += month_of_2019[4]

        # rounding again
        total2019 = round(total2019, 2)
        ad2019 = round(ad2019, 2)
        sub2019 = round(sub2019, 2)
        prime2019 = round(prime2019, 2)
        bits2019 = round(bits2019, 2)

        if total2019 == 0:
            data19 = "No data in 2019!"
        else:
            data19 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2019)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2019)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2019)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2019)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2019)) + " USD`"

        total2020 = 0
        ad2020 = 0
        sub2020 = 0
        prime2020 = 0
        bits2020 = 0

        for month_of_2020 in data2020:
            totaldatagross.append(month_of_2020[0])
            totaldataad.append(month_of_2020[1])
            totaldatasub.append(month_of_2020[2])
            totaldataprime.append(month_of_2020[3])
            totaldatabits.append(month_of_2020[4])

            total2020 += month_of_2020[0]
            ad2020 += month_of_2020[1]
            sub2020 += month_of_2020[2]
            prime2020 += month_of_2020[3]
            bits2020 += month_of_2020[4]

        # rounding again
        total2020 = round(total2020, 2)
        ad2020 = round(ad2020, 2)
        sub2020 = round(sub2020, 2)
        prime2020 = round(prime2020, 2)
        bits2020 = round(bits2020, 2)

        if total2020 == 0:
            data20 = "No data in 2020!"
        else:
            data20 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2020)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2020)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2020)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2020)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2020)) + " USD`"

        total2021 = 0
        ad2021 = 0
        sub2021 = 0
        prime2021 = 0
        bits2021 = 0

        for month_of_2021 in data2021:
            totaldatagross.append(month_of_2021[0])
            totaldataad.append(month_of_2021[1])
            totaldatasub.append(month_of_2021[2])
            totaldataprime.append(month_of_2021[3])
            totaldatabits.append(month_of_2021[4])

            total2021 += month_of_2021[0]
            ad2021 += month_of_2021[1]
            sub2021 += month_of_2021[2]
            prime2021 += month_of_2021[3]
            bits2021 += month_of_2021[4]

        # rounding again
        total2021 = round(total2021, 2)
        ad2021 = round(ad2021, 2)
        sub2021 = round(sub2021, 2)
        prime2021 = round(prime2021, 2)
        bits2021 = round(bits2021, 2)

        if total2021 == 0:
            data21 = "No data in 2021!"
        else:
            data21 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2021)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2021)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2021)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2021)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2021)) + " USD`"

        # Pie chart data formatting
        ads_percentage = round(streamer_data[1] / streamer_data[0] * 100, 2)
        subs_percentage = round(streamer_data[2] / streamer_data[0] * 100, 2)
        primes_percentage = round(streamer_data[3] / streamer_data[0] * 100, 2)
        bits_percentage = round(streamer_data[4] / streamer_data[0] * 100, 2)

        # Some graph related stuff
        short_url = pyshorteners.Shortener()
        timeline_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name + " - Timeline of Gross Total', fontSize:20}},type:'line',data:{labels:" + str(
            LABELS) + ", datasets:[{label:'Gross Total', data: " + str(
            totaldatagross) + ", fill:false,borderColor:'blue'}]}}"
        detailed_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name + "', fontSize:20}},type:'line',data:{labels:" + str(
            LABELS) + ", datasets:[{label:'Ads', data: " + str(
            totaldataad) + ", fill:false,borderColor:'green'},{label:'Subs', data: " + str(
            totaldatasub) + ", fill:false,borderColor:'yellow'},{label:'Primes', data: " + str(
            totaldataprime) + ", fill:false,borderColor:'red'},{label:'Bits', data: " + str(
            totaldatabits) + ", fill:false,borderColor:'orange'}]}}"
        pie_chart_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name + \
                        " - Repartition in %', fontSize:20}},type:'pie',data:{labels:['Gross Ads', 'Gross Subs','Gross Primes','Gross Bits'],datasets:[{data:[" + str(
            ads_percentage) + "," + str(subs_percentage) + "," + str(primes_percentage) + "," + str(
            bits_percentage) + "]}]}}"

        if "timeline" in options or "detailed" in options or "piechart" in options or "allgraphs" in options:
            if "timeline" in options:
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(timeline_url))}")
            if "detailed" in options:
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(detailed_url))}")
            if "piechart" in options:
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(pie_chart_url))}")
            if "allgraphs" in options:
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(timeline_url))}")
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(detailed_url))}")
                await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(pie_chart_url))}")

        else:
            embed = discord.Embed(
                title=f"Twitch Creator Info - {display_name} - ({username})", timestamp=now,
                url=f"https://twitch.tv/{username}")
            main_data = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(streamer_data[0])) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(streamer_data[1])) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(streamer_data[2])) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(streamer_data[3])) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(streamer_data[4])) + " USD`"
            embed.set_thumbnail(url=logo)
            embed.add_field(name=':alarm_clock: Created At',
                            value="`" + str(created) + "`", inline=False)
            if bio:
                embed.add_field(name=':name_badge: Bio',
                                value='```\n' + str(bio) + '\n```', inline=False)
            embed.add_field(name="Data - Total `" + str(month) + '/' +
                                 str(year) + "` - `10/21`", value=main_data, inline=False)
            embed.add_field(name="Data - 2019", value=str(data19), inline=True)
            embed.add_field(name="Data - 2020", value=str(data20), inline=True)
            embed.add_field(name="Data - 2021", value=str(data21), inline=True)

            # Some graph related stuff
            if "nograph" not in options:
                embed.add_field(name="Graphs", value="Timeline of Gross Total: " + short_url.tinyurl.short(
                    'https://quickchart.io/chart?c=' + quote(timeline_url)) + '\nDetailed Timeline: ' +
                                                     short_url.tinyurl.short('https://quickchart.io/chart?c=' + quote(
                                                         detailed_url)) + '\nPi Chart of Gross Payment: ' + short_url.tinyurl.short(
                    'https://quickchart.io/chart?c=' + quote(pie_chart_url)))

            # Exemple code to handle other revenue command options (here parameter demo) :
            # if "demo" in options:
            #     print("demo")
            #     embed.add_field(name= "Demo", value= "Demo", inline=False)

            embed.set_footer(text="Made by SSSEAL-C")
            await main_msg.edit(content='<@' + str(ctx.author.id) + ">", embed=embed)

    # Embed if user exists but not in the leak
    if not idcheck:
        now = datetime.datetime.utcnow()
        embed = discord.Embed(title=f"Twitch Creator Info - {display_name} - ({username})",
                              description="`This user is not in the leak!`", timestamp=now,
                              url=f"https://twitch.tv/{username}")

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                                                           str(bio) + '\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`" + str(created) + "`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        await ctx.send(embed=embed)


@bot.command()
async def info(ctx):
    now = datetime.datetime.utcnow()
    embed = discord.Embed(title='Twitch Creator Info - Made by SSSEAL-C',
                          url="https://github.com/SSSEAL-C/twitch-leak-bot-discord", timestamp=now)
    embed.add_field(name=':busts_in_silhouette: Creators',
                    value='`realsovietseal#0001`', inline=False)
    embed.add_field(name=':gear: Commands',
                    value=f'```{DISCORD_BOT_PREFIX}revenue [twitch username] <option>\n{DISCORD_BOT_PREFIX}ping\n{DISCORD_BOT_PREFIX}info\n{DISCORD_BOT_PREFIX}check [twitch username]\n\neg. {DISCORD_BOT_PREFIX}revenue ludwig nograph```',
                    inline=False)
    embed.add_field(name=':gear: Revenue Command Options',
                    value='`nograph`\n`timeline`\n`detailed`\n`piechart`', inline=False)
    embed.add_field(name=':keyboard: Github',
                    value='`https://github.com/SSSEAL-C/twitch-leak-bot-discord`', inline=False)

    embed.set_footer(text="Made by SSSEAL-C")
    await ctx.send('<@' + str(ctx.author.id) + ">", embed=embed)


# @bot.command()
# async def ping(ctx):
#     embed_var = discord.Embed(title="Ping :ping_pong:")
#     embed_var.add_field(name="Latency", value=str(
#         round(bot.latency * 1000) + 'ms'), inline=False)
#     await ctx.send(embed=embed_var)


# @bot.command()
# async def cache(ctx):
#     cached_count = 0
#     embed_cache = discord.Embed(title='Twitch Creator Info - Streamers cached')
#     for key in cached_results:
#         cached_count += 1
#         embed_cache.add_field(name=f'{cached_results[key]["display_name"]} - ({key}) - ({cached_results[key]["display_name"]})',
#                               value=f'{cached_results[key]["streamer_data"][0]}$')
#     embed_cache.add_field(name=f'Streamer(s) in cache:',
#                           value=f'{cached_count}')
#     # embed_cache.edit(title=f'Twitch Creator Info - {cached_count}Streamers cached')
#     await ctx.send(embed=embed_cache)

#
# '''
# Error catching
# '''
#
#
# @revenue.error
# async def revenue_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
#         await ctx.send(f'You are not providing an argument! (eg. {DISCORD_BOT_PREFIX}revenue ludwig)')
#
#
# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, discord.ext.commands.errors.CommandNotFound):
#         await ctx.send("That command wasn't found! Sorry :-(")
#         await ctx.send(f"Type {DISCORD_BOT_PREFIX}info to see available commands :-)")
#     if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
#         await ctx.send("Please enter a command")
#         await ctx.send(f'(eg. {DISCORD_BOT_PREFIX}revenue ludwig)')
#         await ctx.send(f"Type {DISCORD_BOT_PREFIX}info to see all available commands :-)")

bot.run(DISCORD_TOKEN)
