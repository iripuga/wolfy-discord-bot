###   TODO  ###
# - ko zajebe mu vrnem error message
# - rabim funkcijo errorHandler
# # # # # # # #

global data #.game_data.json
global game #this will be my main game dict in which all will happen - TA JE NUJNA, ostale niti ne tolk
global next_one #hranim ime vloge, ki je naslednja na vrsti - tut nujno
global CHANNEL #kanal v katerem igralci igrajo
game = []
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

### heci... ################################################################################
vic = 'Sprehajala sem se po Hoferju, pa je en kurac pred menoj celo paleto wc papirja vleko!!! Pa sem ga natulila in mu rekla "kaj vi samo serjete doma???" Pa mi je rekel: gospa jaz delam tukaj...'
'''
# Če bom hotu kake evente spreminjat moram bota definirat s tem razredom
class Custom(discord.Client):
    async def overridden_fun():
        return
'''
errors = ['Mission failed succesfully!',  #za tiste, ki ne znajo vnašat wolfy ukaze - izbiram random
            'Well done! Somehow you fucked up...',
            'As\' si mau duška dau?!',
            'Ma goni se!',
            'Bemti nanule, kristusove opanke...',
            'Pišuka Polde, ni to prava komanda']
specialError = ['Prideta Mujo in Haso...', '...pa ti rečeta: "Ajoj, baš ne znaš komandirat, jarane."']  #najprej prvi msg, počakam 3s, pošljem drugi error

'''   
Enkrat mi bo ratal sporočilo za pozdrav - lahko je random nemška fraza iz seznama(http://streettalksavvy.com/street-talk-german-slang/german-slang-phrases/) 
Ne rabi bit sporočilo na začetku logina, lohk je sam ena fora, ki je sprogramirana v bota. Kličeš z eno frazo in bot odgovori iz random knjižnice nemških fraz.    
@wolfy.event
async def on_connect():
    await wolfy.channel.send('Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier') 
''' 
#############################################################################################



### BOT ##########################################################################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #password to get acces to login bot into discord
wolfy = Bot(command_prefix='.') #connection to discord bot, same and more than Client

# Which GUILD to use??? Guild je server v discord jeziku. Za nov server moraš v server najprej prijavit bota preko developers strani
print('Which guild? ', end=' ')
server = input()
if server == 'NFA':
    GUILD = os.getenv('NFA')
elif server == 'w':
    GUILD = os.getenv('WoofServer')
else:
    GUILD = os.getenv('MaGuilt') #default GUILD is MG
GUILD = int(GUILD)
##################################################################################################



### FUNKCIJE #####################################################################################
def msg4user(player):
    #Funkcija sestavi sporočilo, ki ga ob začetku igre pošljem vsakemu uporabniku
    playername = player['name']
    role = player['role']
    rolename = role.split(' ')[0]
    if playername == 'zorkoporko':
        emoji = {'villager':':neutral_face:',
                'werewolf':':wolf:',
                'minion':':smiling_imp:',
                'mason':':police_officer:',
                'seer':':eye:',
                'robber':':detective:',
                'troublemaker':':performing_arts:',
                'drunk':':tumbler_glass:',
                'insomniac':':man_in_manual_wheelchair:',
                'hunter':':gun:',
                'tanner':':poop:'}
    else:
        emoji = {'villager':':neutral_face:',
                'werewolf':':wolf:',
                'minion':':smiling_imp:',
                'mason':':police_officer:',
                'seer':':eye:',
                'robber':':detective:',
                'troublemaker':':performing_arts:',
                'drunk':':beers:',
                'insomniac':':sleeping_accommodation:',
                'hunter':':gun:',
                'tanner':':poop:'}

    msg_role = f"{emoji[rolename.lower()]} {role} Go get \'em!\n"  #:muscle:
    
    return msg_role

