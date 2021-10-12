from urllib.parse import quote
from discord.ext import commands
import discord
import csv
from os import listdir
from os.path import isfile, join
import requests
import json
import datetime
import os
import pyshorteners

now = datetime.datetime.utcnow()

VERSION = 'v1.0.3'
API_CHOICE = 'helix'  # use either helix or kraken
TWITCH_ID = "twitch client id"
TWITCH_SECRET = "twitch client secret"  # only required for helix
DISCORD_TOKEN = 'discord bot token'

DISCORD_BOT_PREFIX = "tw!"

if TWITCH_ID == "twitch client id" or DISCORD_TOKEN == 'discord bot token':
    exit("You must enter twitch adn discord API parameters, see README.md for instructions")
if API_CHOICE == 'helix' and TWITCH_SECRET == "twitch client secret":
    exit("If twitch API is helix, you must enter twitch client secret, see README.md for instructions")

cached_results = {}

def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

async def revenue_yearly_data_split(data2019):
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
    
    return [total2019,ad2019,sub2019,prime2019,bits2019,totaldatagross,totaldataad,totaldatasub, totaldatabits,totaldataprime]

async def revenue_data_setup(streamer_data):
    try:
        data2019 = streamer_data[7]
        data2020 = streamer_data[8]
        data2021 = streamer_data[9]
        month = streamer_data[5]
        year = streamer_data[6]
        now = datetime.datetime.utcnow()
        revenue2019 = await revenue_yearly_data_split(data2019)
        total2019 = revenue2019[0]
        ad2019 = revenue2019[1]
        sub2019 = revenue2019[2]
        prime2019 = revenue2019[3]
        bits2019 = revenue2019[4]
        totaldatagross2019 = revenue2019[5]
        totaldataad2019 = revenue2019[6]
        totaldatasub2019 = revenue2019[7]
        totaldatabits2019 = revenue2019[8]
        totaldataprime2019 = revenue2019[9]

        if total2019 == 0:
            data19 = "No data in 2019!"
        else:
            data19 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2019)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2019)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2019)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2019)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2019)) + " USD`"

        revenue2020 = await revenue_yearly_data_split(data2020)
        total2020 = revenue2020[0]
        ad2020 = revenue2020[1]
        sub2020 = revenue2020[2]
        prime2020 = revenue2020[3]
        bits2020 = revenue2020[4]
        totaldatagross2020 = revenue2020[5]
        totaldataad2020 = revenue2020[6]
        totaldatasub2020 = revenue2020[7]
        totaldatabits2020 = revenue2020[8]
        totaldataprime2020 = revenue2020[9]
        
        
        if total2020 == 0:
            data20 = "No data in 2020!"
        else:
            data20 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2020)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2020)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2020)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2020)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2020)) + " USD`"

        revenue2021 = await revenue_yearly_data_split(data2021)
        total2021 = revenue2021[0]
        ad2021 = revenue2021[1]
        sub2021 = revenue2021[2]
        prime2021 = revenue2021[3]
        bits2021 = revenue2021[4]
        totaldatagross2021 = revenue2021[5]
        totaldataad2021 = revenue2021[6]
        totaldatasub2021 = revenue2021[7]
        totaldatabits2021 = revenue2021[8]
        totaldataprime2021 = revenue2021[9]


        totaldatagross = totaldatagross2019+totaldatagross2020+totaldatagross2021
        totaldataad = totaldataad2019+totaldataad2020+totaldataad2021
        totaldatasub = totaldatasub2019+totaldatasub2020+totaldatasub2021
        totaldatabits = totaldatabits2019+totaldatabits2020+totaldatabits2021
        totaldataprime = totaldataprime2019+totaldataprime2020+totaldataprime2021


        if total2021 == 0:
            data21 = "No data in 2021!"
        else:
            data21 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2021)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2021)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2021)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2021)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2021)) + " USD`"
        return [data19,data20,data21,totaldatagross,totaldataad,totaldatasub,totaldatabits,totaldataprime,month,year,now]
    except Exception as e:
        print(full_stack())

