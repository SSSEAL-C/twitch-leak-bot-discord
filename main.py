import csv
from os import listdir
from os.path import isfile, join
import requests
import json
import datetime
time = datetime.datetime.utcnow()
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
async def main(id,username,ctx,data2019,data2020,data2021):
    
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
                            bits=float(bits_share_gross)+float(bit_share_ad_gross)
                            total=float(ad_share_gross)+float(sub_share_gross)+float(bits_share_gross)+float(prime_sub_share_gross)+float(bit_share_ad_gross)+float(fuel_rev_gross)+float(bb_rev_gross)
                            grosstotal=grosstotal+float(total)
                            adtotal=float(ad_share_gross)+adtotal
                            subtotal=subtotal+float(sub_share_gross)
                            bitstotal=bitstotal+float(bits_share_gross)+float(bits_developer_share_gross)+float(bits_extension_share_gross)
                            primestotal=primestotal+float(prime_sub_share_gross)
                            yeardata=[total,ad_share_gross,sub_share_gross,bits,prime_sub_share_gross,str(month),str(year)]
                            data=[ad_share_gross,sub_share_gross,bits_share_gross,bits_developer_share_gross,bits_extension_share_gross,prime_sub_share_gross,bit_share_ad_gross,fuel_rev_gross,bb_rev_gross,report_date,str(total),str(year)]
                            if year == "19":
                                data2019.append(yeardata)
                            if year == "20":
                                data2020.append(yeardata)
                            if year == "21":
                                data2021.append(yeardata)
                            revenue_data.append(data)
                            await sendmsg(ctx,username,amount_count,countfiles)

                    if detected == 0:
                        amount_count=amount_count+1
                        await senderr(ctx,username,amount_count,countfiles)
        except Exception as e:
            print(' -Revenue- ERR: '+str(e))
    return [grosstotal,adtotal,subtotal,bitstotal,primestotal,monthog,yearog,data2019,data2020,data2021]

import discord
from discord.ext import commands
from urllib.parse import quote
client=discord.Client()
revenue_data=[]
header=[]
all_total_gross=[]
labels=['08/19','09/19','10/19','11/19','12/19','01/20','02/20','03/20','04/20','05/20','06/20','07/20','08/20','09/20','10/20','11/20','12/20','01/21','02/21','03/21','04/21','05/21','06/21','07/21','08/21','09/21','10/21']

