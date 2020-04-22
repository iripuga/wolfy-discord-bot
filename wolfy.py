###   TODO  ###
# - ko zajebe mu vrnem random error message
# - rabim funkcijo errorHandler
# - desires je nujno treba sprogramirat, da lohk zbiramo tiste vloge, ki hočemo
# - nočna navodila se vsa pošiljajo v DM posameznim igralcem...zvem id-je od igralcev in jih fliknem v en list. pol ko pošiljam sporočilo iteriram čez ta list
# *- pogruntat čas fake timinga, da bo igra hitreje tekla. Mogoče uporabim random.gauss(mu, sigma).si
# - w.vote kjer vsak napiše wolfyju koga bi ustrelil, wolfy počaka da vsi volijo in pol objavi v gameroom kod je umrl. Mora tut povedat kako je kdo volil.
# # # # # # # #

global data #.gameData.json
global static #ta se definira na začetku in po njej vloge igrajo
global dynamic #v tej se odražajo dejanja vlog - this will be my main game dict in which all will happen - TA JE NUJNA, ostale niti ne tolk
global next_one #hranim ime vloge, ki je naslednja na vrsti - tut nujno
global GUILD
global CHANNEL #kanal v katerem igralci igrajo
global ADMIN #samo tist, ki začne igro jo lohk predčasno konča
global listOrder #seznam imen igralcev, ki jih uporabim, da je vedno isto zaporedje igralcev v izpisu
global start, end #spremenljivki za štopanje

#global t_start #čas začetka igre - na konc pogledam t_end in gledam kdaj je 10 min
static = []
dynamic = []
listOrder = []
next_one = ''
ADMIN = None

import discord
from discord.ext.commands import Bot
import os
from dotenv import load_dotenv
from random import shuffle, uniform, randint
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
errors = [  'Mission failed succesfully!',  #za tiste, ki ne znajo vnašat wolfy ukaze - izbiram random
            'Well done! Somehow you fucked up...',
            'As\' si mau duška dau?!',
            'Ma goni se!',
            'Bemti nanule, kristusove opanke...',
            'Pišuka Polde, ni to prava komanda',
            'Pejt v maloro klamfe srat, hudič sakramenski.',
            'Ka zaj te bom jaz učil komande pisat? Nea mi ga seri, lepo te prosim.',
            'Ahhh, das ist unglaublich...']
specialError = ['Prideta Mujo in Haso...', '...pa ti rečeta: "Ajoj, baš ni ne znaš komandirat, jarane."']  #najprej prvi msg, počakam 3s, pošljem drugi error

# Dictionary of commands {'command_name':'description'}
commands = {
    'basic':
        {
            "'woof'":'ping wolfy to your channel, only there can you play the game', 
            "'wolfy'":'wolfy tells common german phrase or a joke...',  #'maš kak vic?':'a rabm sploh razlagat?',
            "'w.help'":'you know that already',
            "'w.id'":'wolfy, whats my discord id',
            "'w.logout'":'bye, wolfy',
            "'w.status'":'change your status(on/off), if its off you wont be able to play',
            "'.w'":'start new game of werewolfes'
        },
    'game':
        {
            "'w.<rolename>'":'you will know when the time is right and the moon is bright...',
            "'w.end'":'everybodys roles are revealed, only person who started the game can end it'
        }
} 
'''   
Enkrat mi bo ratal sporočilo za pozdrav - lahko je random nemška fraza iz seznama(http://streettalksavvy.com/street-talk-german-slang/german-slang-phrases/) 
Ne rabi bit sporočilo na začetku logina, lohk je sam ena fora, ki je sprogramirana v bota. Kličeš z eno frazo in bot odgovori iz random knjižnice nemških fraz.    
''' 
#############################################################################################



### BOT ##########################################################################################
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #password to get acces to login bot into discord
wolfy = Bot(command_prefix='.') #connection to discord bot, same and more than Client

# Which GUILD to use??? Guild je server v discord jeziku. Za nov server moraš v server najprej prijavit bota preko developers strani
print('Which guild? ', end=' ')
server = input()
if server.upper() == 'NFA':
    GUILD = os.getenv('NFA')
    CHANNEL = os.getenv('NFA-table')
elif server.upper() == 'W':
    GUILD = os.getenv('WoofServer')
    CHANNEL = os.getenv('W-general')
else:
    GUILD = os.getenv('MaGuilt') #default GUILD is MG
    CHANNEL = os.getenv('MG-table')
GUILD = int(GUILD)
CHANNEL = int(CHANNEL)
##################################################################################################



### FUNKCIJE #####################################################################################
def catchLovric(id):
    '''
    function to find Lovrič and change his id to #wolfy channel id in server #Lovrič so that he doesn't cause any errors\n
    Input
        iID...input player id
    Output
        oID...returns sam id if its not lovrič and returns "wolfy" channel id if its lovrič
    '''
    if iID == 548304226988720149: 
        oID = 702488609478934630
    else:
        oID = iID

    return oID

