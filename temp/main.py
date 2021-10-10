from urllib.parse import quote
from discord.ext import commands
import discord
import csv
from os import listdir
from os.path import isfile, join
import requests
import json
import datetime

time = datetime.datetime.utcnow()

apichoice = 'helix'  # use either helix or kraken
twitchid = "twitch client id"
twitchsecret = "twitch client secret"  # only required for helix
dtoken = 'discord bot token'

if twitchid == "twitch client id" or dtoken == 'discord bot token':
    exit("You must enter twitch adn discord API parameters, see README.md for instructions")
if apichoice == 'helix' and twitchsecret == "twitch client secret":
    exit("If twitch API is helix, you must enter twitch client secret, see README.md for instructions")


async def sendmsg(ctx, username, amount_count, countfiles):
    await ctx.edit(content=':white_check_mark: `'+username+' data found! ('+str(amount_count)+'/'+str(countfiles)+')`')


async def senderr(ctx, username, amount_count, countfiles):
    await ctx.edit(content=':x: `'+username+' no data found! ('+str(amount_count)+'/'+str(countfiles)+')`')


async def checkid(id):
    detected = 0
    with open('./data/ids/ids.json', 'r') as g1:
        g = g1.read()
        data = json.loads(g)
        users = data['ids']
        for row in users:
            if row == id:
                detected = 1
        if detected == 0:
            return False
        if detected == 1:
            return True


async def getAccessToken():
    r = requests.post("https://id.twitch.tv/oauth2/token?client_id="+twitchid +
                      '&client_secret='+twitchsecret+'&grant_type=client_credentials')
    rjson = json.loads(r.text)
    return rjson['access_token']


async def main(id, display_name, ctx, data2019, data2020, data2021):
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
            with open('./data/'+str(file), 'r') as g:
                reader = csv.reader(g)
                detected = 0
                report_date = str(month)+'/'+str(year)
                for row in reader:
                    if row[0] == id:
                        detected = 1
                        if amount_count_s == 0:
                            yearog = str(year)
                            monthog = str(month)
                        amount_count_s = amount_count_s+1
                        amount_count = amount_count+1

                        # Values converted in cents before storage
                        ad_share_gross = int(float(row[2]) * 100)
                        sub_share_gross = int(float(row[3]) * 100)
                        bits_share_gross = int(float(row[4]) *100)
                        bits_developer_share_gross = int(float(row[5]) * 100)
                        bits_extension_share_gross = int(float(row[6]) * 100)
                        prime_sub_share_gross = int(float(row[7]) * 100)
                        bit_share_ad_gross = int(float(row[8]) * 100)
                        fuel_rev_gross = int(float(row[9]) * 100)
                        bb_rev_gross = int(float(row[10]) * 100)

                        # Adding values of same category
                        bits = bits_share_gross + bit_share_ad_gross + bits_developer_share_gross + bits_extension_share_gross
                        total = ad_share_gross + sub_share_gross + bits + prime_sub_share_gross + fuel_rev_gross + bb_rev_gross

                        # Calculating totals
                        grosstotal += total
                        adtotal += ad_share_gross
                        subtotal += sub_share_gross
                        bitstotal += bits
                        primestotal += prime_sub_share_gross

                        yeardata = [total, ad_share_gross, sub_share_gross,
                                    bits, prime_sub_share_gross, str(month), str(year)]

                        if year == "19":
                            data2019.append(yeardata)
                        if year == "20":
                            data2020.append(yeardata)
                        if year == "21":
                            data2021.append(yeardata)
                        await sendmsg(ctx, display_name, amount_count, countfiles)

            if detected == 0:
                amount_count = amount_count+1
                await senderr(ctx, display_name, amount_count, countfiles)

        except Exception as e:
            print(' -Revenue- ERR: '+str(e))

        #  Adding a blank month to year data.
        if detected == 0:
            yeardata = [0, 0, 0, 0, 0, str(month), str(year)]
            if year == "19":
                data2019.append(yeardata)
            if year == "20":
                data2020.append(yeardata)
            if year == "21":
                data2021.append(yeardata)

    return [grosstotal / 100, adtotal / 100, subtotal / 100, primestotal / 100, bitstotal / 100, monthog, yearog, data2019, data2020, data2021]