async def api_choice(username,ctx):
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
                return [streamer_id,display_name,logo,bio,created]
            except Exception as e:
                print(full_stack())
                await ctx.send(f'This user {username} does not exist or the API is broken. (check your twitch tokens)')

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
            return [streamer_id,display_name,logo,bio,created]
        except Exception as e:
            print(full_stack())
            await ctx.send(f'The user {username} does not exist or the API is broken.')
            return

async def store_user_info_in_cache(bio, created, display_name, logo, streamer_data, streamer_id, username):
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
    await ctx.edit(content=':white_check_mark: `'+username+' data found! ('+str(amount_count)+'/'+str(countfiles)+')`')


async def send_err(ctx, username, amount_count, countfiles):
    await ctx.edit(content=':x: `'+username+' no data found! ('+str(amount_count)+'/'+str(countfiles)+')`')


async def check_id(streamer_id):
    check_detected = 0
    with open(os.path.dirname(__file__)+'\\data\\ids\\ids.json', 'r') as g1:
        g = g1.read()
        data = json.loads(g)
        users = data['ids']
        for row in users:
            if row == streamer_id:
                check_detected = 1
        if check_detected == 0:
            return False
        if check_detected == 1:
            return True


async def get_access_token():
    r = requests.post("https://id.twitch.tv/oauth2/token?client_id=" + TWITCH_ID +
                      '&client_secret=' + TWITCH_SECRET + '&grant_type=client_credentials')
    rjson = json.loads(r.text)
    return rjson['access_token']


async def main_parser(streamer_id, display_name, ctx, data2019, data2020, data2021):
    try:
        grosstotal = 0
        yearog = "19"
        monthog = "06"
        adtotal = 0
        subtotal = 0
        bitstotal = 0
        primestotal = 0
        amount_count = 0
        amount_count_s = 0

        onlyfiles = [f for f in listdir(os.path.dirname(__file__)+'\\data\\csv\\') if isfile(join(os.path.dirname(__file__)+'\\data\\csv\\', f))]
        countfiles = len(onlyfiles)
        for file in onlyfiles:
            filearr = file.split("_")
            year = filearr[2]
            month = filearr[3]
            month = month[:-4]
            try:
                with open(os.path.dirname(__file__)+'\\data\\csv\\'+str(file), 'r') as g:
                    reader = csv.reader(g)
                    detected = 0
                    report_date = str(month)+'/'+str(year)
                    for row in reader:
                        if row[0] == streamer_id:
                            detected = 1
                            if amount_count_s == 0:
                                yearog = str(year)
                                monthog = str(month)
                            amount_count_s = amount_count_s+1
                            amount_count = amount_count+1

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
                            month_data = [round(total, 2), round(ad_share_gross, 2), round(sub_share_gross, 2), round(prime_sub_share_gross, 2), bits, str(month), str(year)]

                            if year == "19":
                                data2019.append(month_data)
                            if year == "20":
                                data2020.append(month_data)
                            if year == "21":
                                data2021.append(month_data)
                            await send_msg(ctx, display_name, amount_count, countfiles)

                if detected == 0:
                    amount_count = amount_count+1
                    await send_err(ctx, display_name, amount_count, countfiles)
                if detected == 0:
                    month_data = [0, 0, 0, 0, 0, str(month), str(year)]
                    if year == "19":
                        data2019.append(month_data)
                    if year == "20":
                        data2020.append(month_data)
                    if year == "21":
                        data2021.append(month_data)

            except Exception as e:
                print(full_stack())

            #  Adding a blank month to year data.
        return [round(grosstotal, 2), round(adtotal, 2), round(subtotal, 2), round(primestotal, 2), round(bitstotal, 2), monthog, yearog, data2019, data2020, data2021]
    except Exception as e:
        print(full_stack())


