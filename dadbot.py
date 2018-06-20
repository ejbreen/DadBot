# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 16:11:56 2018

@author: Evan
"""

import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import pickle



squads = ['hammer', 'gladius', 'nomads', 'opt_out']
zones = ['UTC','EST','CST','MT','AET']
offsets = [0, -5, -6, -7, 10]
time_zones = pd.DataFrame({'zone':zones, 'offset':offsets})


class corp:
    def __init__(self, dads = []):
        self.dads = dads
        self.hammer = []
        self.gladius = []
        self.nomads = []
        self.opt_out = []
        self.rockets = []
        self.rocket_timer = datetime.utcnow()
        
        self.__update__()
    
    def __find_by_ID__(self, userID):
        for d in self.dads:
            if d.userID == userID:
                return d
        return False
    
    def __update__(self):
        self.hammer = []
        self.gladius = []
        self.nomads = []
        self.opt_out = []
        self.rockets = []
        
        for d in self.dads:
            if d.squad == 'hammer':
                self.hammer.append(d)
            elif d.squad == 'gladius':
                self.gladius.append(d)
            elif d.squad == 'nomads':
                self.nomads.append(d)
            elif d.squad == 'opt_out':
                self.opt_out.append(d)
            if d.rockets:
                self.rockets.append(d)
    
    def list_dads(self):
        for d in self.dads:
            print(d.name)
    
    def add_a_dad(self, d):
        self.dads.append(d)
    
    def remove_a_dad(self, d):
        self.dads.pop()
    
    def new_WS(self):
        self.__update__()
    
    def find_dad(self, d):
        return self.__find_by_ID__(d)
    
    def next_salvo(self):
        return self.rocket_timer
    
    def who_is_free(self):
        free_dads = []
        for d in self.dads:
            if d.is_free():
                free_dads.append(d)
        return free_dads
    

class dad:
    def __init__(self, userID, name, timezone = 'EST', RSLevel = 5,
                 squad = 'opt_out', rockets = False):
        self.userID = userID
        self.name = name
        self.timezone = timezone
        self.squad = squad
        self.rockets = rockets
        self.rocketReady = False
        self.rocketReadyAt = datetime.utcnow() + timedelta(days = 1000)
        self.RSLevel = RSLevel
        self.freeUntil = datetime.utcnow() - timedelta(hours=2)
    
    def change_timezone(self, newZone):
        self.timezone = newZone
    
    def change_squad(self, squad):
        self.squad = squad
    
    def change_rockets(self, rockets):
        self.rockets = rockets
    
    def change_RSLevel(self, RSLevel):
        self.RSLevel = RSLevel
    
    def rocketSent(self):
        self.rocketReadyAt = datetime.utcnow() + timedelta(hours=2)
    
    def new_white_star(self, squad):
        self.squad = squad
        if self.rockets == True:
            self.rocketReadyAt = datetime.utcnow()
        else:
            self.rocketReadyAt = datetime.utcnow()+timedelta(days=1000)
    
    def ready_to_fire(self):
        if self.rockets:
            d = self.rocketReadyAt - datetime.utcnow()
            if d.days < 0:
                return('Ready to fire')
            else:
                s = "%s until ready"%(str(timedelta(minutes = 5)))
                return(s)
                
    def free_for(self, t):
        if type(t) == timedelta:
            self.freeUntil = datetime.utcnow() + t
    
    def is_free(self):
        d = self.freeUntil - datetime.utcnow()
        return(d.days>=0)
try:
    dadcorp = pickle.load(open('./dadcorp.p','rb'))
except:
    print('failed to load dadcorp')
    dadcorp = corp()


def save_state(dadcorp):
    pickle.dump(dadcorp, open('./dadcorp.p', 'wb'))
    

#dadcorp = pickle.load(open('./dadcorp.p','rb'))

#main token
token = "NDU1ODI2Nzg0NjM0NjY3MDA4.DgBpXQ.O7-auA1eh3OxEmiHpVqcIhd7438"

#test bot token
#token = ""

bot = commands.Bot(command_prefix='?')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name="?add_me || ?help_me"))
    
@bot.command(pass_context=True)
async def help_me(ctx):
    await bot.send_message(ctx.message.author, "Here's what I can do for you")
    await bot.send_message(ctx.message.author, "Commands:")  
    await bot.send_message(ctx.message.author, "?add_me - adds you to the bot's list of dads where it can track things like rs availability and other features coming soon")
    await bot.send_message(ctx.message.author, "?set_rs_level x - sets your maximum rs level to x")
    await bot.send_message(ctx.message.author, "?free_for x y - lets the bot know that you are up free for red star searches for x hours and y minutes")
    await bot.send_message(ctx.message.author, "?whos_free - lists the dads who are currently free for red star searches")
    await bot.send_message(ctx.message.author, "?ping_free - pings all of the dads who are free for red star searches")
#    await bot.send_message(ctx.message.author, "?who_am_i - idk man, who are you tho")
#    await bot.send_message(ctx.message.author, "?next_salvo - check when the next salvo of rockets is to be sent off")


@bot.command()
async def timezones():
    await bot.say(datetime.utcnow().strftime("%I:%M%p"))


@bot.command()
async def next_salvo():
    t = time_zones.copy()
    t['time'] = t.apply(lambda row: dadcorp.next_salvo() + timedelta(hours = row['offset']), axis = 1)
    t['localized time'] = t.apply(lambda row: row['time'].strftime('%d/%m %I:%M%p'), axis = 1)
    
    await bot.say(t.loc[:,['localized time','zone']].set_index('zone'))


@bot.command(pass_context=True)
async def who_am_i(ctx):
    print(ctx.message.author.mention)
    await bot.say(ctx.message.author.mention)


@bot.command()
async def echo(*, message: str):
    await bot.say(message)


@bot.command(pass_context=True)
async def add_me(ctx):
    if dadcorp.find_dad(ctx.message.author.mention)==False:
        print('adding %s, (%s) to dadcorp'%(ctx.message.author.display_name,ctx.message.author.mention))
        d = dad(ctx.message.author.mention, ctx.message.author.display_name)
        dadcorp.add_a_dad(d)
        await bot.say("%s added"%(d.name))
    else:
        await bot.say("No need, you're already on the roster")
    save_state(dadcorp)
   
@bot.command(pass_context=True)
async def set_rs_level(ctx, rs_level:int):
    d = dadcorp.find_dad(ctx.message.author.mention)
    d.change_RSLevel(rs_level)
    save_state(dadcorp)
    await bot.say("set %s's maximum RS level to %i"%(d.name, d.RSLevel))
     
@bot.command(pass_context=True)
async def free_for(ctx, hour:int, minute:int):
    d = dadcorp.find_dad(ctx.message.author.mention)
    d.free_for(timedelta(hours=hour, minutes=minute))
    save_state(dadcorp)
    await bot.say("Got it, %s's free for the next %i hours and %i minutes"%(d.name, hour, minute))
    
    
@bot.command()
async def whos_free(rs_level:int = 5):
    for d in dadcorp.who_is_free():
        if d.RSLevel >= rs_level:
            t = d.freeUntil - datetime.utcnow()
            await bot.say("%s (RS %i) is free for the next %d minutes"%(d.name, d.RSLevel, round(t.seconds/60)))
    await bot.say("If your max RS level is wrong, change with the ?set_rs_level command")

@bot.command()
async def ping_free(rs_level:int = 5):
    for d in dadcorp.who_is_free():
        if d.RSLevel >= rs_level:
            await bot.say("%s"%(d.userID))
    await bot.say("If your max RS level is wrong, change with the ?set_rs_level command")

@bot.command()
async def list_dads():
    for d in dadcorp.dads:
        await bot.say("%s, RS%i"%(d.name, d.RSLevel))

@bot.command()
async def die():
    await bot.logout()

bot.run(token)