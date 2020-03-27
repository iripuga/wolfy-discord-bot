global data
global game #this will be my main game dict in which all will happen - TA JE NUJNA, ostale niti ne tolk
game = []
global tableID 
tableID = [1, 2, 3] #ID od table slotov
global next_one #hranim ime vloge, ki je naslednja na vrsti
next_one = ''

import discord
from discord.ext.commands import Bot
import os
from dotenv import load_dotenv
from random import shuffle
from numpy import linspace
import werewolfes as ww
import json
import time

# heci
vic = 'Sprehajala sem se po Hoferju, pa je en kurac pred menoj celo paleto wc papirja vleko!!! Pa sem ga natulila in mu rekla "kaj vi samo serjete doma???" Pa mi je rekel: gospa jaz delam tukaj...'
'''
# Če bom hotu kake evente spreminjat moram bota definirat s tem razredom
class Custom(discord.Client):
    async def overridden_fun():
        return
'''




### BOT ##########################################################################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #password to get acces to login bot into discord
wolfy = Bot(command_prefix='.') #connection to discord bot, same and more than Client

# Which GUILD to use??? Guild je server v discord jeziku.
print('Which guild? ', end=' ')
server = input()
if server == 'NFA':
    GUILD = os.getenv('NFA')
    CHANNEL = 688744586293936296 #general
    TABLE = 691400770557444096  #table
else:
    #print('MG')
    GUILD = os.getenv('DISCORD_GUILD') #default GUILD is IoS
    CHANNEL = 690010969438421006  #general!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TOLE JE TREBA ŠE DAT V .env!!!
    TABLE = 690141479666188334  #table
GUILD = int(GUILD)
##################################################################################################



### FUNKCIJE #####################################################################################
def msg4user(player):
    #Funkcija sestavi sporočilo, ki ga ob začetku igre pošljem vsakemu uporabniku
    role = player['role']
    role_name = role.split(' ')[0]
    msg_role = f"👀\n{role} Go get \'em! 👋\n"
    
    return msg_role