client = discord.Client()
LABELS = ['08/19', '09/19', '10/19', '11/19', '12/19', '01/20', '02/20', '03/20', '04/20', '05/20', '06/20', '07/20', '08/20',
          '09/20', '10/20', '11/20', '12/20', '01/21', '02/21', '03/21', '04/21', '05/21', '06/21', '07/21', '08/21', '09/21', '10/21']

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
    try:
        username_before_api = username
        main_msg = await ctx.send(content='`Checking '+username+'...`')
        streamer_id = ""

        print(f"check {username}")

        if username in cached_results:
            bio, created, display_name, logo, streamer_id = await retrieve_user_info_from_cache(username)
        else:
            api_data = await api_choice(username,ctx)
            streamer_id = api_data[0]
            display_name = api_data[1]
            logo = api_data[2]
            bio = api_data[3]
            created = api_data[4]


        idcheck = await check_id(streamer_id)
        if idcheck:
            now = datetime.datetime.utcnow()
            embed = discord.Embed(url=f"https://twitch.tv/{username}", title=f"Twitch Creator Info - {display_name} - ({username})",
                                description="`This user is in the leak!`", timestamp=now)

            embed.set_thumbnail(url=logo)
            if bio:
                embed.add_field(name=':name_badge: Bio', value='```\n' +
                                str(bio)+'\n```', inline=False)
            embed.add_field(name=':alarm_clock: Created At',
                            value="`"+str(created)+"`", inline=False)
            embed.set_footer(text="Made by SSSEAL-C")
            await main_msg.edit(embed=embed, content="")
        if not idcheck:
            now = datetime.datetime.utcnow()
            embed = discord.Embed(url=f"https://twitch.tv/{username}", title=f"Twitch Creator Info - {display_name} - ({username})",
                                description="`This user is not in the leak!`", timestamp=now)

            embed.set_thumbnail(url=logo)
            if bio:
                embed.add_field(name=':name_badge: Bio', value='```\n' +
                                str(bio)+'\n```', inline=False)
            embed.add_field(name=':alarm_clock: Created At',
                            value="`"+str(created)+"`", inline=False)
            embed.set_footer(text="Made by SSSEAL-C")
            await main_msg.edit(embed=embed, content="")
    except Exception as e:
        print(full_stack())
        print(str(e))