async def msg4seer(message, game, channel, wolfy):
    seer = ww.findUser(game, wolfy, 'SEER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if seer != None:
        msg, _bljak = ww.list4role(game, 'SEER', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('SEER, open your  👀')
        await seer.send(msg)

async def msg4robber(message, game, channel, wolfy):
    robber = ww.findUser(game, wolfy, 'ROBBER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if robber != None:
        msg, _bljak = ww.list4role(game, 'ROBBER', wolfy) #določim med kom lahko robber izbira
        await table.send('ROBBER, open your  👀')
        await robber.send(msg)

async def msg4troublemaker(message, game, channel, wolfy):
    troublemaker = ww.findUser(game, wolfy, 'TROUBLEMAKER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if troublemaker != None:
        msg, _bljak = ww.list4role(game, 'TROUBLEMAKER', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('TROUBLEMAKER, open your  👀')
        await troublemaker.send(msg)

async def msg4drunk(message, game, channel, wolfy):
    drunk = ww.findUser(game, wolfy, 'DRUNK', method='by_rolename')
    table = wolfy.get_channel(channel)
    if drunk != None:
        msg, _bljak = ww.list4role(game, 'DRUNK', wolfy) #določim med kom lahko drunk izbira, _bljak ne rabim
        await table.send('DRUNK, open your  👀')
        await drunk.send(msg)

async def msg4insomniac(message, game, channel, wolfy):
    insomniac = ww.findUser(game, wolfy, 'INSOMNIAC', method='by_rolename')
    table = wolfy.get_channel(channel)
    if insomniac != None:
        msg, _bljak = ww.list4role(game, 'INSOMNIAC', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('INSOMNIAC, open your  👀')
        await insomniac.send(msg)

async def msg4whos_next(message, game, channel, wolfy, nightRole):
    '''
    Pošlje sporočilo igralcu, ki je naslednji na vrsti. Nič ne vrne zaenkrat.\n
    Input:
        message...objekt od uporabnika, ko pošlej sporočilo v kanal
        game...aktualna igra
        channel...kanal v katerem se igra. Tja grejo sporočila za vse.
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
        await msg4seer(message, game, channel, wolfy)
    elif nightRole == 'ROBBER':
        await msg4robber(message, game, channel, wolfy)
    elif nightRole == 'TROUBLEMAKER':
        await msg4troublemaker(message, game, channel, wolfy)  #await msg4robber(message, game, wolfy)
    elif nightRole == 'DRUNK':
        await msg4drunk(message, game, channel, wolfy)
    elif nightRole == 'INSOMNIAC':
        await msg4insomniac(message, game, channel, wolfy)       
    elif nightRole == None:  #Ko noben več ni na vrsti
        table = wolfy.get_channel(channel)
        await table.send('```yaml\nEverybody, open your  👀\n```')
    else:
        raise ValueError(str(nightRole) + ' is not awake at night.')
    return

async def safetyNet(game, user, currentRole, role2protect):
    '''
    varovala, da samo igralci z vlogo dostopajo do ukazov vloge - e.g. samo robber lahko uporablja ukaze robberja\n
    Input:
        game...list aktualne 
        user...discord objekt, ki ga določim z role_id, in ga uporabim za DM komunikacijo z uporabnikom
        nextRole...ime vloge, ki je trenutno na vrsti(string)
        role2protect...katero vlogo varuje ta safetyNet
    Output:
        issafe...bool, ki pove če je user pravi in lahko uporablja ukaze vloge rolename
    '''
    issafe = False
    print('SafetyNet >>> ',end='')
    try:
        for player in game:     #najdem vlogo tega igralca
            if player['user_id'] == user.id:
                playersRole = player['role'].split(' ')[0]
        #the net
        print('playersRole: ', playersRole, ' <> ','currentRole:', currentRole, ' <> ','role2protect:', role2protect, '\n', end='')
        if (playersRole == role2protect) and (currentRole == role2protect):
            issafe = True   #če se nič zgoraj ne zgodi pol ukaz uporablja ta prava vloga, takrat ko je na vrsti
        elif (playersRole == role2protect) and (currentRole != role2protect):  #če nisi na vrsti drugi pogoj ne velja
            await user.send('Not your turn buddy!')
        elif playersRole != role2protect:                   #varovalni pogoji so na začetku
            await user.send('You are not ' + role2protect + ', so cut it out.\nDumbkopf!')
        else:
            pass
    except:
        await user.send('The game hasn\'t started yet.')
    return issafe

async def throwError(errors):
    '''
    Randomly returns one error from collection of errors.
    '''
    error='no error'
    return error
##################################################################################################

### LOGIN into guild ################################################################################
@wolfy.event   #@ je event handler - ko se vzpostavi povezava se izvede ta funkcija
async def on_ready():
    #print(wolfy.guilds)
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
##################################################################################################







##################################################################################################
############################################## MAIN ##############################################
##################################################################################################
@wolfy.event
async def on_message(message):
    global data
    global game
    global next_one
    global CHANNEL

    testgame = [#{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'SEER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False}, 
                {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': 'MASON - The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win.', 'played':False}, 
                {'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'INSOMNIAC - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False},
                #{'name': 'kristof', 'user_id': 689072253002186762, 'status': 'off', 'role': 'SEER - The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win.', 'played':False}, 
                {'name': 'tableCard1', 'user_id': 1, 'status': 'on', 'role': 'MASON - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
                {'name': 'tableCard2', 'user_id': 2, 'status': 'on', 'role': 'WEREWOLF - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
                {'name': 'tableCard3', 'user_id': 3, 'status': 'on', 'role': 'VILLAGER - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}]

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
        game = testgame#ww.assign_roles(data)  #dobim list vseh članov, ki so v igri
        CHANNEL = message.channel.id #tam kjer začnem igro, tam se bo končala
        nextRole = None   #ni še noč, villager itak spi
        
        #adding nicknames
        justroles = ww.list_active_roles(game)  #katere vloge so v igri
        msg = 'NewGame:\n' + justroles + '\nassigning roles...'
        beautifulmsg = f'```yaml\n{msg}\n```'
        await message.channel.send(beautifulmsg) 
        time.sleep(1);

        for player in game:
            playerID = player['user_id']
            playersRole = player['role'].split(' ')[0]
            #TUKI GRE FUNKCIJA ZA ŠTETJE MASONOV, če je samo eden moram zamenjat vloge
            if playerID in [(n+1) for n in range(3)]:
                print(player['name'] + ' ' +str(player['role'].split(' ')[0]))  #don't send message to tableCards
            else:   
                user = wolfy.get_user(playerID)      #user - samo njemu pošiljam sporočila v tej iteraciji for zanke
                print(user.name, player['role'].split(' ')[0])
                player['name'] = user.name #priredim ime v slovarju game, da bo lažje naprej delat
                init_msg = msg4user(player) #lovrič me je blokiral!!! no_hello ne morem pošiljat
                await user.send(init_msg)   #sporočim vsakemu igralcu njegovo vlogo/karto

    ### .w NIGHT GAME - for static roles to know each other 
                if playersRole == 'VILLAGER':
                    player['played'] = True #nothing happens - just to make sure, that nothing happens
                elif playersRole == 'WEREWOLF': 
                    flag = False
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                            werewolf = wolfy.get_user(player_i['user_id']);
                            if werewolf != user:
                                flag = True
                                await user.send(f'> - **`{werewolf.name}`** is a WEREWOLF')  #POVEM KDO JE WEREWOLF                       
                    if not flag:
                        await user.send('> You are the only WEREWOLF') 
                    player['played'] = True
                elif playersRole == 'MINION':
                    flag = False #da vem, če sem našel kakega volkodlaka
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                            flag = True
                            werewolf = wolfy.get_user(player_i['user_id']);
                            await user.send(f'> - **`{werewolf.name}`** is a WEREWOLF')  #POVEM KDO JE WEREWOLF
                    if not flag:
                        await user.send('> You have no friends or WEREWOLFES, MINION\nhahaha...little piece of shit, Dumbkopf!')
                    player['played'] = True
                elif playersRole == 'MASON': #MASON numbers taken care of in function ww.assigned_roles()
                    flag = False #davem, če sem našel kakega masona
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'MASON') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                            mason = wolfy.get_user(player_i['user_id']);
                            if mason != user:
                                flag = True
                                await user.send(f'> - **`{mason.name}`** is a MASON')
                    if not flag:
                        await user.send('> You are the only MASON')
                    #player['played'] = True  #to se bo zgodilo v funkciji whos_next

        #send message to next role - his turn 
        next_one = ww.whos_next(game, data); #0-villager, 1-werewolf, 2-minion, 3-mason so zrihtani. Kdo je naslednji?
        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)
        print('.w',next_one)

###  NIGHT GAME - for dynamic roles to change game cards
    #Za vsako dinamično vlogo posebej glede na night_order...če igralec ni ta vloga ga Wolfy ignorira
    elif message.content.startswith('w.seer'):      ### SEER
        print('\nseer-start:',next_one)
        id_seer = message.author.id
        seer = wolfy.get_user(id_seer)
        _bljak, players4seer = ww.list4role(game, 'SEER', wolfy) #_bljak is list4msg, which we don't need anymore, but still need for function output
        #print(players4seer)
        
        safe = await safetyNet(game, seer, next_one, 'SEER') #da še kdo drug kot prava vloga ne izvaja ukazov
        for player in game:
            if safe: #past the safetyNet - user je definitivno seer
                look = message.content.split(' ')[1::] #spustim prvi element
                if len(look) == 1:    #če hoče videt igralca
                    if look[0] == 'abstain': 
                        await seer.send('Abstinence is your choice.') #seer-pass
                        #send message to next role - his turn 
                        next_one = ww.whos_next(game, data);
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)
                        break
                    else:
                        hiddenPlaya = look[0];  
                        hiddenUser = ww.findUser(game, wolfy, hiddenPlaya, method='by_username')
                        for playa in game:
                            if playa['user_id'] == hiddenUser.id:
                                hiddenRole = playa['role']
                        await seer.send('> **`' + hiddenPlaya + '`** is a ' + hiddenRole + '.')   #show hiddenPlayer
                        #send message to next - his turn 
                        next_one = ww.whos_next(game, data);
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)
                        break
                elif len(look) == 2: #če hoče videt karti na mizi
                    first = ''; second = ''; #sporočila za posamezne karte
                    for card in look:
                        for tableCard in game:
                            if tableCard['name'] == card:
                                if first == '':
                                    first = card + ' is a ' + tableCard['role']
                                else:
                                    second = card + ' is a ' + tableCard['role']
                                    break
                    await seer.send(first + '\n' + second);
                    #send message to next - his turn 
                    next_one = ww.whos_next(game, data);
                    await msg4whos_next(message, game, CHANNEL, wolfy, next_one)
                    break
                else:   #če zajebe in neki ni prov vnesel
                    await seer.send('Well done! Somehow you fucked up...'); #If you fuck up the seer number we move on
                    break
        print('seer-end:', next_one, '\n')
    elif message.content.startswith('w.robber'):    ### ROBBER
        print('\nrobber-start', next_one)                                                                            
        id_robber = message.author.id
        robber = wolfy.get_user(id_robber);
        _bljak, players4robber = ww.list4role(game, 'ROBBER', wolfy)

        safe = await safetyNet(game, robber, next_one, 'ROBBER') #da še kdo drug kot robber ne izvaja ukazov              
        for player in game:
            #print('user:', robber, robber.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                choice = message.content.split(' ')[1]  #koga bomo oropal
                #print(type(choice), choice)
                #print(playersRole)
                if choice == 'abstain':
                    await robber.send('Abstinence is your choice.') #robber-pass
                    next_one = ww.whos_next(game, data);
                    print('robber-end',next_one, '\n')
                    await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                    break
                elif choice in players4robber.keys():
                    if choice in ['tableCard' + str(n+1) for n in range(3)]:
                        card_id = ww.findUser(game, wolfy, choice, method='on_table')
                        game, switch_msg = ww.switch(game, robber.id, card_id)
                        #print(game)
                        print('robber -',robber.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        for playa in game:   #robberju je treba povedat kaj je njegova nova vloga
                            if playa['user_id'] == robber.id:
                                new_role = playa['role']
                                msg = '> Great! You are now ' + new_role.split('-')[0] + ' - ' + new_role.split('-')[1] + '.'
                                await robber.send(msg)
                                break
                        print('robber -',robber.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        next_one = ww.whos_next(game, data);
                        print('robber-end',next_one, '\n')
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                        break
                    else:
                        victim = ww.findUser(game, wolfy, choice, method='by_username')
                        game, switch_msg = ww.switch(game, robber.id, victim.id)   #rob the victim
                        print(game)#game = list(game) in case game becomes tuple somehow???
                        for playa in game:   #robberju je treba povedat kaj je njegova nova vloga
                            if playa['user_id'] == robber.id:
                                new_role = playa['role']
                                msg = 'Great! You are now ' + new_role
                                await robber.send(msg)
                                break
                        print('robber -',robber.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        next_one = ww.whos_next(game, data);
                        print('robber-end',next_one, '\n')
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                        break
                else:
                    await robber.send('Well done! Somehow you fucked up...');   #If you fuck up the victim number we move on
                    break

    if message.content.startswith('w.troublemaker'):       ### TROUBLEMAKER
        print('\ntroublemaker-start', next_one)                                                                            
        id_trouble = message.author.id
        troublemaker = wolfy.get_user(id_trouble);
        _bljak, players4trouble = ww.list4role(game, 'TROUBLEMAKER', wolfy)
        firstID = None; secondID = None #id-ja ki ju moram zamenjat

        safe = await safetyNet(game, troublemaker, next_one, 'TROUBLEMAKER') #da še kdo drug kot robber ne izvaja ukazov              
        for player in game:
            #print('user:', troublemaker, troublemaker.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                trouble = message.content.split(' ')[1::]  #koga bomo menjal
                if trouble[0] == 'abstain':
                    await troublemaker.send('Abstinence is your choice.') #trouble pass
                    next_one = ww.whos_next(game, data);
                    print('troublemaker-end',next_one, '\n')
                    await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                    break
                else:
                    if len(trouble) == 2: #tukaj zamenjam dve karti
                        for playa in trouble:
                            if firstID == None:  #zapišem ID v ta pravo/prosto spremenljivko
                                if playa in ['tableCard' + str(n+1) for n in range(3)]: #Določim ID igralca, ki ga menjam
                                    firstID = ww.findUser(game, wolfy, playa, method='on_table') 
                                    first_name = playa
                                else:
                                    user = ww.findUser(game, wolfy, playa, method='by_username') 
                                    firstID = user.id
                                    first_name = user.name
                            else:
                                if playa in ['tableCard' + str(n+1) for n in range(3)]: #Določim ID igralca, ki ga menjam
                                    secondID = ww.findUser(game, wolfy, playa, method='on_table') 
                                    second_name = playa
                                else:
                                    user = ww.findUser(game, wolfy, playa, method='by_username') 
                                    secondID = user.id
                                    second_name = user.name

                        game, switch_msg = ww.switch(game, firstID, secondID)   #menjam
                        print('troublemaker -',troublemaker.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        await troublemaker.send('> Well done! You switched **`' + first_name + '`** and **`' + second_name + '`**.')
                        next_one = ww.whos_next(game, data);
                        print('troublemaker-end',next_one, '\n')
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                        break
                    else:
                        await troublemaker.send('Well done! Somehow you fucked up...');   #If you fuck up the victim number we move on
                        break
        
    if message.content.startswith('w.drunk'):   ### DRUNK
        print('\ndrunk-start', next_one)                                                                            
        id_drunk = message.author.id
        drunk = wolfy.get_user(id_drunk);
        _bljak, players4drunk = ww.list4role(game, 'DRUNK', wolfy)

        safe = await safetyNet(game, drunk, next_one, 'DRUNK') #da še kdo drug kot robber ne izvaja ukazov              
        for player in game:
            #print('user:', drunk, drunk.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                drunk_choice = message.content.split(' ')[1]  #katero karto na mizi je uporabnik izbral
                if drunk_choice == 'abstain':
                    await drunk.send('> Abstinence is your choice, good for you.') #drunk-pass
                    next_one = ww.whos_next(game, data);
                    print('drunk-end',next_one, '\n')
                    await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                    break
                else:
                    if drunk_choice in ['tableCard' + str(n+1) for n in range(3)]:
                        cardID = ww.findUser(game, wolfy, drunk_choice, method='on_table')
                        game, switch_msg = ww.switch(game, drunk.id, cardID)
                        print('drunk -',drunk.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        await drunk.send('> In the morning you won\'t know who you are...')
                        next_one = ww.whos_next(game, data);
                        print('drunk-end',next_one, '\n')
                        await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                        break
                    else:
                        await drunk.send('> Off course you screwed up. Your\'re drunk!')
                        break

    if message.content.startswith('w.insomniac'):
        print('\ninsomniac-start', next_one)                                                                            
        id_insomniac = message.author.id
        insomniac = wolfy.get_user(id_insomniac);
        _bljak, players4insomniac = ww.list4role(game, 'INSOMNIAC', wolfy)

        safe = await safetyNet(game, insomniac, next_one, 'INSOMNIAC') #da še kdo drug kot robber ne izvaja ukazov              
        for player in game:
            #print('user:', insomniac, insomniac.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                choice = message.content.split(' ')[1]  #če hočeš pogledat svojo karto pusti prazno
                if choice == 'abstain':
                    await insomniac.send('> Abstinence is your choice.') #insomniac-pass
                    next_one = ww.whos_next(game, data);
                    print('insomniac-end',next_one, '\n')
                    await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                    break
                elif choice = '':
                    if player['user_id'] == insomniac.id:
                        whoami = player['role'].split(' ')[0]
                        if whoami == 'INSOMNIAC':
                            await insomniac.send('> At the end of the night you are still INSOMNIAC.')
                            next_one = ww.whos_next(game, data);
                            print('insomniac-end',next_one, '\n')
                            await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                            break
                        else:
                            await insomniac.send('> At the dawn you wake up as ' + player['role'] + '.')
                            next_one = ww.whos_next(game, data);
                            print('insomniac-end',next_one, '\n')
                            await msg4whos_next(message, game, CHANNEL, wolfy, next_one)  
                            break
                else:
                    await insomniac.send('> Dude, you had one job!')

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
            table = wolfy.get_channel(CHANNEL)
        except:
            CHANNEL = 691400770557444096 #table v NoFunAllowed
            table = wolfy.get_channel(CHANNEL)
        if not game:
            await table.send('The game hasn\'t started yet.')
        else:
            ### glavno sporočilo za vse ###
            #v channel #table prikažem kdo je bil kdo 
            msg = 'GameOver:\n'
            table_cards = '\nTable cards were\n'
            for player in game:
                playerID = player['user_id']
                #show table cards
                if playerID in [(n+1) for n in range(3)]:
                    role_name = player['role'].split(' ')[0]
                    table_cards = table_cards + ' - ' + role_name + '\n'
                else:
                    user = wolfy.get_user(playerID)
                    player_name = user.name
                    role_name = player['role'].split(' ')[0]
                    msg = msg + ' - ' + player_name + ' was ' + role_name + '\n'
            game = [] #reset game

            msg = msg + table_cards
            beautifulmsg = f'```yaml\n{msg}\n```'
            await table.send(beautifulmsg)
            

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