def msg4user(game, game_player, wolfy):
    '''
    Funkcija sestavi sporočilo, ki ga ob začetku igre pošljem vsakemu uporabniku\n
    Input:
        game...aktivna igra(seznam slovarjev) z vsemi igralci in vlogami
        game_player...slovar enega igralca
        wolfy...you know!
    Output:
        msg...sporočilo za igralca
        user...objekt s katerim lahko pošljemo direktno sporočilo igralcu
    '''
    print(game_player)
    game_playerID = game_player['user_id']
    user = ww.checkID(game, game_playerID, wolfy)  #user - samo njemu pošiljam sporočila v tej funkciji - funkcija pa se iterira čez vse igralce
    
    # PRILAGODIM IMENA IGRALCEV, da lepše izgleda na discordu
    if game_player['name'] == 'lovric':
        game_player['name'] = 'no_hello'; #še en dodatek za lovriča
    else:
        game_player['name'] = user.name #priredim ime v slovarju game, da bo lažje naprej delat

    playername = game_player['name']
    role = game_player['role']
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
    
    return msg_role, user

async def msg4all(message, userIDs, wolfy, activeRole):
    '''
    Funkcija poskrbi, da se sporočila namenjena vsem trenutnim igralcem pošljejo v DM. Zaenkrat nič ne vrne.
    \nInput    
        userIDs...seznam ID-jev trenutnih uporabnikov, da jim lahko pošiljam sporočila
        wolfy...ma man
        activeRole...name of role which wakes up at night
    '''
    activeRole.upper()  #velke črke hočem

    if activeRole in ['VILLAGER', 'WEREWOLF', 'MINION', 'MASON']:
        msg = 'WEREWOLFES, MASONS and MINION have done their thing :crescent_moon:'
    else:
        msg = f'{activeRole}, open your :eyes:'

    for uid in userIDs:
        u = wolfy.get_user(uid)
        await u.send(msg)   

    return f'>>> msg4all(..., {activeRole}) sent'