intents = discord.Intents.default()
activity=discord.Game(name="tw!info")
bot = commands.Bot(command_prefix='tw!', intents=intents, activity=activity, status=discord.Status.online)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def revenue(ctx, username: str, graph: str):
    if username is str:
        return await ctx.send('You must specfiy a username!')
    if graph is str:
        return await ctx.send('You must specfiy yes or no for the graph!')
    data2019=[]
    data2020=[]
    data2021=[]
    if apichoice == 'helix':
        atoken=await getAccessToken()
        print(username)
        r=requests.get("https://api.twitch.tv/helix/users?login="+username.lower(), headers={"Client-ID":twitchid, 'Authorization': 'Bearer '+atoken})
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
        thedata=await main(id,username,mainmsg,data2019,data2020,data2021)
        data2019=thedata[7]
        data2020=thedata[8]
        data2021=thedata[9]
        month=thedata[5]
        year=thedata[6]
        time = datetime.datetime.utcnow()
        data19=""
        data20=""
        data21=""
        totaldatagross=[]
        totaldataad=[]
        totaldatasub=[]
        totaldatabits=[]
        totaldataprime=[]
        if data2019 == []:
            data19="No data in 2019!"
            i=5
            for l in range(i):
                totaldatagross.append(0)
                totaldataad.append(0)
                totaldatasub.append(0)
                totaldataprime.append(0)
                totaldatabits.append(0)
        if data2019 != []:
            total2019=0
            ad2019=0
            sub2019=0
            prime2019=0
            bits2019=0
            for list in data2019:
                totaldatagross.append(float(list[0]))
                totaldataad.append(float(list[1]))
                totaldatasub.append(float(list[2]))
                totaldataprime.append(float(list[3]))
                totaldatabits.append(float(list[4]))
                total2019=total2019+float(list[0])
                ad2019=ad2019+float(list[1])
                sub2019=sub2019+float(list[2])
                prime2019=prime2019+float(list[3])
                bits2019=bits2019+float(list[4])
            data19=':moneybag: Gross Total: '+"`$"+str("{:,}".format(round(total2019,2)))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(round(ad2019,2)))+" USD`\n"+':star: Sub Total: '+"`$"+str("{:,}".format(round(sub2019,2)))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(round(prime2019,2)))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(round(bits2019,2)))+" USD`"
        if data2020 == []:
            data20="No data in 2020!"
            i=12
            for l in range(i):
                totaldatagross.append(0)
                totaldataad.append(0)
                totaldatasub.append(0)
                totaldataprime.append(0)
                totaldatabits.append(0)
        if data2020 != []:
            total2020=0
            ad2020=0
            sub2020=0
            prime2020=0
            bits2020=0
            for list in data2020:
                totaldatagross.append(float(list[0]))
                totaldataad.append(float(list[1]))
                totaldatasub.append(float(list[2]))
                totaldataprime.append(float(list[3]))
                totaldatabits.append(float(list[4]))
                total2020=total2020+float(list[0])
                ad2020=ad2020+float(list[1])
                sub2020=sub2020+float(list[2])
                prime2020=prime2020+float(list[3])
                bits2020=bits2020+float(list[4])
            data20=':moneybag: Gross Total: '+"`$"+str("{:,}".format(round(total2020,2)))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(round(ad2020,2)))+" USD`\n"+':star: Sub Total: '+"`$"+str("{:,}".format(round(sub2020,2)))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(round(prime2020,2)))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(round(bits2020,2)))+" USD`"
        if data2021 == []:
            data21="No data in 2021!"
            i=10
            for l in range(i):
                totaldatagross.append(0)
                totaldataad.append(0)
                totaldatasub.append(0)
                totaldataprime.append(0)
                totaldatabits.append(0)
        if data2021 != []:
            total2021=0
            ad2021=0
            sub2021=0
            prime2021=0
            bits2021=0
            for list in data2021:
                totaldatagross.append(float(list[0]))
                totaldataad.append(float(list[1]))
                totaldatasub.append(float(list[2]))
                totaldataprime.append(float(list[3]))
                totaldatabits.append(float(list[4]))
                total2021=total2021+float(list[0])
                ad2021=ad2021+float(list[1])
                sub2021=sub2021+float(list[2])
                prime2021=prime2021+float(list[3])
                bits2021=bits2021+float(list[4])
            data21=':moneybag: Gross Total: '+"`$"+str("{:,}".format(round(total2021,2)))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(round(ad2021,2)))+" USD`\n"+':star: Sub Total: '+"`$"+str("{:,}".format(round(sub2021,2)))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(round(prime2021,2)))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(round(bits2021,2)))+" USD`"
        import pyshorteners

        s = pyshorteners.Shortener()
        timelineurl="{options:{title:{display:true,text:'Twitch Creator Data - "+username+"', fontSize:20}},type:'line',data:{labels:"+str(labels)+", datasets:[{label:'Gross Total', data: "+str(totaldatagross)+", fill:false,borderColor:'blue'}]}}"
        bargraphurl="{options:{title:{display:true,text:'Twitch Creator Data - "+username+"', fontSize:20}},type:'bar',data:{labels:"+str(labels)+", datasets:[{label:'Gross Total', data: "+str(totaldatagross)+", fill:false,borderColor:'blue'},{label:'Gross Ads', data: "+str(totaldatagross)+", fill:false,borderColor:'green'},{label:'Gross Subs', data: "+str(totaldatasub)+", fill:false,borderColor:'yellow'},{label:'Gross Prime', data: "+str(totaldataprime)+", fill:false,borderColor:'red'},{label:'Gross Bits', data: "+str(totaldatabits)+", fill:false,borderColor:'orange'}]}}"
        embed = discord.Embed(title='Twitch Creator Info - '+username,timestamp=time)
        maindata=':moneybag: Gross Total: '+"`$"+str("{:,}".format(round(thedata[0],2)))+" USD`\n"+':tv: Ad Total: '+"`$"+str("{:,}".format(round(thedata[1],2)))+" USD`\n"+':star: Sub Total: '+"`$"+str("{:,}".format(round(thedata[2],2)))+" USD`\n"+':stars: Primers Total: '+"`$"+str("{:,}".format(round(thedata[3],2)))+" USD`\n"+':ice_cube: Bits Total: '+"`$"+str("{:,}".format(round(thedata[4],2)))+" USD`"
        embed.set_thumbnail(url=logo)
        embed.add_field(name=':alarm_clock: Created At',value="`"+str(created)+"`", inline=False)
        embed.add_field(name=':name_badge: Bio',value='```\n'+str(bio)+'\n```',inline=False)
        embed.add_field(name="Data - Total `"+str(month)+'/'+str(year)+"` - `10/21`", value=maindata,inline=False)
        embed.add_field(name="Data - 2019", value=str(data19),inline=True)
        embed.add_field(name="Data - 2020", value=str(data20),inline=True)
        embed.add_field(name="Data - 2021", value=str(data21),inline=True)
        if graph == "yes":
            embed.add_field(name="Graphs",value="Gross Total: "+s.tinyurl.short('https://quickchart.io/chart?c='+quote(timelineurl))+'\nAll Values: '+s.tinyurl.short('https://quickchart.io/chart?c='+quote(bargraphurl)))
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
    embed.add_field(name=':gear: Command Format',value='`tw!revenue [twitch username] <graph? (yes/no)>` (eg. `tw!revenue ludwig yes`)',inline=False)
    embed.add_field(name=':keyboard: Github',value='`https://github.com/SSSEAL-C/twitch-leak-bot-discord`',inline=False)
    embed.set_footer(text="Made by SSSEAL-C")
    await ctx.send('<@'+str(ctx.author.id)+">",embed=embed)


bot.run(dtoken)