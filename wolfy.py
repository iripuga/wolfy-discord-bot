global game #this will be my main game dict in which all will happen
global night_role #spremenljivka, ki hrani katera vloga je ponoči na vrsti
global tableID 
global players4role #number coded list of players for quicker game with dynamic roles
tableID = [1, 2, 3] #ID od table slotov

import discord
from discord.ext.commands import Bot
import os
from dotenv import load_dotenv
from random import shuffle
from numpy import linspace
import werewolfes as ww
import json
import time

# init vars
vic = "Sprehajala sem se po Hoferju, pa je en kurac pred menoj celo paleto wc papirja vleko!!! Pa sem ga natulila in mu rekla 'kaj vi samo serjete doma???' Pa mi je rekel: gospa jaz delam tukaj..."

testgame = [{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'ROBBER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.'}, 
            #{'name': 'rok', 'user_id': 261105970548178944, 'status': 'on', 'role': 'WEREWOLF - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.'}, 
            {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': "MASON - The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win."}, 
            #{'name': 'kristof', 'user_id': 689072253002186762, 'status': 'on', 'role': 'MASON - The Mason wakes up at night and looks for the other Mason. If the Mason doesnt see another Mason, it means the other Mason is in the center.'}, 
            #{'name': 'klemzo', 'user_id': 641347330804678667, 'status': 'on', 'role': 'MASON - The Mason wakes up at night and looks for the other Mason. If the Mason doesnt see another Mason, it means the other Mason is in the center.'}, 
            {'name': 'table_slot1', 'user_id': 1, 'status': 'on', 'role': 'MASON - The Villager has no special ability, but he is definitely not a werewolf.'}, 
            {'name': 'table_slot2', 'user_id': 2, 'status': 'on', 'role': 'VILLAGER - The Villager has no special ability, but he is definitely not a werewolf.'}, 
            {'name': 'table_slot3', 'user_id': 3, 'status': 'on', 'role': 'VILLAGER - The Villager has no special ability, but he is definitely not a werewolf.'}]


"""
# Če bom hotu kake evente spreminjat moram bota definirat s tem razredom
class Custom(discord.Client):
    async def overridden_fun():
        return
"""

### BOT 
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN") #password to get acces to login bot into discord
wolfy = Bot(command_prefix='.') #connection to discord bot, same and more than Client


# Which GUILD to use??? Guild je server v discord jeziku.
print("Which guild? ", end=" ")
server = input()
if server == "NFA":
    GUILD = os.getenv("NFA")
    CHANNEL = 688744586293936296 #general
    TABLE = 691400770557444096  #table
else:
    #print("MG")
    GUILD = os.getenv("DISCORD_GUILD") #default GUILD is IoS
    CHANNEL = 690010969438421006  #general!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!TOLE JE TREBA ŠE DAT V .env!!!
    TABLE = 690141479666188334  #table
GUILD = int(GUILD)




#nč ne dela to
@wolfy.command()
async def ping(ctx, *, message):
    #await wolfy.process_commands(message)
    await ctx.send(message)

### LOGIN into guild
@wolfy.event   #@ je event handler - ko se vzpostavi povezava se izvede ta funkcija
async def on_ready():
    for guild in wolfy.guilds:      #Na katerem serverju sem in...
        if int(guild.id) == GUILD:
            break
    print(
        f"{wolfy.user} is connected to the following guild:\n"
        f"{guild.name}(id: {guild.id})"
    )
    show_members = "\n - ".join([member.name for member in guild.members])
    print(f"Guild Members:\n - {show_members}")
    
    
"""   
Enkrat mi bo ratal sporočilo za pozdrav - lahko je random nemška fraza iz seznama(http://streettalksavvy.com/street-talk-german-slang/german-slang-phrases/) 
Ne rabi bit sporočilo na začetku logina, lohk je sam ena fora, ki je sprogramirana v bota. Kličeš z eno frazo in bot odgovori iz random knjižnice nemških fraz.    
@wolfy.event
async def on_connect():
    await wolfy.channel.send("Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier") 
"""     
    







### MAIN
@wolfy.event
async def on_message(message):
    #other shit
    #-------------------------------------------------------------------------------------------#
    if message.author == wolfy.user:    # ignore bot messages in chat - tko se bot ne bo pogovarjal sam s sabo!
        return
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith("woof"):      # message for ping
        await message.channel.send("WoofWoof!")
    #-------------------------------------------------------------------------------------------#
    elif message.content.startswith("ustreli"):#rabim seznam vicev
        await message.channel.send(vic)        #prostor za zbirko vicev, fraz in podobnih stvari
    elif message.content.startswith("spam") or message.content.startswith("wolfy"):  #rabim seznam nempkih glupih fraz
        await message.channel.send("Ich wünsche allen Durchfall, kurze Arme, und kein Klopapier") 
    #-------------------------------------------------------------------------------------------#
    elif message.content == "!logout":     # by wolfy - stops script
        await message.channel.send("Aufwiedersehen!")  
        await wolfy.close()
    elif message.content == "!id":  #vsak lahko izve svoj id
        your_id = message.author.id
        user = wolfy.get_user(your_id)
        await user.send('Your ID is: ' + str(your_id))
    #-------------------------------------------------------------------------------------------#
    else:
        pass  #Don't respond to everything!
    
    # werewolfes game
    #-------------------------------------------------------------------------------------------#
     #aktualen seznam igralcev
    global night_role
    global tableID
    global players4role

    if message.content == "!w":
        await message.channel.send("...erewolfes?") 
        #Uvozim json podatke o igri in igralcih
        data = json.load(open(".game_data.json", "r"))
        
        global game
        game = testgame #ww.assign_roles(data)  #dobim list vseh članov, ki so v igri
        justroles = ww.list_active_roles(game)

        #adding nicknames
        msg = "New game - active roles:\n" + justroles + "\nassigning roles...\n"
        await message.channel.send(msg) 
        time.sleep(1);

    ####################################  START GAME - send msg to players  ###################################
        for player in game:
            playerID = player['user_id']
            playersRole = player['role'].split(' ')[0]
            #TUKI GRE FUNKCIJA ZA ŠTETJE MASONOV, če je samo eden moram zamenjat vloge
            if playerID in tableID:
                print('table #' + str(playerID))  #skip tables
            else:   
                user = wolfy.get_user(playerID)      #user - samo njemu pošiljam sporočila v tej iteraciji for zanke
                
                init_msg = ww.msg4user(player) #lovrič me je blokiral!!! no_hello ne morem pošiljat
                await user.send(init_msg)   #sporočim vsakemu igralcu njegovo vlogo/karto

                #######  NIGHT GAME - for static roles(knowing each other) and for dynamic roles to know what to do  ###
                if playersRole == 'VILLAGER':
                    pass #nothing happens
                elif playersRole == 'WEREWOLF': 
                    flag = False
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in tableID)):
                            werewolf = wolfy.get_user(player_i['user_id']);
                            if werewolf != user:
                                flag = True
                                await user.send(f" - {werewolf.name} is a WEREWOLF")  #POVEM KDO JE WEREWOLF                       
                    if not flag:
                        await user.send("You are the only WEREWOLF") 
                elif playersRole == 'MINION':
                    flag = False
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'WEREWOLF') and (not (player_i['user_id'] in tableID)):
                            flag = True
                            werewolf = wolfy.get_user(player_i['user_id']);
                            await user.send(f" - {werewolf.name} is a WEREWOLF")  #POVEM KDO JE WEREWOLF
                    if not flag:
                        await user.send("You have no friends or WEREWOLFES, MINION\nhahaha...little piece of shit, Dumbkopf!")
                elif playersRole == 'MASON': #MASON numbers taken care of in function ww.assigned_roles()
                    flag = False
                    for player_i in game:
                        if (player_i['role'].split(' ')[0] == 'MASON') and (not (player_i['user_id'] in tableID)):
                            mason = wolfy.get_user(player_i['user_id']);
                            if mason != user:
                                flag = True
                                await user.send(f" - {mason.name} is a MASON")
                    if not flag:
                        await user.send("You are the only MASON")
        night_role = 4; #villager, werewolf, minion, mason, next ROBBER

        #send message to robber - his turn
        robber = ww.find_role(game, 'ROBBER', wolfy)
        if robber != None:
            list4msg, players4role = ww.list_players(game, 'ROBBER', wolfy)
            msg = 'Your turn! Do you want to steal something\nEnter: robber-number\n' + list4msg;
            await message.channel.send('ROBBER, open your 👀.')
            await robber.send(msg)
   
    ####################################  NIGHT GAME - for dynamic roles(changing cards in a game)  ##########
    #Za vsako dinamično vlogo posebej...če igralec ni ta vloga ga Wolfy ignorira
    if message.content.startswith("robber"):
        user = wolfy.get_user(message.author.id);
        #TEŽAVE z globalnimi spremenljivkami
        try:
            a = message.content[8]; 
            ida = ww.get_id(players4role, a); 
            idb = message.author.id;
            print(a, ida)
            for player in game:
                playersRole = player['role'].split(' ')[0]
                if (playersRole == 'ROBBER') and (night_role == 4):
                    print(game)
                    game = switchAB(game, ida, idb)
                    print(game)
                    break
                elif (playersRole == 'ROBBER') and (night_role != 4):
                    await user.send('Not your turn buddy!')
                    break
                else:
                    await user.send('You are not a ROBBER, so cut it out.\nDumbkopf!')
                    break
        except:
            await user.send('The game hasn\'t started yet.')
        '''
        if playersRole == 'TROUBLEMAKER':
            pass
        elif playersRole == 'SEER':
            pass
        elif playersRole == 'INSOMNIAC':
            pass
        elif playersRole == 'DRUNK':
            pass
        elif playersRole == 'HUNTER':
            pass
        elif playersRole == 'TANNER':
            pass
        else:
            raise ValueError('Role non existent in this guild!')
        '''
    ####################################  MID GAME - Wolfy waits for players to discuss who to kill  #########
    #detajli

    ####################################  VOTING - Players send private message to Wolfy  ####################
    elif message.content == "!vote":
        pass

    ####################################  END GAME - who died, Wolfy reveals all the cards  ##################
    elif message.content == "!end":
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
    elif message.content == '!wolfy #iwannawin': #to bo na konc drugačen klic - GAME OVER
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
    elif message.content == "!s":
        #Tole je za vpis/izpis iz igre - menjava statusa v glavnem slovarju
        user_id = message.author.id
        nickname = message.author.name
        klik = ww.change_status(data, user_id)        #menjava statusa
        #with open('.game_data.json', 'w', encoding='utf-8') as f:
        #    json.dump(data, f, ensure_ascii=False, indent=4)
        msg = nickname + ' status: ' + klik
        await message.channel.send(str(msg))      
    
        
#run everything
wolfy.run(TOKEN)














"""
NOBENA KOMANDA NE DELA!?      in niimam pojma zakva!  
        
@wolfy.command(name = "werewolfes")
async def wolfs(ctx):
    await ctx.send("55") 
        
@wolfy.command(name="99")
async def nine_nine(ctx):
    brooklyn_99_quotes = [
        "I\"m the human form of the 💯 emoji.",
        "Bingpot!",
        (
            "Cool. Cool cool cool cool cool cool cool, "
            "no doubt no doubt no doubt no doubt."
        ),
    ]
    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)
    
@wolfy.command() #define the first command and set prefix to "!"
async def testt(ctx):
    await ctx.send("Hello!!")
# PRIVATE COMMUNICATION with members
        await message.author.send("👋")   #Tut dela, sam ni primerna za mojo aplikacijo
"""