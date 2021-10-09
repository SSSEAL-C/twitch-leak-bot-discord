import csv
from os import listdir
from os.path import isfile, join
import requests
import json
import datetime
apichoice='helix' # use either helix or kraken
twitchid="twitch client id"
twitchsecret="twitch client secret" #only required for helix
dtoken='discord bot token'
async def sendmsg(ctx,username,amount_count,countfiles):
    await ctx.edit(content=':white_check_mark: `'+username+' data found! ('+str(amount_count)+'/'+str(countfiles)+')`')
async def senderr(ctx,username,amount_count,countfiles):
    await ctx.edit(content=':x: `'+username+' no data found! ('+str(amount_count)+'/'+str(countfiles)+')`')
async def check(id):
    try:
        detected=0
        with open('./data/ids/ids.json', 'r') as g1:
            g=g1.read()
            data=json.loads(g)
            users=data['ids']
            for row in users:
                if row == id:
                    detected=1
            if detected==0:
                return False
            if detected==1:
                return True
    except Exception as e:
        return e
async def getAccessToken():
    r=requests.post("https://id.twitch.tv/oauth2/token?client_id="+twitchid+'&client_secret='+twitchsecret+'&grant_type=client_credentials', headers={"Accept":"application/vnd.twitchtv.v5+json"})
    rjson=json.loads(r.text)
    return rjson['access_token']
async def main(id,username,ctx):
    
    grosstotal=0
    yearog="19"
    monthog="06"
    adtotal=0
    subtotal=0
    bitstotal=0
    primestotal=0
    amount_count=0
    amount_count_s=0
    onlyfiles = [f for f in listdir('./data/') if isfile(join('./data/', f))]
    countfiles=len(onlyfiles)
    for file in onlyfiles:
        filearr=file.split("_")
        year=filearr[2]
        month=filearr[3]
        month = month[:-4]
        try:
            with open('./data/'+str(file), 'r') as g:
                    reader = csv.reader(g)
                    detected=0
                    report_date = str(month)+'/'+str(year)
                    for row in reader:
                        if row[0] == id:
                            detected = 1
                            if amount_count_s == 0:
                                yearog=str(year)
                                monthog=str(month)
                            amount_count_s=amount_count_s+1
                            amount_count=amount_count+1
                            ad_share_gross = row[2]
                            sub_share_gross = row[3]
                            bits_share_gross = row[4]
                            bits_developer_share_gross = row[5]
                            bits_extension_share_gross = row[6]
                            prime_sub_share_gross = row[7]
                            bit_share_ad_gross = row[8]
                            fuel_rev_gross = row[9]
                            bb_rev_gross = row[10]
                            total=float(ad_share_gross)+float(sub_share_gross)+float(bits_share_gross)+float(prime_sub_share_gross)+float(bit_share_ad_gross)+float(fuel_rev_gross)+float(bb_rev_gross)
                            grosstotal=grosstotal+float(total)
                            adtotal=float(ad_share_gross)+adtotal
                            subtotal=subtotal+float(sub_share_gross)
                            bitstotal=bitstotal+float(bits_share_gross)+float(bits_developer_share_gross)+float(bits_extension_share_gross)
                            primestotal=primestotal+float(prime_sub_share_gross)
                            data=[ad_share_gross,sub_share_gross,bits_share_gross,bits_developer_share_gross,bits_extension_share_gross,prime_sub_share_gross,bit_share_ad_gross,fuel_rev_gross,bb_rev_gross,report_date,str(total),str(year)]
                            revenue_data.append(data)
                            await sendmsg(ctx,username,amount_count,countfiles)

                    if detected == 0:
                        amount_count=amount_count+1
                        await senderr(ctx,username,amount_count,countfiles)
        except Exception as e:
            print(' -Revenue- ERR: '+str(e))
    return [grosstotal,adtotal,subtotal,bitstotal,primestotal,monthog,yearog]

import discord
from discord.ext import commands
client=discord.Client()
revenue_data=[]
tax_data=[]
shortctr_data=[]
header=[]
all_total_gross=[]