@bot.command()
async def revenue(ctx, username: str, *options: str):
    try:
        username = username.lower()
        data2019 = []
        data2020 = []
        data2021 = []

        print(f"revenue {username}")

        if username in cached_results:
            bio, created, display_name, logo, streamer_id = await retrieve_user_info_from_cache(username)
        else:
            api_data = await api_choice(username,ctx)
            streamer_id = api_data[0]
            display_name = api_data[1]
            logo = api_data[2]
            bio = api_data[3]
            created = api_data[4]
        idcheck = await check_id(streamer_id)
        if idcheck:
            totaldatagross = 0
            totaldataad = 0
            totaldatasub = 0
            totaldatabits = 0
            totaldataprime = 0
            main_msg = await ctx.send('Data for '+display_name+' is loading... You will be pinged when the embed is sent!')
            # Check presence of streamer in cache
            if username in cached_results:
                streamer_data = await retrieve_streamer_data_from_cache(username)
            else:
                streamer_data = await main_parser(streamer_id, display_name, main_msg, data2019, data2020, data2021)
                
                # Storage of info in cache
                await store_user_info_in_cache(bio, created, display_name, logo, streamer_data, streamer_id, username)
            revenue_data_one = await revenue_data_setup(streamer_data)
            data19 = revenue_data_one[0]
            data20 = revenue_data_one[1]
            data21 = revenue_data_one[2]
            totaldatagross = revenue_data_one[3]
            totaldataad= revenue_data_one[4]
            totaldatasub = revenue_data_one[5]
            totaldatabits = revenue_data_one[6]
            totaldataprime = revenue_data_one[7]
            month = revenue_data_one[8]
            year = revenue_data_one[9]
            now= revenue_data_one[10]

            # Pie chart data formatting
            ads_percentage = round(streamer_data[1] / streamer_data[0] * 100, 2)
            subs_percentage = round(streamer_data[2] / streamer_data[0] * 100, 2)
            primes_percentage = round(streamer_data[3] / streamer_data[0] * 100, 2)
            bits_percentage = round(streamer_data[4] / streamer_data[0] * 100, 2)

            # Some graph related stuff
            short_url = pyshorteners.Shortener()
            timeline_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name +" - Timeline of Gross Total', fontSize:20}},type:'line',data:{labels:" + str(LABELS) + ", datasets:[{label:'Gross Total', data: " + str(totaldatagross) + ", fill:false,borderColor:'blue'}]}}"
            detailed_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name + "', fontSize:20}},type:'line',data:{labels:" + str(
                LABELS) + ", datasets:[{label:'Ads', data: " + str(
                totaldataad) + ", fill:false,borderColor:'green'},{label:'Subs', data: " + str(
                totaldatasub) + ", fill:false,borderColor:'yellow'},{label:'Primes', data: " + str(
                totaldataprime) + ", fill:false,borderColor:'red'},{label:'Bits', data: " + str(
                totaldatabits) + ", fill:false,borderColor:'orange'}]}}"
            pie_chart_url = "{options:{title:{display:true,text:'Twitch Creator Data - "+display_name + \
                " - Repartition in %', fontSize:20}},type:'pie',data:{labels:['Gross Ads', 'Gross Subs','Gross Primes','Gross Bits'],datasets:[{data:["+str(
                    ads_percentage)+","+str(subs_percentage)+","+str(primes_percentage)+","+str(bits_percentage)+"]}]}}"

            embed = discord.Embed(
                title="Twitch Creator Info - "+display_name+" - ("+username+")", timestamp=now, url="https://twitch.tv/"+username)
            
            
            if "timeline" in options or "detailed" in options or "piechart" in options or "allgraphs" in options:
                if "timeline" in options:
                    graph=f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(timeline_url))}"
                    embed.set_image(url=graph)
                if "detailed" in options:
                    graph=f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(detailed_url))}"
                    embed.set_image(url=graph)
                if "piechart" in options:
                    graph=f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(pie_chart_url))}"
                    embed.set_image(url=graph)
                if "allgraphs" in options:
                    await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(timeline_url))}")
                    await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(detailed_url))}")
                    await ctx.send(f"{short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(pie_chart_url))}")
                    return
            
            main_data = ':moneybag: Gross Total: '+"`$"+str("{:,}".format(streamer_data[0]))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(streamer_data[1]))+" USD`\n"+':star: Sub Total: '+"`$"+str(
                "{:,}".format(streamer_data[2]))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(streamer_data[3]))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(streamer_data[4]))+" USD`"
            embed.set_thumbnail(url=logo)
            embed.add_field(name=':alarm_clock: Created At',
                            value="`"+str(created)+"`", inline=False)
            if bio:
                embed.add_field(name=':name_badge: Bio',
                                value='```\n'+str(bio)+'\n```', inline=False)
            embed.add_field(name="Data - Total `"+str(month)+'/' +
                            str(year)+"` - `10/21`", value=main_data, inline=False)
            embed.add_field(name="Data - 2019", value=str(data19), inline=True)
            embed.add_field(name="Data - 2020", value=str(data20), inline=True)
            embed.add_field(name="Data - 2021", value=str(data21), inline=True)

            # Some graph related stuff
            if "nograph" not in options and "timeline" not in options and "detailed" not in options and "piechart" not in options and "allgraphs" not in options:
                embed.add_field(name="Graphs", value="Timeline of Gross Total: "+short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(timeline_url))+'\nDetailed Timeline: ' +
                                short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(detailed_url))+'\nPi Chart of Gross Payment: '+short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(pie_chart_url)))

            # Exemple code to handle other revenue command options (here parameter demo) :
            # if "demo" in options:
            #     print("demo")
            #     embed.add_field(name= "Demo", value= "Demo", inline=False)

            embed.set_footer(text="Made by SSSEAL-C")
            await main_msg.edit(content='<@'+str(ctx.author.id)+">", embed=embed)

        # Embed if user exists but not in the leak
        if not idcheck:
            now = datetime.datetime.utcnow()
            embed = discord.Embed(title=f"Twitch Creator Info - {display_name} - ({username})",
                                description="`This user is not in the leak!`", timestamp=now, url=f"https://twitch.tv/{username}")

            embed.set_thumbnail(url=logo)
            if bio:
                embed.add_field(name=':name_badge: Bio', value='```\n' +
                                str(bio)+'\n```', inline=False)
            embed.add_field(name=':alarm_clock: Created At',
                            value="`"+str(created)+"`", inline=False)
            embed.set_footer(text="Made by SSSEAL-C")
            await ctx.send(embed=embed)
    except Exception as e:
        print(full_stack())