async def msg4werewolf(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    activeRole = 'WEREWOLFES'
    table = wolfy.get_channel(channel)
    if active:
        pass #to je že na začetku zrihtan
    else:
        await table.send('WEREWOLFES, open your  👀')

async def msg4minion(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    table = wolfy.get_channel(channel)
    if active:
        pass #to je že na začetku zrihtan
    else:
        await table.send('MINION, open your  👀')

async def msg4mason(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    table = wolfy.get_channel(channel)
    if active:
        pass #to je že na začetku zrihtan
    else:
        await table.send('MASONS, open your  👀')

async def msg4seer(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    seer = ww.findUser(game, wolfy, 'SEER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if seer != None and active:
        msg, _bljak = ww.list4role(game, 'SEER', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('SEER, open your  👀')
        await seer.send(msg)
    else:
        await table.send('SEER, open your  👀')

async def msg4robber(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    robber = ww.findUser(game, wolfy, 'ROBBER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if robber != None and active:
        msg, _bljak = ww.list4role(game, 'ROBBER', wolfy) #določim med kom lahko robber izbira
        await table.send('ROBBER, open your  👀')
        await robber.send(msg)
    else:
        await table.send('ROBBER, open your  👀')

async def msg4troublemaker(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    troublemaker = ww.findUser(game, wolfy, 'TROUBLEMAKER', method='by_rolename')
    table = wolfy.get_channel(channel)
    if troublemaker != None and active:
        msg, _bljak = ww.list4role(game, 'TROUBLEMAKER', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('TROUBLEMAKER, open your  👀')
        await troublemaker.send(msg)
    else:
        await table.send('TROUBLEMAKER, open your  👀')

async def msg4drunk(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    drunk = ww.findUser(game, wolfy, 'DRUNK', method='by_rolename')
    table = wolfy.get_channel(channel)
    if drunk != None and active:
        msg, _bljak = ww.list4role(game, 'DRUNK', wolfy) #določim med kom lahko drunk izbira, _bljak ne rabim
        await table.send('DRUNK, open your  👀')
        await drunk.send(msg)
    else:
        await table.send('DRUNK, open your  👀')

async def msg4insomniac(message, game, channel, wolfy, active):
    '''
    active...bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    '''
    insomniac = ww.findUser(game, wolfy, 'INSOMNIAC', method='by_rolename')
    table = wolfy.get_channel(channel)
    if insomniac != None and active:
        msg, _bljak = ww.list4role(game, 'INSOMNIAC', wolfy) #določim med kom lahko robber izbira, _bljak ne rabim
        await table.send('INSOMNIAC, open your  👀')
        await insomniac.send(msg)
    else:
        await table.send('INSOMNIAC, open your  👀')

async def msg4whos_next(message, game, channel, wolfy, data, t1):
    '''
    Pošlje sporočilo igralcu, ki je naslednji na vrsti. Vrne ime vloge, ki je naslednja na vrsti.
    Tut vloge, ki nič ne delajo in so na mizi mora izgledat da so odigrale svojo potezo. 
    Z izjemo villagerja, ki pa vedno spi ponoči.\n
    Input:
        message...objekt od uporabnika, ko pošlje sporočilo v kanal
        game...aktualna igra
        channel...kanal v katerem se igra. Tja grejo sporočila za vse.
        wolfy...ma bot
        data...slovar celotne igre in igralcev .gameData.json
        t1...previous start time -> to calculate deltaT i measure end time t2 at beginning of this function
    Output: 
        nextRole...ime vloge, ki bi trenutno mogla bit na vrsti, type string
        startTime...current start time -> začnem štopat, da izmerim uporabnikov odziv oz. kolk časa je rabu, da je odgovoru
    '''
    #nastavim najkrajši in najdaljši čas zakasnitve
    short = 6.1
    long = 14.2
    
    t2 = time.time() # beležim končni čas odziva uporabnika
    print('active user\'s deltaT >>>', t2 - t1)

    all_roles_order, active_roles_order = ww.whos_next(game, data); #None-villager, 1-werewolf, 2-minion, 3-mason so zrihtani. Kdo je naslednji?
    table = wolfy.get_channel(channel)
    roleStatus = False # roleStatus je bool, ki pove ali je ta vloga dejansko aktivna ponoči(True) al se sam dela da je aktivna ponoči(False)
    #print('\nall_roles_order >>>', all_roles_order, '\nactive_roles_order >>>', active_roles_order)
    
    # NI LOGIČNO - sam zato, da gre v for zanki čez, ker neki nagaja zaradi OrderedDict() data tipa
    if not active_roles_order:
        active_roles_order = ['ShimSham'] 
    elif not all_roles_order:
        all_roles_order = ['ShamShim']
    else:
        pass 
    ########################################
    
    localt1 = ww.transcribe(t1)
    localt2 = ww.transcribe(t2)
    #iskanje naslednje aktivne vloge med množico pasivnih vse dokler ne najdem ene aktivne
    for i in range(len(all_roles_order)):
        deltaT = t2 - t1 #zračunam kolk je uporabnik rabil
        nextrole = all_roles_order[i]
        print('\nnextRole >>>', nextrole)
        if nextrole == None:
            pass
        elif nextrole == active_roles_order[0]: #naslednja dejansko aktivna vloga
            print('...is active')
            for player in game:
                if nextrole == player['role'].split(' ')[0]:
                    nextRole = nextrole #small become large eventually
                    player['played'] = True #ta igralec je zdaj zabeležen, kot da je že odigral
                    roleStatus = True
                    break
            break
        else:#if nextrole == all_roles_order[0]:  #fake aktivna vloga
            for playa in game:
                if nextrole == playa['role'].split(' ')[0]:
                    print('...waiting for playa')
                    all_roles_order[i] = None #odstranim ta element, ne smem spremenit dolžine seznama
                    #print('\nall_roles_order.pop(0) >>>', all_roles_order)
                    nextRole = nextrole #nima veze kdo je ta vloga, ker itak fejkam aktivnost
                    playa['played'] = True #važno je da se ne pojavlja na kasnejših seznamih
                    roleStatus = False
                    break    

        #else:
           # raise ValueError('Unknown error in msg4whos_next() from wolfy.py')

        # Tukaj pošiljam sporočilo za nextRole
        if nextRole == 'WEREWOLF':
            await msg4werewolf(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
        elif nextRole == 'MINION':
            await msg4minion(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
        elif nextRole == 'MASON':
            await msg4mason(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
        elif nextRole == 'SEER':
            await msg4seer(message, game, channel, wolfy, active=roleStatus)
        elif nextRole == 'ROBBER':
            await msg4robber(message, game, channel, wolfy, active=roleStatus)
        elif nextRole == 'TROUBLEMAKER':
            await msg4troublemaker(message, game, channel, wolfy, active=roleStatus)  
        elif nextRole == 'DRUNK':
            await msg4drunk(message, game, channel, wolfy, active=roleStatus)
        elif nextRole == 'INSOMNIAC':
            await msg4insomniac(message, game, channel, wolfy, active=roleStatus)       
        else:
            raise ValueError(str(nextRole) + ' is not awake at night.')

        if roleStatus:
            break # Če je aktivna vloga odigrala svoje skočim ven iz funkcije in igra se nadaljuje normalno
        else:
            deltaT = uniform(short, long)
            time.sleep(deltaT)
            print('deltaT >>>', deltaT)
            
        ########################################################

    if all(role is None for role in all_roles_order):  #Ko noben več ni na vrsti
        nextRole = None  

    # Še enkrat moram tole ponoviti izven for zanke, da se igra lahko premakne naprej
    if nextRole == 'WEREWOLF':
        await msg4werewolf(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
    elif nextRole == 'MINION':
        await msg4minion(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
    elif nextRole == 'MASON':
        await msg4mason(message, game, channel, wolfy, active=roleStatus)    #zrihtano v .w - tukaj le simuliram aktivnost za ostale igralce
    elif nextRole == 'SEER':
        await msg4seer(message, game, channel, wolfy, active=roleStatus)
    elif nextRole == 'ROBBER':
        await msg4robber(message, game, channel, wolfy, active=roleStatus)
    elif nextRole == 'TROUBLEMAKER':
        await msg4troublemaker(message, game, channel, wolfy, active=roleStatus)  
    elif nextRole == 'DRUNK':
        await msg4drunk(message, game, channel, wolfy, active=roleStatus)
    elif nextRole == 'INSOMNIAC':
        await msg4insomniac(message, game, channel, wolfy, active=roleStatus)       
    else:
        #time.sleep(uniform(short, long))
        await table.send('```prolog\nEverybody, open your  👀```') #Na konc zbudim vse
    
    startTime = time.time()  #nov start time

    return nextRole, startTime

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
    channel = wolfy.get_channel(CHANNEL)

    '''
    # TODO - FINDING lovrič #
    print(wolfy.private_channels)
    for ch in wolfy.private_channels:
        print(ch)
    lovric = wolfy.get_user(689399469090799848)
    print('>>> LOVRIČ', lovric.name, lovric.id)
    try:
        await lovric.send('jel radi?')
    except:
        await channel.send('ne radi!')
    ##################
    '''

    for guild in wolfy.guilds:      #Na katerem serverju sem in...
        if int(guild.id) == GUILD:
            break
    print(
        f'{wolfy.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    show_members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {show_members}')

    await wolfy.change_presence(status=discord.Status('w.help'), 
                                game=discord.Game(name="Werewolfes"))
                                #activity=discord.Activity(type=discord.ActivityType.playing, name="to w.help")) # da vsi vidijo ukaz za pomoč
    await channel.send('Hallo, ich möchte ein Spiel zu spielen!')    
##################################################################################################

'''
# TODO - FINDING Lovrič #
@wolfy.event
async def in_msg(msg):
    user = msg.author
    for ch in client.private_channels:
        print(ch)
        if user in recipients and len(recipients) == 2:
            await doSomethingWithChannel(ch, user)
            return
    # user doesn't have a PM channel yet if we got here
    ch = await client.start_private_message(user)
    await firstMessageToUser(ch, user)
##################
'''

############################################## MAIN ##############################################
@wolfy.event
async def on_message(message):
    '''
    Ukaz za začetek Werewolfs igre je '.w' 
    Ostali ukazi pa se kličejo z 'w.' + <ime_ukaza> ali pa samo <ime_ukaza>
    '''
    global data
    global static   #dict -> igra na začetku, po kateri kličem igralce
    global dynamic  #dict -> igra v kateri se vse spreminja
    global next_one
    global GUILD
    global CHANNEL
    global ADMIN
    global listOrder #seznam imen igralcev, ki jih uporabim, da je vedno isto zaporedje igralcev v izpisu
    global startTime, endTime
    #Če nista dve definiciji sta static in dynamic skos isti - pointerji na pomnilniški prostor so isti, samo ime je drugo

    '''
    testgame = [#{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'SEER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False}, 
                #{'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': 'DRUNK - ', 'played':False}, 
                {'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'INSOMNIAC - ', 'played':False},
                #{'name': 'kristof', 'user_id': 689072253002186762, 'status': 'on', 'role': 'VILLAGER - ', 'played':False}, 
                {'name': 'tableCard1', 'user_id': 1, 'status': 'on', 'role': 'SEER - ', 'played':True}, 
                {'name': 'tableCard2', 'user_id': 2, 'status': 'on', 'role': 'WEREWOLF - ', 'played':True}, 
                {'name': 'tableCard3', 'user_id': 3, 'status': 'on', 'role': 'MINION - ', 'played':True}]
    '''

### other COM stuff
    print('>>> PRIVATE CHANNELS >>>', wolfy.private_channels)
    #-------------------------------------------------------------------------------------------#
    if message.author == wolfy.user:    # ignore bot messages in chat - tko se bot ne bo pogovarjal sam s sabo!
        return
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith('woof'):      # message to call wolfy to desired channel on desired server
        gameguild = wolfy.get_guild(GUILD)
        gameroom = wolfy.get_channel(CHANNEL)
        if (not static) and (message.guild != None): #če ni igre lahko menjam guild in channel, drugač pa ne ker bi lahko kdorkoli prekinil trenuntno igro
            GUILD = message.guild.id
            CHANNEL = message.channel.id
            newguild = wolfy.get_guild(GUILD)
            newroom = wolfy.get_channel(CHANNEL)
            print(f'\n>>> woof switched to {newguild} in channel #{newroom}')
            await message.channel.send('WoofWoof!')
        elif message.guild == None:
            await message.channel.send(f'You can not play game alone! Come join in **{gameguild}** in **{gameroom}**.')
        else:
            await message.channel.send(f'Can\'t do that! Game is currently active on **{gameguild}** in **{gameroom}**. Maybe later...')
    elif message.content.startswith('w.help'): #Wolfy pomagaj!
        user = ww.checkID(static, message.author.id, wolfy) # povsod moram preverit, če je to LOVRIČ in potem pošljem sporočilo

        msg = 'Basics:\n'
        basic = commands['basic']
        ingame = commands['game']
        for cmd in basic:
            fullcmd = ' ' + cmd + ' - ' + basic[cmd] + '\n'
            msg = msg + fullcmd
        msg = msg + '\nDaGame:\n'
        for cmd in ingame:
            fullcmd = ' ' + cmd + ' - ' + ingame[cmd] + '\n'
            msg = msg + fullcmd
        msg = msg + '\nViel Spass!\n'

        HELP = '```prolog\n' + msg + '\n```' 
        await user.send(HELP)
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith('vic?'):#rabim seznam vicev
        await message.channel.send(vic)        #prostor za zbirko vicev, fraz in podobnih stvari
    elif message.content.startswith('wolfy'):  #rabim seznam nempkih glupih fraz
        await message.channel.send('Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier') 
    #-------------------------------------------------------------------------------------------#
    elif message.content == 'w.logout':     # by wolfy - stops script
        await message.channel.send('Aufwiedersehen!')  
        await wolfy.close()
    elif message.content == 'w.id':  #vsak lahko izve svoj id
        # to je spet LOVRIČ jebemu mast haha #
        your_id = catchLovric(message.author.id)
        ######################################
        user = wolfy.get_user(your_id)
        await user.send('Your ID is: ' + str(your_id))
    elif message.content.startswith('w.status'):
        #Tole je za vpis/izpis iz igre - menjava statusa v glavnem slovarju
        user_id = message.author.id
        nickname = message.author.name
        klik = ww.change_status(user_id)        #menjava statusa
        #with open('.gameData.json', 'w', encoding='utf-8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)
        msg = nickname + ' status: ' + klik
        await message.channel.send(str(msg))   
    #-------------------------------------------------------------------------------------------#
    
    ### WEREWOLFES GAME
    #-------------------------------------------------------------------------------------------#
### .w START GAME - send msg to players
    elif message.content == '.w':
        gameroom = wolfy.get_channel(CHANNEL)   #global CHANNEL kamor pošiljam splošne info o igri
        gameguild = wolfy.get_guild(GUILD)

        if message.channel.id != CHANNEL:
            someuser = wolfy.get_user(message.author.id)
            someroom = wolfy.get_channel(message.channel.id)
            await someroom.send(f'**`{someuser.name}`** you are in the wrong room. Game is on **{gameguild}** in **#{gameroom}**. Go there! \n...or say "woof" and we can play the game here.')
        elif not static: #if game is nonexistent, only then a new game can begin
            await gameroom.send('...erewolfes?')  
            ADMIN = message.author.id   # Edino un, ki začne igro jo lahko konča - to je ADMIN
            admin = wolfy.get_user(ADMIN)

            #Uvozim json podatke o igri in igralcih
            data = json.load(open('.gameData.json', 'r'))
            
            #definiram igro in preverim, če sta kazalca od slovarjev različna
            static = ww.assign_roles(data)  #dobim list vseh članov, ki so v igri -> To je dinamična igra, ki se skos spreminja
            dynamic = ww.transcribe(static) #ta se bo spreminjala
            print(f'>>> .w-start NEW GAME on {gameguild} in {gameroom}: \n - static is dynamic?', static is dynamic)
            
            #adding nicknames
            justroles = ww.listRoles(static)  #katere vloge so v igri
            msg = 'NewGame:\n' + justroles + '\nassigning roles...'
            beautifulmsg = f'```yaml\n{msg}\n```'
            await message.channel.send(beautifulmsg) 
            time.sleep(uniform(0.5, 2.5));
            await message.channel.send('Fertig!')

            print('\nACTIVE ROLES:')
            startTime = time.time()  #kao zacetek poteze od werewolfov, minionov in masonov
            for player in static:
                playerID = player['user_id']
                playersRole = player['role'].split(' ')[0]
                #TUKI GRE FUNKCIJA ZA ŠTETJE MASONOV, če je samo eden moram zamenjat vloge
                if playerID in [(n+1) for n in range(3)]:
                    print(' - ' + player['name'] + ' ' + str(player['role'].split(' ')[0]))  #don't send message to tableCards
                else:   
                    init_msg, user = msg4user(static, player, wolfy) #lovrič me je blokiral!!! no_hello ne morem pošiljat
                    print(user.name, player['role'].split(' ')[0])
                    try:
                        await user.send(init_msg)   #sporočim vsakemu igralcu njegovo vlogo/karto
                    except:
                        msg = 'A jebiga ' + user.name  #za lovriča
                        await gameroom.send(msg)

                    ### .w NIGHT GAME - for static roles to know each other 
                    if playersRole == 'VILLAGER':
                        player['played'] = True #nothing happens - just to make sure, that nothing happens
                    elif playersRole == 'WEREWOLF': 
                        flag = False
                        for player_i in static:
                            if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                                werewolf = wolfy.get_user(player_i['user_id']);
                                if werewolf != user:
                                    flag = True
                                    await user.send(f'> - **`{werewolf.name}`** is a WEREWOLF')  #POVEM KDO JE WEREWOLF                       
                        if not flag:
                            await user.send('> You are the only WEREWOLF') 
                        #player['played'] = True  to se vse dela zdj v msg4whos_next
                    elif playersRole == 'MINION':
                        flag = False #da vem, če sem našel kakega volkodlaka
                        for player_i in static:
                            if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                                flag = True
                                werewolf = wolfy.get_user(player_i['user_id']);
                                await user.send(f'> - **`{werewolf.name}`** is a WEREWOLF')  #POVEM KDO JE WEREWOLF
                        if not flag:
                            await user.send('> You have no friends or WEREWOLFES, MINION\nhahaha...little piece of shit, Dumbkopf!')
                        #player['played'] = True
                    elif playersRole == 'MASON': #MASON numbers taken care of in function ww.assigned_roles()
                        flag = False #davem, če sem našel kakega masona
                        for player_i in static:
                            if (player_i['role'].split(' ')[0] == 'MASON') and (not (player_i['user_id'] in [(n+1) for n in range(3)])):
                                mason = wolfy.get_user(player_i['user_id']);
                                if mason != user:
                                    flag = True
                                    await user.send(f'> - **`{mason.name}`** is a MASON')
                        if not flag:
                            await user.send('> You are the only MASON')
                        
                listOrder.append(player['name'])  #rabim ohranit isto zaporedje, da so igralci vedno izpisani v istem vrstnem redu v discord

            #rearrange list order for clear output at the end of game - tableCards in the end
            for card in ['tableCard1', 'tableCard2', 'tableCard3']:
                listOrder.remove(card)
            for card in ['tableCard1', 'tableCard2', 'tableCard3']:
                listOrder.append(card)
            print('\nplayersOrder >>>', listOrder)   
            print('userIDs >>>', ww.getIDs(listOrder, static))
            # Send message to next role - his turn 
            time.sleep(uniform(2.3, 4.1)) #da zgleda kot da pasivne vloge neki delajo
            await message.channel.send('WEREWOLFES, MINION and MASON have done their thing :crescent_moon:')
            next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)  #delay for non-active roles must be implemented here
            #print(listOrder)
            print('\n>>> .w-end',next_one)
        else:
            admin = wolfy.get_user(ADMIN)
            await message.channel.send(f'Can\'t start a new game with the current one still running. You can ask **`{admin.name}`** to finish the current game?')

###  NIGHT GAME - for dynamic roles to change game cards
    #Za vsako dinamično vlogo posebej glede na night_order...če igralec ni ta vloga ga Wolfy ignorira
    elif message.content.startswith('w.seer'):      ### SEER
        print('\n>>> seer-start:',next_one)
        id_seer = message.author.id
        seer = wolfy.get_user(id_seer)
        _bljak, players4seer = ww.list4role(static, 'SEER', wolfy) #_bljak is list4msg, which we don't need anymore, but still need for function output
        #print(players4seer)
        
        safe = await safetyNet(static, seer, next_one, 'SEER') #da še kdo drug kot prava vloga ne izvaja ukazov
        for player in static:
            if safe: #past the safetyNet - user je definitivno seer
                look = message.content.split(' ')[1::] #spustim prvi element
                if len(look) == 1:    #če hoče videt igralca
                    if look[0] == 'abstain': 
                        await seer.send('It is easier to look away from da truth...\n...da truth is DaWee!') #seer-pass
                        # Send message to next role - his turn 
                        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                        break
                    else:
                        hiddenPlaya = look[0];  
                        hiddenUser = ww.findUser(static, wolfy, hiddenPlaya, method='by_username')
                        for playa in static:
                            if playa['user_id'] == hiddenUser.id:
                                hiddenRole = playa['role']
                        await seer.send('> **`' + hiddenPlaya + '`** is a ' + hiddenRole + '.')   #show hiddenPlayer
                        # Send message to next role - his turn 
                        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                        break
                elif len(look) == 2: #če hoče videt karti na mizi
                    first = ''; second = ''; #sporočila za posamezne karte
                    for card in look:
                        for tableCard in static:
                            shortName = tableCard['name'][0] + tableCard['name'][-1]
                            if shortName == card:
                                if first == '':
                                    first = card + ' is a ' + tableCard['role']
                                else:
                                    second = card + ' is a ' + tableCard['role']
                                    break
                    await seer.send(first + '\n' + second);
                    # Send message to next role - his turn 
                    next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                    break
                else:   #če zajebe in neki ni prov vnesel
                    await seer.send('Well done! Somehow you fucked up...'); #If you fuck up the seer number we move on
                    break
        print('>>> seer-end:', next_one, '\n')
    
    elif message.content.startswith('w.robber'):    ### ROBBER
        print('\n>>> robber-start', next_one)                                                                            
        id_robber = message.author.id
        robber = wolfy.get_user(id_robber);
        _bljak, players4robber = ww.list4role(static, 'ROBBER', wolfy)

        safe = await safetyNet(static, robber, next_one, 'ROBBER') #da še kdo drug kot robber ne izvaja ukazov              
        for player in static:
            #print('user:', robber, robber.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                choice = message.content.split(' ')[1]  #koga bomo oropal
                #print(type(choice), choice)
                #print(playersRole)
                if choice == 'abstain':
                    await robber.send('To steal or not to steal is your choice.') #robber-pass
                    # Send message to next role - his turn 
                    next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                    break
                elif choice in players4robber.keys():
                    if choice not in ['tableCard' + str(n+1) for n in range(3)]:
                        victim = ww.findUser(static, wolfy, choice, method='by_username')
                        dynamic, switch_msg = ww.switch(dynamic, robber.id, victim.id)   #rob the victim
                        #print(game)#game = list(game) in case game becomes tuple somehow???
                        for playa in dynamic:   #robberju je treba povedat kaj je njegova nova vloga
                            if playa['user_id'] == robber.id:
                                new_role = playa['role']
                                msg = 'Great! You are now ' + new_role
                                await robber.send(msg)
                                break
                        print('\nrobber -',robber.name,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        # Send message to next role - his turn 
                        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime) 
                        break
                else:
                    await robber.send('Well done! Somehow you fucked up...');   #If you fuck up the victim number we move on
                    break
        print('>>> robber-end',next_one, '\n')

    if message.content.startswith('w.trouble'):       ### TROUBLEMAKER
        print('\n>>> troublemaker-start', next_one)                                                                            
        id_trouble = message.author.id
        troublemaker = wolfy.get_user(id_trouble);
        _bljak, players4trouble = ww.list4role(static, 'TROUBLEMAKER', wolfy)
        firstID = None; secondID = None #id-ja ki ju moram zamenjat

        safe = await safetyNet(static, troublemaker, next_one, 'TROUBLEMAKER') #da še kdo drug kot robber ne izvaja ukazov              
        for player in static:
            #print('user:', troublemaker, troublemaker.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                trouble = message.content.split(' ')[1::]  #koga bomo menjal
                if trouble[0] == 'abstain':
                    await troublemaker.send('Afraid to stir the pot, right? It\'s your choice.') #trouble pass
                    # Send message to next role - his turn 
                    next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime) 
                    break
                else:
                    if len(trouble) == 2: #tukaj zamenjam dve karti
                        for playa in trouble:
                            if firstID == None:  #zapišem ID v ta pravo/prosto spremenljivko
                                if playa not in ['tableCard' + str(n+1) for n in range(3)]: #Določim ID igralca, ki ga menjam
                                    user = ww.findUser(static, wolfy, playa, method='by_username') 
                                    firstID = user.id
                                    first_name = user.name
                            else:
                                if playa not in ['tableCard' + str(n+1) for n in range(3)]: #Določim ID igralca, ki ga menjam
                                    user = ww.findUser(static, wolfy, playa, method='by_username') 
                                    secondID = user.id
                                    second_name = user.name

                        dynamic, switch_msg = ww.switch(dynamic, firstID, secondID)   #menjam
                        #print('\nstatic >>>\n', static)
                        #print('\ndynamic >>>\n', dynamic)
                        print('troublemaker -',troublemaker.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                        await troublemaker.send('> Well done! You switched **`' + first_name + '`** and **`' + second_name + '`**.')
                        # Send message to next role - his turn 
                        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime) 
                        break
                    else:
                        await troublemaker.send('Well done! Somehow you fucked up...');   #If you fuck up the victim number we move on
                        break
        print('>>> troublemaker-end',next_one, '\n')

    if message.content.startswith('w.drunk'):   ### DRUNK
        print('\n>>> drunk-start', next_one)                                                                            
        id_drunk = message.author.id
        drunk = wolfy.get_user(id_drunk);
        _bljak, players4drunk = ww.list4role(static, 'DRUNK', wolfy)

        safe = await safetyNet(static, drunk, next_one, 'DRUNK') #da še kdo drug kot robber ne izvaja ukazov              
        for player in static:
            #print('user:', drunk, drunk.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                if len(message.content.split(' ')) > 1:
                    drunk_choice = message.content.split(' ')[1]  #katero karto na mizi je uporabnik izbral
                    if drunk_choice == 'abstain':
                        await drunk.send('> Abstinence will be good for you.') #drunk-pass
                        # Send message to next role - his turn 
                        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                        break
                    else:
                        print(drunk_choice)
                        if drunk_choice in ['t' + str(n+1) for n in range(3)]:
                            cardID = ww.findUser(static, wolfy, drunk_choice, method='on_table')
                            dynamic, switch_msg = ww.switch(dynamic, drunk.id, cardID)
                            print('drunk -',drunk.id,'>>>', switch_msg) #v terminalu vidim kdo je koga zamenjal
                            await drunk.send('> In the morning you won\'t know who you are...:face_vomiting:')
                            # Send message to next role - his turn 
                            next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                            break
                        else:
                            await drunk.send('> Of course you screwed up. Your\'re drunk!')
                            break
                else:
                    await drunk.send('> Of course you screwed up. Your\'re drunk!')
                    break
        print('>>> drunk-end',next_one, '\n')

    if message.content.startswith('w.insomniac'):   ### INSOMNIAC
        print('\n>>> insomniac-start', next_one)                                                                            
        id_insomniac = message.author.id
        insomniac = wolfy.get_user(id_insomniac);
        _bljak, players4insomniac = ww.list4role(static, 'INSOMNIAC', wolfy)

        safe = await safetyNet(static, insomniac, next_one, 'INSOMNIAC') #da še kdo drug kot robber ne izvaja ukazov              
        for player in dynamic:
            #print('user:', insomniac, insomniac.id, ' <> player:', player['name'], ' <> role:', player['role'].split(' ')[0])
            playersRole = player['role'].split(' ')[0]
            if safe:  #past the safetyNet
                choice = message.content  #če hočeš pogledat svojo karto pusti prazno
                if choice == 'w.insomniac abstain':
                    await insomniac.send('> Abstinence is your choice. Now go back to sleep!') #insomniac-pass
                    # Send message to next role - his turn 
                    next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime) 
                    break
                elif choice == 'w.insomniac':
                    if player['user_id'] == insomniac.id:
                        whoami = player['role'].split(' ')[0]
                        if whoami == 'INSOMNIAC':
                            await insomniac.send('> At the end of the night you are still INSOMNIAC.')
                            # Send message to next role - his turn 
                            next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)  
                            break
                        else:
                            await insomniac.send('> At the dawn you wake up as ' + player['role'] + '.')
                            # Send message to next role - his turn 
                            next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
                            break
                else:
                    await insomniac.send('> Dude, you had one job!')
                    break
        print('>>> insomniac-end',next_one, '\n')

    if message.content.startswith('w.abstain'):
        print('\n>>> abstain-start', next_one)                                                                            
        id_abstain = message.author.id
        abstain = wolfy.get_user(id_abstain)
        await abstain.send('> Abstinence is your choice.') #role-pass
        # Send message to next role - his turn 
        next_one, startTime = await msg4whos_next(message, static, CHANNEL, wolfy, data, startTime)
        print('>>> abstain-end',next_one, '\n')

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
    elif message.content == 'w.vote':
        pass

###  END GAME - who died, Wolfy reveals all the cards  ##################
    elif message.content == 'w.end':
        try:        #preveri, če je ADMIN ... to bi moral pomenit, da se igra še ni začela
            gameroom = wolfy.get_channel(message.channel.id)
            user = wolfy.get_user(message.author.id)
            admin = wolfy.get_user(ADMIN)
            print('table, user, admin >>>', table, user, admin)
        except: #če ne pozna channel poščje v NoFunAllowed
            user = wolfy.get_user(message.author.id)
            gameguild = wolfy.get_guild(GUILD)
            gameroom = wolfy.get_channel(CHANNEL)
        print('\n>>> w.end-start ' + user.name + ' in #', end='')
        #print(gameroom, type(message.channel.id), type(CHANNEL))

        if  CHANNEL != message.channel.id:
            someroom = wolfy.get_channel(message.channel.id)
            await someroom.send(f'**`{user.name}`** you are in the wrong room. Game is on **{gameguild}** in **#{gameroom}**. Go there! \n...or say "woof" and we can play the game here.')
        elif not static:
            await gameroom.send(f'**{user.name}** the game hasn\'t started yet!')
        elif ADMIN == None:
            pass
        else:
            if message.author.id == ADMIN:
                admin = wolfy.get_user(ADMIN)
                ### glavno sporočilo za vse ###
                #v channel #table prikažem kdo je bil kdo 
                #print(static,'\n', listOrder)

                start_terminal, start_msg = ww.openCards(static, wolfy, listOrder, tip='static') #_fujfuj ne rabim nikjer
                end_terminal, end_msg = ww.openCards(dynamic, wolfy, listOrder)
                
                # reset game #
                static = []
                dynamic = [] 
                ADMIN = None
                admin = None
                user = None
                #CHANNEL se spremeni samo z ukazom 'woof'
                listOrder = []
                next_one = ''
                ##############

                print(start_terminal, '\n', end_terminal) #začetne vloge so itak že napisane na začetku
                beautifulmsg = f'```yaml\n{start_msg}\n{end_msg}```'
                await gameroom.send(beautifulmsg)
            else:
                await user.send('You are not admin of current game. You will have to talk with **`' + admin.name + '`** about that.')
        print('>>> w.end-end')        

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