async def msg4seer(message, game, wolfy):
    seer = ww.find_role_user(game, 'SEER', wolfy)
    table = wolfy.get_channel(TABLE)
    if seer != None:
        msg, _bljak = ww.list4role(game, 'SEER', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('SEER, open your 👀.')
        await seer.send(msg)


async def msg4robber(message, game, wolfy):
    robber = ww.find_role_user(game, 'ROBBER', wolfy)
    table = wolfy.get_channel(TABLE)
    if robber != None:
        msg, _bljak = ww.list4role(game, 'ROBBER', wolfy) #določim med kom lahko robber izbira
        await table.send('ROBBER, open your 👀.')
        await robber.send(msg)

async def msg4whos_next(message, game, wolfy, nightRole):
    '''
    Pošlje sporočilo igralcu, ki je naslednji na vrsti. Nič ne vrne zaenkrat.\n
    Input:
        message...objekt od uporabnika, ko pošlej sporočilo v kanal
        game...aktualna igra
        wolfy...ma bot
        nightRole...ime vloge, ki bi trenutno mogla bit na vrsti, type string
    '''
    if nightRole == 'WEREWOLF':
        pass    #zrihtano v .w
    elif nightRole == 'MINION':
        pass    #zrihtano v .w
    elif nightRole == 'MASON':
        pass    #zrihtano v .w
    elif nightRole == 'SEER':
        await msg4seer(message, game, wolfy)
    elif nightRole == 'ROBBER':
        await msg4robber(message, game, wolfy)
    elif nightRole == 'TROUBLEMAKER':
        await msg4robber(message, game, wolfy)
    elif nightRole == 'DRUNK':
        await msg4robber(message, game, wolfy)
    elif nightRole == 'INSOMNIAC':
        await msg4robber(message, game, wolfy)         
    else:
        raise ValueError(str(nightRole) + ' is not awake at night.')

    '''
                            DUMP
    #flags for function to know which roles were already inspected in dictionary order
    #print('msg4whos_next', night_role, order)
    villager = False;
    werewolf = False;
    minion = False;
    mason = False;
    seer = False;
    robber = False;
    
    #neccessary role numbers
    seerrole = 4
    robberrole = 5
    troublerole = 6
    drunkrole = 7
    insomniacrole = 8

    for role in order:
    '''
    return

async def safetyNet(player, user, nextRole, rolename):
    '''
    varovala, da samo igralci z vlogo dostopajo do ukazov vloge - e.g. samo robber lahko uporablja ukaze robberja\n
    Input:
        playersRole...string s podatki o aktualni vlogi
        user...discord objekt, ki ga določim z role_id, in ga uporabim za DM komunikacijo z uporabnikom
        nextRole...ime vloge, ki je trenutno na vrsti(string)
        rolename...katero vlogo varuje ta safetyNet
    Output:
        issafe...bool, ki pove če je user pravi in lahko uporablja ukaze vloge rolename
    '''
    issafe = False
    playersRole = player['role'].split(' ')[0]
    if (playersRole != rolename):                   #varovalni pogoji so na začetku
        print(player)
        await user.send('You are not ' + rolename + ', so cut it out.\nDumbkopf!')
    elif (playersRole == rolename) and (nextRole != rolename):  #če nisi na vrsti drugi pogoj ne velja
        await user.send('Not your turn buddy!')
    else:
        issafe = True   #če se nič zgoraj ne zgodi pol ukaz uporablja ta prava vloga, takrat ko je na vrsti
    return issafe

##################################################################################################


'''
#nč ne dela to!!!
@wolfy.command()
async def ping(ctx, *, message):
    #await wolfy.process_commands(message)
    await ctx.send(message)
'''




### LOGIN into guild ################################################################################
@wolfy.event   #@ je event handler - ko se vzpostavi povezava se izvede ta funkcija
async def on_ready():
    for guild in wolfy.guilds:      #Na katerem serverju sem in...
        if int(guild.id) == GUILD:
            break
    print(
        f'{wolfy.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    show_members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {show_members}')
    #await wolfy.channel.send('Hallo')
'''   
Enkrat mi bo ratal sporočilo za pozdrav - lahko je random nemška fraza iz seznama(http://streettalksavvy.com/street-talk-german-slang/german-slang-phrases/) 
Ne rabi bit sporočilo na začetku logina, lohk je sam ena fora, ki je sprogramirana v bota. Kličeš z eno frazo in bot odgovori iz random knjižnice nemških fraz.    
@wolfy.event
async def on_connect():
    await wolfy.channel.send('Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier') 
'''     
##################################################################################################







##################################################################################################
############################################## MAIN ##############################################
##################################################################################################
@wolfy.event
async def on_message(message):
    global data
    global game
    global tableID
    global next_one

    testgame = [{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'SEER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False}, 
                {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': 'ROBBER - The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win.', 'played':False}, 
                {'name': 'table_slot1', 'user_id': 1, 'status': 'on', 'role': 'TROUBLEMAKER - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
                {'name': 'table_slot2', 'user_id': 2, 'status': 'on', 'role': 'INSOMNIAC - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
                {'name': 'table_slot3', 'user_id': 3, 'status': 'on', 'role': 'DRUNK - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}]

### other COM stuff
    #-------------------------------------------------------------------------------------------#
    if message.author == wolfy.user:    # ignore bot messages in chat - tko se bot ne bo pogovarjal sam s sabo!
        return
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith('woof'):      # message for ping
        await message.channel.send('WoofWoof!')
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith('ustreli'):#rabim seznam vicev
        await message.channel.send(vic)        #prostor za zbirko vicev, fraz in podobnih stvari
    elif message.content.startswith('spam') or message.content.startswith('wolfy'):  #rabim seznam nempkih glupih fraz
        await message.channel.send('Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier') 
    #-------------------------------------------------------------------------------------------#
    elif message.content == '.logout':     # by wolfy - stops script
        await message.channel.send('Aufwiedersehen!')  
        await wolfy.close()
    elif message.content == '.id':  #vsak lahko izve svoj id
        your_id = message.author.id
        user = wolfy.get_user(your_id)
        await user.send('Your ID is: ' + str(your_id))
    #-------------------------------------------------------------------------------------------#
    
### WEREWOLFES GAME
    #-------------------------------------------------------------------------------------------#
    elif message.content == '.s':
        #Tole je za vpis/izpis iz igre - menjava statusa v glavnem slovarju
        user_id = message.author.id
        nickname = message.author.name
        klik = ww.change_status(data, user_id)        #menjava statusa
        #with open('.game_data.json', 'w', encoding='utf-8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)
        msg = nickname + ' status: ' + klik
        await message.channel.send(str(msg))   

### .w START GAME - send msg to players
    elif message.content == '.w':
        #global CHANNEL in bi tja vse pošiljal...detajli
        await message.channel.send('...erewolfes?')     
        #Uvozim json podatke o igri in igralcih
        data = json.load(open('.game_data.json', 'r'))
        
        #for i in range(len(game)):
        #    game.pop()
        game = testgame #ww.assign_roles(data)  #dobim list vseh članov, ki so v igri
        #print(game)
        nextRole = None   #ni še noč, villager itak spi
        
        #adding nicknames
        justroles = ww.list_active_roles(game)  #katere vloge so v igri
        msg = 'New game - active roles:\n' + justroles + '\nassigning roles...\n'
        await message.channel.send(msg) 
        time.sleep(1);

        for player in game:
            playerID = player['user_id']
            playersRole = player['role'].split(' ')[0]
            #TUKI GRE FUNKCIJA ZA ŠTETJE MASONOV, če je samo eden moram zamenjat vloge
            if playerID in tableID:
                print('table#' + str(playerID)+ ' ' +str(player['role'].split(' ')[0]))  #skip tables
            else:   
                user = wolfy.get_user(playerID)      #user - samo njemu pošiljam sporočila v tej iteraciji for zanke
                print(user.name, player['role'].split(' ')[0])
                init_msg = msg4user(player) #lovrič me je blokiral!!! no_hello ne morem pošiljat
                await user.send(init_msg)   #sporočim vsakemu igralcu njegovo vlogo/karto

### .w NIGHT GAME - for static roles to know each other 
                if playersRole == 'VILLAGER':
                    player['played'] = True #nothing happens - just to make sure, that nothing happens
                elif playersRole == 'WEREWOLF': 
                    flag = False
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in tableID)):
                            werewolf = wolfy.get_user(player_i['user_id']);
                            if werewolf != user:
                                flag = True
                                await user.send(f' - {werewolf.name} is a WEREWOLF')  #POVEM KDO JE WEREWOLF                       
                    if not flag:
                        await user.send('\nYou are the only WEREWOLF') 
                    player['played'] = True
                elif playersRole == 'MINION':
                    flag = False #da vem, če sem našel kakega volkodlaka
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in tableID)):
                            flag = True
                            werewolf = wolfy.get_user(player_i['user_id']);
                            await user.send(f' - {werewolf.name} is a WEREWOLF')  #POVEM KDO JE WEREWOLF
                    if not flag:
                        await user.send('\nYou have no friends or WEREWOLFES, MINION\nhahaha...little piece of shit, Dumbkopf!')
                    player['played'] = True
                elif playersRole == 'MASON': #MASON numbers taken care of in function ww.assigned_roles()
                    flag = False #davem, če sem našel kakega masona
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'MASON') and (not (player_i['user_id'] in tableID)):
                            mason = wolfy.get_user(player_i['user_id']);
                            if mason != user:
                                flag = True
                                await user.send(f' - {mason.name} is a MASON')
                    if not flag:
                        await user.send('\nYou are the only MASON')
                    #player['played'] = True  #to se bo zgodilo v funkciji whos_next

        #send message to next role - his turn 
        next_one = ww.whos_next(game, data); #0-villager, 1-werewolf, 2-minion, 3-mason so zrihtani. Kdo je naslednji?
        await msg4whos_next(message, game, wolfy, next_one)
        print('.w',next_one)

###  NIGHT GAME - for dynamic roles to change game cards
    #Za vsako dinamično vlogo posebej glede na night_order...če igralec ni ta vloga ga Wolfy ignorira
    elif message.content.startswith('seer'):      ### SEER
        print('seer-start:',next_one)
        id_seer = message.author.id
        seer = wolfy.get_user(id_seer)
        _bljak, players4seer = ww.list4role(game, 'SEER', wolfy) #_bljak is list4msg, which we don't need anymore, but still need for function output
        #print(players4seer)
        if not game:                                            
            await seer.send('The game hasn\'t started yet.')
        else:
            for player in game:
                playersRole = player['role'].split(' ')[0]
                safe = await safetyNet(player, seer, next_one, 'SEER') #da še kdo drug kot prava vloga ne izvaja ukazov
                if not safe:
                    break
                else:   #past the safetyNet - user je definitivno seer
                    last = message.content[-1]
                    if last not in ['0','1','2','3','4','5','6','7','8','9']:    #če je sploh vnesena številka
                        await seer.send('Well done! Somehow you fucked up...');
                    else:
                        looknum = int(message.content.split('-')[1])    #kjero cifro si zbral
                        if looknum == 0: 
                            await seer.send('It\'s your choice') #seer-pass
                        elif len(str(looknum)) == 1: #ko vpišeš eno številko - to je če hočeš videt playerja
                            if looknum not in players4seer.keys():
                                await seer.send('Well done! Somehow you fucked up...'); #pass #If you fuck up the seer number we move on
                            else:
                                await seer.send('You will see in a minute ;) - ' + str(looknum))
                        elif len(str(looknum)) == 2:#dve številki za mizo
                            await seer.send('You will see in a minute ;) - ' + str(looknum))
                        else:
                            await seer.send('Well done! Somehow you fucked up...'); #If you fuck up input number we move on
                    #send message to robber - his turn 
                    next_one = ww.whos_next(game, data);
                    await msg4whos_next(message, game, wolfy, next_one)
                    break
        print('seer-end:', next_one)
                        
        
    elif message.content.startswith('robber'):    ### ROBBER
        #varovala gredo lohk v funkcijo safety_net(message, game, next_one), napisana tko da se lohk večkrat uporabijo
        print('robber', next_one)                                                                            
        id_robber = message.author.id
        robber = wolfy.get_user(id_robber);
        robberatnight = 5
        _bljak, players4role = ww.list4role(game, 'ROBBER', wolfy)
        if not game:                 
            await robber.send('The game hasn\'t started yet.')
        else:
            for player in game:
                playersRole = player['role'].split(' ')[0]
                safe = await safetyNet(player, robber, next_one, 'ROBBER') #da še kdo drug kot robber ne izvaja ukazov
                if not safe:
                    break
                else:   #past the safetyNet
                    victim = int(message.content.split('-')[1]);  #koga bomo oropal
                    if (playersRole == 'ROBBER') and (victim == 0) and (next_one == robberatnight):
                        await robber.send('It\'s your choice') #robber-pass
                    elif (playersRole == 'ROBBER') and (next_one == robberatnight):
                        if victim not in players4role.keys():
                            next_one = 6
                            await seer.send('Well done! Somehow you fucked up...');   #If you fuck up the victim number we move on
                            break
                        else:
                            id_victim = players4role[victim] #določim kdo je to v igri

                        game, switch_msg = ww.switch(game, id_robber, id_victim)   #rob the victim
                        print('ROBBER', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        #game = list(game) in case game becomes tuple somehow???
                        for player_i in game:
                            if player_i['user_id'] == id_robber:
                                new_role = player['role']
                                msg = 'Great! You are now ' + new_role
                                await robber.send(msg)
                                break
                        
                    next_one = ww.whos_next(game, data);
                    await msg4whos_next(message, game, wolfy, order, next_one)  
                    break
        print('robber',next_one)
        '''
        else:
            
        '''

    if message.content.startswith('troublemaker'):
        pass

    if message.content.startswith('drunk'):
        pass

    if message.content.startswith('insomniac'):
        pass

### JOKE commands for roles with no dynamic night function ###
    if message.content.startswith('hunter'):
        pass

    if message.content.startswith('tanner'):
        pass

    if message.content.startswith('villager'):
        pass

    if message.content.startswith('werewolf'):
        pass

    if message.content.startswith('minion'):
        pass

    if message.content.startswith('mason'):
        pass

###  MID GAME - Wolfy waits for players to discuss who to kill  #########
    #detajli

###  VOTING - Players send private message to Wolfy  ####################
    elif message.content == '.vote':
        pass

###  END GAME - who died, Wolfy reveals all the cards  ##################
    elif message.content == '.end':
        try:
            ### glavno sporočilo za vse ###
            stupid_test = game[0]   #just to call game before sending any message
            table = wolfy.get_channel(TABLE)
            await table.send('GAME OVER\n\n')
            
            #v channel #table prikažem kdo je bil kdo 
            table_cards = ''
            for player in game:
                playerID = player['user_id']
                user = wolfy.get_user(playerID)
                #show table cards
                if playerID in tableID:
                    role_name = player['role'].split(' ')[0]
                    table_cards = table_cards + '\n' + role_name
                else:
                    player_name = user.name
                    role_name = player['role'].split(' ')[0]
                    msg = ' - ' + player_name + ' was ' + role_name
                    await table.send(msg)
            
            msg = '\nTable cards were: ' + table_cards
            await table.send(msg)
        except:
            table = wolfy.get_channel(TABLE)
            await table.send('The game hasn\'t started yet.')

###  CHEAT CODES ###
    elif message.content == '.wolfy #iwannawin': #to bo na konc drugačen klic - GAME OVER
        loosers = ww.list_active_id(game)
        winner_name = message.author.name
        winner_id = message.author.id
        #dobim aktualen seznam igralcev, ki igrajo in njihove vloge
        
        for looser in loosers:
            if looser == winner_id:
                #for the winner
                user = wolfy.get_user(winner_id)
                await user.send('You win by cheating. Shame on you!!!')
                time.sleep(1)
                await user.send('Dumbkopf!')
            else:
                #loosers punishment
                user = wolfy.get_user(looser)
                await user.send('HAHAHA, you lost!\nhttps://www.youtube.com/watch?v=GLsVWEi7BoM')    
    else:
        pass #raise ValueError('Command "' + message.content + '" not received or nonexistent.')  #če je karkoli druzga
#run everything
wolfy.run(TOKEN)














'''
NOBENA KOMANDA NE DELA!?      in niimam pojma zakva!  
        
@wolfy.command(name = 'werewolfes')
async def wolfs(ctx):
    await ctx.send('55') 
        
@wolfy.command(name='99')
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]
    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    
@wolfy.command() #define the first command and set prefix to '!'
async def testt(ctx):
    await ctx.send('Hello!!')
# PRIVATE COMMUNICATION with members
        await message.author.send('👋')   #Tut dela, sam ni primerna za mojo aplikacijo
'''