@bot.command()
async def info(ctx):
    now = datetime.datetime.utcnow()
    embed = discord.Embed(title='Twitch Creator Info - Made by SSSEAL-C',
                          url="https://github.com/SSSEAL-C/twitch-leak-bot-discord", timestamp=now)
    embed.add_field(name=':busts_in_silhouette: Creators',
                    value='`realsovietseal#0001`', inline=False)
    embed.add_field(name=':gear: Commands',
                    value=f'```{DISCORD_BOT_PREFIX}revenue [twitch username] <option>\n{DISCORD_BOT_PREFIX}ping\n{DISCORD_BOT_PREFIX}info\n{DISCORD_BOT_PREFIX}check [twitch username]\n\neg. {DISCORD_BOT_PREFIX}revenue ludwig nograph```', inline=False)
    embed.add_field(name=':gear: Revenue Command Options',
                    value='`nograph`\n`timeline`\n`detailed`\n`piechart`\n`allgraphs`', inline=False)
    embed.add_field(name=':keyboard: Github',
                    value='`https://github.com/SSSEAL-C/twitch-leak-bot-discord`', inline=False)
    embed.add_field(name=':cd: Version',
                            value=f'`{VERSION}`', inline=False)
    embed.set_footer(text="Made by SSSEAL-C")
    await ctx.send('<@'+str(ctx.author.id)+">", embed=embed)


@bot.command()
async def ping(ctx):
    try:
        embed_var = discord.Embed(title="Ping :ping_pong:")
        embed_var.add_field(name="Latency", value=str(
            round(bot.latency * 1000)) + 'ms', inline=False)
        await ctx.send(embed=embed_var)
    except Exception as e:
        print(full_stack())
        print(str(e))


@bot.command()
async def cache(ctx):
    try:
        cached_count = 0
        cached_streamer_list=[]
        for key in cached_results:
            cached_count += 1
            cached_streamer_list.append(key)
        if cached_count == 1:
            embed_cache = discord.Embed(title=f'Cache - {cached_count} user cached')
        else:
            embed_cache = discord.Embed(title=f'Cache - {cached_count} users cached')
        if str(cached_streamer_list) == "[]":
            embed_cache.add_field(name=f'User list',
                                    value=f'No users cached!')
        if str(cached_streamer_list) != "[]":
            embed_cache.add_field(name=f'User list',
                                    value=str("\n".join(cached_streamer_list)))
        
        # embed_cache.edit(title=f'Twitch Creator Info - {cached_count}Streamers cached')
        await ctx.send(embed=embed_cache)
    except Exception as e:
        print(full_stack())
        print(str(e))