client = discord.Client()
header = []
all_total_gross = []
labels = ['08/19', '09/19', '10/19', '11/19', '12/19', '01/20', '02/20', '03/20', '04/20', '05/20', '06/20', '07/20', '08/20',
          '09/20', '10/20', '11/20', '12/20', '01/21', '02/21', '03/21', '04/21', '05/21', '06/21', '07/21', '08/21', '09/21', '10/21']

intents = discord.Intents.default()
activity = discord.Game(name="tw!info")
bot = commands.Bot(command_prefix='tw!', intents=intents,
                   activity=activity, status=discord.Status.online)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def check(ctx, username: str):
    username_before_api = username
    mainmsg = await ctx.send(content='`Checking '+username+'...`')
    id = ""
    if apichoice == 'helix':
        atoken = await getAccessToken()
        print(username)
        r = requests.get("https://api.twitch.tv/helix/users?login="+username_before_api.lower(),
                         headers={"Client-ID": twitchid, 'Authorization': 'Bearer '+atoken})
        rjson = json.loads(r.text)
        try:

            id = rjson['data'][0]["id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['data'][0]["profile_image_url"]
            bio = rjson['data'][0]["description"]
            created = rjson['data'][0]["created_at"]

        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken. (check your twitch tokens)')
            return

    if apichoice == 'kraken':
        print(username)
        r = requests.get("https://api.twitch.tv/kraken/users?login="+username_before_api.lower(),
                         headers={"Client-ID": twitchid, "Accept": "application/vnd.twitchtv.v5+json"})
        rjson = json.loads(r.text)
        try:

            id = rjson['users'][0]["_id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['users'][0]["logo"]
            bio = rjson['users'][0]["bio"]
            created = rjson['users'][0]["created_at"]

        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken.')
            return
    username_after_api = username
    idcheck = await checkid(id)
    if idcheck:
        time = datetime.datetime.utcnow()
        embed = discord.Embed(url="https://twitch.tv/{username}", title=f"Twitch Creator Info - {display_name} - ({username_after_api})",
                              description="`This user is in the leak!`", timestamp=time)

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                            str(bio)+'\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`"+str(created)+"`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        await mainmsg.edit(embed=embed, content="")
    if not idcheck:
        time = datetime.datetime.utcnow()
        embed = discord.Embed(url="https://twitch.tv/{username}", title=f"Twitch Creator Info - {display_name} - ({username})",
                              description="`This user is not in the leak!`", timestamp=time)

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                            str(bio)+'\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`"+str(created)+"`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        await mainmsg.edit(embed=embed, content="")


@bot.command()
async def revenue(ctx, username: str, *options: str):
    data2019 = []
    data2020 = []
    data2021 = []

    if apichoice == 'helix':
        atoken = await getAccessToken()
        print(username)
        r = requests.get("https://api.twitch.tv/helix/users?login="+username.lower(),
                         headers={"Client-ID": twitchid, 'Authorization': 'Bearer '+atoken})
        rjson = json.loads(r.text)
        try:

            id = rjson['data'][0]["id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['data'][0]["profile_image_url"]
            bio = rjson['data'][0]["description"]
            created = rjson['data'][0]["created_at"]

        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken. (check your twitch tokens)')
            return

    if apichoice == 'kraken':
        print(username)
        r = requests.get("https://api.twitch.tv/kraken/users?login="+username.lower(),
                         headers={"Client-ID": twitchid, "Accept": "application/vnd.twitchtv.v5+json"})
        rjson = json.loads(r.text)
        try:

            id = rjson['users'][0]["_id"]
            display_name = rjson['data'][0]["display_name"]
            logo = rjson['users'][0]["logo"]
            bio = rjson['users'][0]["bio"]
            created = rjson['users'][0]["created_at"]

        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken.')
            return

    idcheck = await checkid(id)
    if idcheck:
        mainmsg = await ctx.send('Data for '+display_name+' is loading... You will be pinged when the embed is sent!')
        thedata = await main(id, display_name, mainmsg, data2019, data2020, data2021)
        data2019 = thedata[7]
        data2020 = thedata[8]
        data2021 = thedata[9]
        month = thedata[5]
        year = thedata[6]
        time = datetime.datetime.utcnow()
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

        for list in data2019:
            totaldatagross.append(list[0])
            totaldataad.append(list[1])
            totaldatasub.append(list[2])
            totaldataprime.append(list[3])
            totaldatabits.append(list[4])

            total2019 += list[0]
            ad2019 += list[1]
            sub2019 += list[2]
            prime2019 += list[3]
            bits2019 += list[4]

        # conversion in $ 
        total2019 /= 100
        ad2019 /= 100
        sub2019 /= 100
        prime2019 /= 100
        bits2019 /= 100

        if total2019 == 0:
            data19 = "No data in 1920!"
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

        print(data2020)

        for list in data2020:
            totaldatagross.append(list[0])
            totaldataad.append(list[1])
            totaldatasub.append(list[2])
            totaldataprime.append(list[3])
            totaldatabits.append(list[4])

            total2020 += list[0]
            ad2020 += list[1]
            sub2020 += list[2]
            prime2020 += list[3]
            bits2020 += list[4]

        # conversion in $ 
        total2020 /= 100
        ad2020 /= 100
        sub2020 /= 100
        prime2020 /= 100
        bits2020 /= 100

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

        print(data2021)

        for list in data2021:
            totaldatagross.append(list[0] / 100)
            totaldataad.append(list[1] / 100)
            totaldatasub.append(list[2] / 100)
            totaldataprime.append(list[3] / 100)
            totaldatabits.append(list[4] / 100)

            total2021 += list[0]
            ad2021 += list[1]
            sub2021 += list[2]
            prime2021 += list[3]
            bits2021 += list[4]

        # conversion in $ 
        total2021 /= 100
        ad2021 /= 100
        sub2021 /= 100
        prime2021 /= 100
        bits2021 /= 100

        if total2021 == 0:
            data21 = "No data in 2120!"
        else:
            data21 = ':moneybag: Gross Total: ' + "`$" + str(
                "{:,}".format(total2021)) + " USD`\n" + ':tv: Ad Total: ' + "`$" + str(
                "{:,}".format(ad2021)) + " USD`\n" + ':star: Sub Total: ' + "`$" + str(
                "{:,}".format(sub2021)) + " USD`\n" + ':stars: Primers Total: ' + "`$" + str(
                "{:,}".format(prime2021)) + " USD`\n" + ':ice_cube: Bits Total: ' + "`$" + str(
                "{:,}".format(bits2021)) + " USD`"


        # Some graph related stuff
        if "nograph" not in options:
            import pyshorteners
            s = pyshorteners.Shortener()

            # format strings for pie graph
            gross_ads_str = f"${str(thedata[1])}"
            gross_subs_str = f"${str(thedata[2])}"
            gross_primes_str = f"${str(thedata[3])}"
            gross_bits_str = f"${str(thedata[1])}"

            pigraphurl = "{options:{title:{display:true,text:'Twitch Creator Data - "+display_name + \
                " - Pi Chart of Gross Payment', fontSize:20}},type:'pie',data:{labels:['Gross Ads', 'Gross Subs','Gross Prime','Gross Bits'],datasets:[{data:["+str(
                    thedata[1])+","+str(thedata[2])+","+str(thedata[3])+","+str(thedata[4])+"]}]}}"
            timelineurl = "{options:{title:{display:true,text:'Twitch Creator Data - "+display_name+" - Timeline of Gross Total', fontSize:20}},type:'line',data:{labels:" + \
                str(labels)+", datasets:[{label:'Gross Total', data: " + \
                str(totaldatagross)+", fill:false,borderColor:'blue'}]}}"
            bargraphurl = "{options:{title:{display:true,text:'Twitch Creator Data - " + display_name + "', fontSize:20}},type:'bar',data:{labels:" + str(labels) + ", datasets:[{label:'Gross Total', data: " + str(totaldatagross) + ", fill:false,borderColor:'blue'},{label:'Ads', data: " + str(
                totaldataad) + ", fill:false,borderColor:'green'},{label:'Subs', data: " + str(totaldatasub) + ", fill:false,borderColor:'yellow'},{label:'Prime', data: " + str(totaldataprime) + ", fill:false,borderColor:'red'},{label:'Bits', data: " + str(totaldatabits) + ", fill:false,borderColor:'orange'}]}}"

        embed = discord.Embed(
            title=f"Twitch Creator Info - {display_name} - ({username})", timestamp=time, url="https://twitch.tv/{username}")
        maindata = ':moneybag: Gross Total: '+"`$"+str("{:,}".format(thedata[0]))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(thedata[1]))+" USD`\n"+':star: Sub Total: '+"`$"+str(
            "{:,}".format(thedata[2]))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(thedata[3]))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(thedata[4]))+" USD`"
        embed.set_thumbnail(url=logo)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`"+str(created)+"`", inline=False)
        if bio:
            embed.add_field(name=':name_badge: Bio',
                            value='```\n'+str(bio)+'\n```', inline=False)
        embed.add_field(name="Data - Total `"+str(month)+'/' +
                        str(year)+"` - `10/21`", value=maindata, inline=False)
        embed.add_field(name="Data - 2019", value=str(data19), inline=True)
        embed.add_field(name="Data - 2020", value=str(data20), inline=True)
        embed.add_field(name="Data - 2021", value=str(data21), inline=True)

        # Some graph related stuff
        if "nograph" not in options:
            embed.add_field(name="Graphs", value="Timeline of Gross Total: "+s.tinyurl.short('https://quickchart.io/chart?c='+quote(timelineurl))+'\nBar Graph of split per month: ' +
                            s.tinyurl.short('https://quickchart.io/chart?c='+quote(bargraphurl))+'\nPi Chart of Gross Payment: '+s.tinyurl.short('https://quickchart.io/chart?c='+quote(pigraphurl)))

        # Exemple code to handle other options :
        # if "demo" in options:
        #     print("demo")
        #     embed.add_field(name= "Demo", value= "Demo", inline=False)

        embed.set_footer(text="Made by SSSEAL-C")
        await mainmsg.edit(content='<@'+str(ctx.author.id)+">", embed=embed)

    # Embed if user exists but not in the leak
    if not idcheck:
        time = datetime.datetime.utcnow()
        embed = discord.Embed(title=f"Twitch Creator Info - {display_name} - ({username})",
                              description="`This user is not in the leak!`", timestamp=time, url="https://twitch.tv/{username}")

        embed.set_thumbnail(url=logo)
        if bio:
            embed.add_field(name=':name_badge: Bio', value='```\n' +
                            str(bio)+'\n```', inline=False)
        embed.add_field(name=':alarm_clock: Created At',
                        value="`"+str(created)+"`", inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        mainmsg = await ctx.send(embed=embed)


@revenue.error
async def revenue_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send('You are not providing an argument! (eg. tw!revenue ludwig)')


@bot.command()
async def info(ctx):
    time = datetime.datetime.utcnow()
    embed = discord.Embed(title='Twitch Creator Info - Made by SSSEAL-C',
                          url="https://github.com/SSSEAL-C/twitch-leak-bot-discord", timestamp=time)
    embed.add_field(name=':busts_in_silhouette: Creators',
                    value='`realsovietseal#0001`', inline=False)
    embed.add_field(name=':gear: Commands',
                    value='```tw!revenue [twitch username] <option>\ntw!ping\ntw!info\ntw!check [twitch username]\n\neg. tw!revenue ludwig nograph```', inline=False)
    embed.add_field(name=':gear: Revenue Command Options',
                    value='`nograph`', inline=False)
    embed.add_field(name=':keyboard: Github',
                    value='`https://github.com/SSSEAL-C/twitch-leak-bot-discord`', inline=False)

    embed.set_footer(text="Made by SSSEAL-C")
    await ctx.send('<@'+str(ctx.author.id)+">", embed=embed)


@bot.command()
async def ping(ctx):
    embedVar = discord.Embed(title="Ping :ping_pong:")
    embedVar.add_field(name="Latency", value=str(
        round(bot.latency * 1000)+'ms'), inline=False)
    await ctx.send(embed=embedVar)

bot.run(dtoken)