intents = discord.Intents.default()
activity=discord.Game(name="tw!info")
bot = commands.Bot(command_prefix='tw!', intents=intents, activity=activity, status=discord.Status.online)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def revenue(ctx, username: str):
    if apichoice == 'helix':
        atoken=await getAccessToken()
        print(username)
        r=requests.get("https://api.twitch.tv/helix/users?login="+username.lower(), headers={"Client-ID":twitchid, "Accept":"application/vnd.twitchtv.v5+json",'Authorization': 'Bearer '+atoken})
        rjson=json.loads(r.text)
        try:
            id=rjson['data'][0]["id"]
            logo=rjson['data'][0]["profile_image_url"]
            bio=rjson['data'][0]["description"]
            created=rjson['data'][0]["created_at"]
        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken. (check your twitch tokens)')
            return
    if apichoice == 'kraken':
        print(username)
        r=requests.get("https://api.twitch.tv/kraken/users?login="+username.lower(), headers={"Client-ID":twitchid, "Accept":"application/vnd.twitchtv.v5+json"})
        rjson=json.loads(r.text)
        try:
            id=rjson['users'][0]["_id"]
            logo=rjson['users'][0]["logo"]
            bio=rjson['users'][0]["bio"]
            created=rjson['users'][0]["created_at"]
        except Exception as e:
            print(str(e))
            await ctx.send('This user does not exist or the API is broken.')
            return
    checkid=await check(id)
    if checkid == True:
        mainmsg = await ctx.send('Data for '+username+' is loading... You will be pinged when the embed is sent!')
        thedata=await main(id,username,mainmsg)
        month=thedata[5]
        year=thedata[6]
        time = datetime.datetime.utcnow()
        embed = discord.Embed(title='Twitch Creator Info - '+username,description="Data Timespan: `"+str(month)+'/'+str(year)+"` - `10/21`",timestamp=time)
        embed.set_thumbnail(url=logo)
        embed.add_field(name=':name_badge: Bio',value='```\n'+str(bio)+'\n```',inline=False)
        embed.add_field(name=':alarm_clock: Created At',value="`"+str(created)+"`",inline=False)
        embed.add_field(name=':moneybag: Gross Total', value="`$"+str("{:,}".format(round(thedata[0],2)))+" USD`",inline=True)
        embed.add_field(name=':tv: Ad Total', value="`$"+str("{:,}".format(round(thedata[1],2)))+" USD`",inline=True)
        embed.add_field(name=':star: Sub Total', value="`$"+str("{:,}".format(round(thedata[2],2)))+" USD`",inline=True)
        embed.add_field(name=':stars: Primers Total', value="`$"+str("{:,}".format(round(thedata[3],2)))+" USD`",inline=True)
        embed.add_field(name=':ice_cube: Bits Total', value="`$"+str("{:,}".format(round(thedata[4],2)))+" USD`",inline=True)
        embed.set_footer(text="Made by SSSEAL-C")
        await mainmsg.edit(content='<@'+str(ctx.author.id)+">",embed=embed)
    if checkid == False or checkid != True:
        time = datetime.datetime.utcnow()
        embed = discord.Embed(title='Twitch Creator Info - '+username,description="`This user is not in the leak!`",timestamp=time)
        embed.set_thumbnail(url=logo)
        embed.add_field(name=':name_badge: Bio',value='```\n'+str(bio)+'\n```',inline=False)
        embed.add_field(name=':alarm_clock: Created At',value="`"+str(created)+"`",inline=False)
        embed.set_footer(text="Made by SSSEAL-C")
        mainmsg = await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    time = datetime.datetime.utcnow()
    embed = discord.Embed(title='Twitch Creator Info - Made by SSSEAL-C', url="https://github.com/SSSEAL-C/twitch-leak-bot-discord",timestamp=time)
    embed.add_field(name=':busts_in_silhouette: Creators',value='`realsovietseal#0001`',inline=False)
    embed.add_field(name=':gear: Command Format',value='`tw!revenue [twitch username]`',inline=False)
    embed.add_field(name=':keyboard: Github',value='`https://github.com/SSSEAL-C/twitch-leak-bot-discord`',inline=False)
    embed.set_footer(text="Made by SSSEAL-C")
    await ctx.send('<@'+str(ctx.author.id)+">",embed=embed)


bot.run(dtoken)