@bot.command()
async def compare(ctx, username_one: str, username_two:str, *options:str):
    username_one = username_one.lower()
    username_two = username_two.lower()

    data2019_one = []
    data2020_one = []
    data2021_one = []
    data2019_two = []
    data2020_two = []
    data2021_two = []

    print(f"compare {username_one} vs. {username_two}")
    if username_one in cached_results:
        bio_one, created_one, display_name_one, logo_one, streamer_id_one = await retrieve_user_info_from_cache(username_one)
    else:
        api_data_one = await api_choice(username_one,ctx)
        streamer_id_one = api_data_one[0]
        display_name_one = api_data_one[1]
        logo_one = api_data_one[2]
        bio_one = api_data_one[3]
        created_one = api_data_one[4]
    if username_two in cached_results:
        bio_two, created_two, display_name_two, logo_two, streamer_id_two = await retrieve_user_info_from_cache(username_two)
    else:
        api_data_two = await api_choice(username_two,ctx)
        streamer_id_two = api_data_two[0]
        display_name_two = api_data_two[1]
        logo_two = api_data_two[2]
        bio_two = api_data_two[3]
        created_two = api_data_two[4]
    idcheck_one = await check_id(streamer_id_one)
    idcheck_two = await check_id(streamer_id_two)
    if idcheck_one:
        if idcheck_two:
            try:
                totaldatagross_one = 0
                totaldataad_one = 0
                totaldatasub_one = 0
                totaldatabits_one = 0
                totaldataprime_one = 0
                totaldatagross_two = 0
                totaldataad_two = 0
                totaldatasub_two = 0
                totaldatabits_two = 0
                totaldataprime_two = 0
                main_msg = await ctx.send('Data for '+display_name_one+' is loading... You will be pinged when the embed is sent!')
                # Check presence of streamer in cache
                if username_one in cached_results:
                    streamer_data_one = await retrieve_streamer_data_from_cache(username_one)
                else:
                    streamer_data_one = await main_parser(streamer_id_one, display_name_one, main_msg, data2019_one, data2020_one, data2021_one)
                    # Storage of info in cache
                    await store_user_info_in_cache(bio_one, created_one, display_name_one, logo_one, streamer_data_one, streamer_id_one, username_one)
                
                revenue_data_one = await revenue_data_setup(streamer_data_one)
                data19_one = revenue_data_one[0]
                data20_one = revenue_data_one[1]
                data21_one = revenue_data_one[2]
                totaldatagross_one = revenue_data_one[3]
                totaldataad_one= revenue_data_one[4]
                totaldatasub_one = revenue_data_one[5]
                totaldatabits_one = revenue_data_one[6]
                totaldataprime_one = revenue_data_one[7]
                month_one = revenue_data_one[8]
                year_one = revenue_data_one[9]
                now_one = revenue_data_one[10]
                # Pie chart data formatting
                ads_percentage_one = round(streamer_data_one[1] / streamer_data_one[0] * 100, 2)
                subs_percentage_one = round(streamer_data_one[2] / streamer_data_one[0] * 100, 2)
                primes_percentage_one = round(streamer_data_one[3] / streamer_data_one[0] * 100, 2)
                bits_percentage_one = round(streamer_data_one[4] / streamer_data_one[0] * 100, 2)
                
                if username_two in cached_results:
                    streamer_data_two = await retrieve_streamer_data_from_cache(username_two)
                else:
                    streamer_data_two = await main_parser(streamer_id_two, display_name_two, main_msg, data2019_two, data2020_two, data2021_two)
                    # Storage of info in cache
                    await store_user_info_in_cache(bio_two, created_two, display_name_two, logo_two, streamer_data_two, streamer_id_two, username_two)
                revenue_data_two = await revenue_data_setup(streamer_data_two)
                data19_two = revenue_data_two[0]
                data20_two = revenue_data_two[1]
                data21_two = revenue_data_two[2]
                totaldatagross_two = revenue_data_two[3]
                totaldataad_two= revenue_data_two[4]
                totaldatasub_two = revenue_data_two[5]
                totaldatabits_two = revenue_data_two[6]
                totaldataprime_two = revenue_data_two[7]
                month_two = revenue_data_two[8]
                year_two = revenue_data_two[9]
                now_two = revenue_data_two[10]
                # Pie chart data formatting
                ads_percentage_two = round(streamer_data_two[1] / streamer_data_two[0] * 100, 2)
                subs_percentage_two = round(streamer_data_two[2] / streamer_data_two[0] * 100, 2)
                primes_percentage_two = round(streamer_data_two[3] / streamer_data_two[0] * 100, 2)
                bits_percentage_two = round(streamer_data_two[4] / streamer_data_two[0] * 100, 2)

                # Some graph related stuff
                short_url = pyshorteners.Shortener()
                timeline_url = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name_one +" vs. "+display_name_two +" - Timeline of Gross Total', fontSize:20}},type:'line',data:{labels:" + str(LABELS) + ", datasets:[{label:'Gross Total of "+display_name_one+"', data: " + str(totaldatagross_one) + ", fill:false,borderColor:'blue'},{label:'Gross Total of "+display_name_two+"', data: " + str(totaldatagross_two) + ", fill:false,borderColor:'red'}]}}"

                embed = discord.Embed(
                    title=f"Twitch Creator Info - {display_name_one} vs. {display_name_two}", timestamp=now)
                main_data_one = f':moneybag: Gross Total {display_name_one} '+"`$"+str("{:,}".format(streamer_data_one[0]))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(streamer_data_one[1]))+" USD`\n"+':star: Sub Total: '+"`$"+str(
                    "{:,}".format(streamer_data_one[2]))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(streamer_data_one[3]))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(streamer_data_one[4]))+" USD`"
                main_data_two = f':moneybag: Gross Total {display_name_two} '+"`$"+str("{:,}".format(streamer_data_two[0]))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(streamer_data_two[1]))+" USD`\n"+':star: Sub Total: '+"`$"+str(
                    "{:,}".format(streamer_data_two[2]))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(streamer_data_two[3]))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(streamer_data_two[4]))+" USD`"
                embed.add_field(name=f"{display_name_one} - Total - `"+str(month_one)+'/' +
                                str(year_one)+"` - `10/21`", value=main_data_one, inline=False)
                embed.add_field(name=f"{display_name_one} - 2019", value=str(data19_one), inline=True)
                embed.add_field(name=f"{display_name_one} - 2020", value=str(data20_one), inline=True)
                embed.add_field(name=f"{display_name_one} - 2021", value=str(data21_one), inline=True)
                embed.add_field(name=f"{display_name_two} - Total - `"+str(month_two)+'/' +
                                str(year_two)+"` - `10/21`", value=main_data_two, inline=False)
                embed.add_field(name=f"{display_name_two} - 2019", value=str(data19_two), inline=True)
                embed.add_field(name=f"{display_name_two} - 2020", value=str(data20_two), inline=True)
                embed.add_field(name=f"{display_name_two} - 2021", value=str(data21_two), inline=True)
                embed.set_image(url=short_url.tinyurl.short('https://quickchart.io/chart?c='+quote(timeline_url)))
                return await main_msg.edit(content='<@'+str(ctx.author.id)+">", embed=embed)
            except Exception as e:
                print(full_stack())
        if not idcheck_two:
            return await ctx.send(content=f"The user {username_two} is not in the leak!")
    if not idcheck_one:
        return await ctx.send(content=f"The user {username_one} is not in the leak!")

'''
Error catching
'''


@revenue.error
async def revenue_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send(f'You are not providing an argument! (eg. {DISCORD_BOT_PREFIX}revenue ludwig)')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("That command wasn't found! Sorry :-(")
        await ctx.send(f"Type {DISCORD_BOT_PREFIX}info to see available commands :-)")
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("Please enter a command")
        await ctx.send(f'(eg. {DISCORD_BOT_PREFIX}revenue ludwig)')
        await ctx.send(f"Type {DISCORD_BOT_PREFIX}info to see all available commands :-)")

bot.run(DISCORD_TOKEN)