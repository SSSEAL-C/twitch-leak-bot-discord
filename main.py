import csv
from os import listdir
from os.path import isfile, join
import requests
import json
twitchid="twitch client id here"
dtoken='discord token here'
async def sendmsg(ctx,username,amount_count,countfiles):
    await ctx.edit(content=':white_check_mark: `'+username+' data found! ('+str(amount_count)+'/'+str(countfiles)+')`')
async def senderr(ctx,username,amount_count,countfiles):
    await ctx.edit(content=':x: `'+username+' no data found! ('+str(amount_count)+'/'+str(countfiles)+')`')
async def main(id,username,ctx):
    
    grosstotal=0
    yearog=""
    monthog=""
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
description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()

bot = commands.Bot(command_prefix='tw!', description=description, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def revenue(ctx, username: str):
    r=requests.get("https://api.twitch.tv/kraken/users?login="+username.lower(), headers={"Client-ID":twitchid, "Accept":"application/vnd.twitchtv.v5+json"})
    rjson=json.loads(r.text)
    try:
        id=rjson['users'][0]["_id"]
        logo=rjson['users'][0]["logo"]
        bio=rjson['users'][0]["bio"]
        created=rjson['users'][0]["created_at"]
    except:
        await ctx.send('This user does not exist or the API is broken.')
        return
    mainmsg = await ctx.send('Data for '+username+' is loading... You will be pinged when the embed is sent!')
    thedata=await main(id,username,mainmsg)
    month=thedata[5]
    year=thedata[6]
    embed = discord.Embed(title='Twitch Creator Info - '+username,description="Data Timespan: `"+str(month)+'/'+str(year)+"` - `10/21`")
    embed.set_thumbnail(url=logo)
    embed.add_field(name=':name_badge: Bio',value='```\n'+str(bio)+'\n```',inline=False)
    embed.add_field(name=':alarm_clock: Created At',value="`"+str(created)+"`",inline=False)
    embed.add_field(name=':moneybag: Gross Total', value="`$"+str("{:,}".format(round(thedata[0],2)))+" USD`",inline=True)
    embed.add_field(name=':tv: Ad Total', value="`$"+str("{:,}".format(round(thedata[1],2)))+" USD`",inline=True)
    embed.add_field(name=':star: Sub Total', value="`$"+str("{:,}".format(round(thedata[2],2)))+" USD`",inline=True)
    embed.add_field(name=':stars: Primers Total', value="`$"+str("{:,}".format(round(thedata[3],2)))+" USD`",inline=True)
    embed.add_field(name=':ice_cube: Bits Total', value="`$"+str("{:,}".format(round(thedata[4],2)))+" USD`",inline=True)
    await mainmsg.edit(content='<@'+str(ctx.author.id)+">",embed=embed)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title='Twitch Creator Info - Made by SSSEAL-C')
    embed.add_field(name=':busts_in_silhouette: Creators',value='`realsovietseal#0001`',inline=False)
    embed.add_field(name=':gear: Command Format',value='`tw!revenue [twitch username]`',inline=False)
    await ctx.send('<@'+str(ctx.author.id)+">",embed=embed)

bot.run(dtoken)