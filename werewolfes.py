'''
Module for werewolfes game on discord.
'''
from random import shuffle, randint
from numpy import linspace
import json
import collections
from discord.ext.commands import Bot
wolfy = Bot(command_prefix='.')

#Uvozim json podatke o igri in igralcih
data = json.load(open('.gameData.json', 'r'))

### Funkcije #####################################################################################
def find_active(members):
    '''
    Determine who is playing by checking users ''status'' in members dict and returning list od active 'user_id''s
    Input:
        members...dict of members who are playing current game
    Output:
        players..returns list of active players for current game
    '''
    players = []
    for member in members:
        if member['status'] == 'on':
            players.append(member['user_id'])
        else:
            pass        #tisti, ki se nočjo igrat jih izpustim
            
    return players
 
def assign_roles(idata=data, desires=None):
    '''
    Shuffle new roles for another game of werewolfes. Append roles to dictionary 'members'.
    Input:
        idata...role and members data dictionary(look up)
        desires...list of desired roles which must match len(players)
    Output:
        assigned...list of members with assigned roles in dict format. 
    '''
    #init variables
    assigned_roles = []
    roles = idata['roles']; members = idata['members']
    players = find_active(members) #get list of active player id's which need role assignment
    
    #RANDOM SHUFFLE - določim indexe za vloge iz seznama members. samo toliko kot je igralcev v igri
    r_idx = []
    for num in range(len(players)):   
        r_idx.append(num)
    for mix in range(3351):   #every day i'm shuffling...premiksam, da je izbira vlog naključna
        shuffle(r_idx)  
    
    masons = 0;     #Števec MASONov poskrbim, da sta v igri dva MASONA al pa noben, ker drugač ta vloga nima smisla
    if desires == None:    #vloge so določene glede na index, ki se generira na podlagi števila igralcev. Ene vloge nikoli ne pridejo na vrsto! 
        i = 0
        for member in members:  #določam vloge
            for playerID in players:
                if playerID == member['user_id']:
                    get_role = int(r_idx[i]) #poiščem vlogo glede na index v seznamu premešanih indeksov
                    i = i + 1
                    rolename = roles[get_role]['name']
                    roledescription = roles[get_role]['description']
                    if rolename == 'MASON': #preverim, če je vsaj eden v igri
                        masons = masons + 1  
                    
                    #prepisovanje v member seznam
                    ROLE =  rolename + ' - ' + roledescription  
                    member['role'] = ROLE
                    if (rolename in ['VILLAGER', 'WEREWOLF', 'MINION', 'MASON']):
                        member['played'] = True #teli itak špilajo že v .w
                    else:
                        member['played'] = False #Za dinamičen del igre - če vloga še ni bila na vrsti je to False
                    assigned_roles.append(member)
                else:
                    pass
    else:
        '''
        Vloge določam glede na index v seznamu roles. 
        Ker nas je samo 9 igralcev(z mizami vred) ne moremo nikoli 
        dobiti vloge od Troublemakerja naprej. 
        Nekaj za razmislit, ko bom uvajal desires.
        ...definitivno bo to potrebno
        '''
        raise NotImplementedError('No desires!')
    
    #ne sme bit samo en MASON...DVA al pa NIČ
    if masons == 1:
        for role in assigned_roles:
            if role['role'].split(' ')[0] == 'VILLAGER':    
                NEW_ROLE = 'MASON - The Mason wakes up at night and looks for the other Mason. If the Mason doesnt see another Mason, it means the other Mason is in the center.'
                role['role'] = NEW_ROLE
                break
    return assigned_roles

def getIDs(listOrder, game):
    '''
    Funkcija uporabi urejen seznam igralcev po nočnem vrstnem redu 
    in pridobi njihove id-je, da lahko pošiljam DM sporočila hkrati.
    Input
        listOrder...seznam igralcev po nočnih vlogah, ki ga wolfy.py uporablja za lepo izpisovanje v discord
        game...seznam slovarjev aktualne igre, na kratko podatki o trenutni igri
    Output
        uids...User IDs, seznam id-jev od vseh igralcev, ki igrajo
    '''
    uids = []
    for name in listOrder:
        for u in game:
            if u['name'] == name:
                uid = u['user_id']
                if uid not in [1, 2, 3]:
                    txt = uid#name + ' ' + str(uid)
                    uids.append(txt)
    return  uids

def transcribe(igame):
    '''
    Just to transcribe object igame into new NOT CONNECTED object ogame
    \nSolution for "static is dynamic == True" problem, is to copy content by steps.
    This happens because every time an object is assigned to variable 
    it gets specific id(var_name). If id() of two objects are the same, 
    then objects are connected. 
    Yet I want static to be disconected to dynamic...
    
    \n...e.g. transcribe to get different id(). Function can also transcribe different data types.
    '''
    if isinstance(igame, dict):
        ogame = {}
        for payer in igame.keys():
            ogame[payer] = igame[payer]
    elif isinstance(igame, list):
        ogame = []
        for playa in igame:
            ogame.append(playa)
    elif isinstance(igame, str):
        ogame = ''
        for char in igame:
            ogame = ogame + char
    elif isinstance(igame, float):
        ogame = igame             #transcribe float
        #while ogame < igame:
        #    ogame = ogame + 0.1
    else:
        raise NotImplementedError('Data type of \'igame\' unknown')
    return ogame

def listRoles(game_roles):
    '''
    Vrne seznam vseh vlog v igri.
    \nInput:
        game_roles...seznam imen vlog v slovarju {id: role}
    Output:
        justroles...samo imena vlog za začetek igre
    '''
    justroles=''

    #print('game >>>', game_roles, '\n')
    for mix in range(1042):
        shuffle(game_roles)
    #print('shuffled >>>', game_roles, '\n')
    for player in game_roles:
        role = player['role'].split(' ')[0]
        justroles = justroles + ' - ' + role + '\n'
    return justroles
    
def list_active_id(game_roles):
    #Dobim seznam aktivnih id-jev iz slovarja {id: role}
    justid=[]
    for player in game_roles:
        key = player['user_id']
        if key == 1 or key == 2 or key == 3:
            pass
        else:
            justid.append(int(key))
    return justid
    
### DYNAMIC stuff with wolfy and users ##################################################################
def list4role(game, rolename, wolfy):
    '''
    creates a dict of players for dynamic roles (seer, robber, troublemaker) to use\n
    Input:
        game...active game data list, in dict form
        rolename...for which role are we listing players
        wolfy...my bot object
    Output:
        msg...for our user(depends on rolename)
        players4role...dict {user.name: user.id} of users for a specific role to chose from 
    '''
    tableID = [1, 2, 3]
    list4msg = f' - To abstain from your power TYPE: <w.abstain>\n'  #list4msg...string formated list for easier output
    list4insomniac = list4msg
    players4role = {}

    #print('game >>>', game, '\n')
    for mix in range(1042):
        shuffle(game)
    #print('shuffled >>>', game, '\n')
    for player in game:
        if player['name'] in ['tableCard' + str(n+1) for n in range(3)]:    #za tableCards ne morem narest wolfy objekta user - samo SEER lahko gleda karte ki so na mizi
            if (rolename == 'SEER') or (rolename == 'DRUNK'):
                list4msg = list4msg + ' - '+ player['name'][0] + player['name'][-1] + '\n'
                players4role[player['name']] = player['user_id']
            else:
                pass
        else:
            if (player['role'].split(' ')[0] != rolename) and (rolename != 'DRUNK'):  #vloga, ki je na vrsti ne sme bit na tem seznamu
                uid = player['user_id']
                usr = wolfy.get_user(uid)
                list4msg = list4msg + ' - '+ str(usr.name) + '\n'
                players4role[usr.name] = usr.id  #samo ime je dovolj za pošiljat
    #prettier output 
    #nice = '```yaml\n---------------------------------------------------------------------------------------\n```' 
    if rolename == 'SEER':
        nice = 'Your turn! Which cards shall we peek? Card from one player or two cards from table.\n' + list4msg
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.seer <player> or w.seer <tableCard#> <tableCard#>'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'ROBBER':
        nice = 'Your turn! Do you want to steal from someone?\n' + list4msg     #send message to robber - his turn 
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.robber <player>'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'TROUBLEMAKER':
        nice = 'Your turn! Let\'s make some mess and switch two players.\n' + list4msg
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.trouble <player1> <player2>'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'DRUNK':
        nice = 'Your\'re too drunk to do anything really, but you can play you role. You might become someone else...\n' + list4msg
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.drunk <tableCard#>'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'INSOMNIAC':
        nice = 'Your turn! Check your card, if you still have trouble sleeping.\n' + list4insomniac
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.insomniac'
        msg2 = f'```yaml\n{command}\n```'


    msg = msg1 + msg2
    return msg, players4role

def findUser(igame, wolfy, searchPar, method='by_rolename'):
    '''
    Finds role in active game data, by searching for its rolename. Returns user ID\n
    Input:
        igame...game data in list, each element is a dict
        searchPar...search parameter to help me find my user.
        wolfy...ma bot
        method...na kakšen način iščem uporabnika. Possible arguments:
            - rolename, method='by_rolename'
            - discord username, method='by_username'
            - tableCard#, method='on_table'
    Output:
        userID...discord UserID - player or card found by searchPar
    '''
    game = transcribe(igame)
    tableID = [1, 2, 3]
    user = None
    #print('findUser searchPar >>', searchPar)
    if method == 'by_rolename':
        #print('findUser method >>', method)
        rolename = searchPar
        rolename.upper();
        for player in game:
            #print('findUser >>', player['name'])
            if (player['role'].split(' ')[0] == rolename) and (player['user_id'] not in tableID):
                userID = player['user_id']
                break
            else:
                userID = None
    elif method == 'by_username':
        #print('findUser method >>', method)
        username = searchPar
        for player in game:
            if (player['name'] == username) and (player['user_id'] not in tableID):
                userID = player['user_id']
                break
            else:
                userID = None
    elif method == 'on_table':
        #print('findUser method >>', method)
        for c in game:
            shortName = c['name'][0] + c['name'][-1]
            if shortName == searchPar:
                searchPar = c['name']
                break
        tableCard = searchPar #tista karta, s katero moram neki ponoč narest
        for player in game:
            if player['user_id'] in tableID:
                if player['name'] == tableCard:
                    card_id = player['user_id']
                    break
        return card_id
    else:
        raise NotImplementedError('Method unknown in findUser().')
    #print('findUser userID>>', userID)
    return userID

def switch(igame, idA, idB):
    '''
    Function switches roles of player A and player B and returns refreshed game 
    Input:
        igame...list of players each in dict format
        idA, idB...ID numbers of players being switched
    Output:
        ogame...refreshed igame ro should I say reshuffled
        switched...string with a message who was switched
    '''
    ogame = transcribe(igame)
    dynogame = []
    switched = "switched "
    #saving in temp variables
    for player in igame:
        player_i = transcribe(player)
        if player_i['user_id'] == idA:
            tmpA = transcribe(player_i['role'])
            switched = switched + player_i['name'] + '(' + player_i['role'].split(' ')[0] + ') '
        elif player_i['user_id'] == idB:
            tmpB = transcribe(player_i['role'])
            switched = switched + player_i['name'] + '(' + player_i['role'].split(' ')[0] + ') '
    switched = switched + 'to '
    #switching roles
    for playa in ogame:
        playa_i = transcribe(playa)
        if playa_i['user_id'] == idA:
            playa_i['role'] = transcribe(tmpB)
            playme = transcribe(playa_i)
            switched = switched + playa_i['name'] + '(' + playa_i['role'].split(' ')[0] + ') '
        elif playa_i['user_id'] == idB:
            playa_i['role'] = transcribe(tmpA)
            playme = transcribe(playa_i)
            switched = switched + playa_i['name'] + '(' + playa_i['role'].split(' ')[0] + ') '
        else:
            playme = transcribe(playa_i)

        dynogame.append(playme)
    switched = switched + 'ID: ' + str(igame is ogame)

    return dynogame, switched

def change_status(user_id): ### NE DELA - MENJAVA SE NE UPOŠTEVA PRI .w
    '''
    Function changes status of current user to on/off. Updated dictionary is then written to hidden file .gameData.json from which this game runs
    Input:
        data...slovar igre 
        user_id...kdo hoče menjat status
    '''
    #Uvozim json podatke o igri in igralcih
    gdata = json.load(open('.gameData.json', 'r'))
    members = gdata['members']
    klik = ''
    user_name = ''
    user_id = user_id
    for member in members:
        if member['user_id']==user_id:
            user_name = member['name']
            if member['status'] == 'on':
                klik = 'off'
                member['status'] = klik
            else:
                klik = 'on'
                member['status'] = klik
    with open('.gameData.json', 'w', encoding='utf-8') as f:       
        json.dump(gdata, f, ensure_ascii=False, indent=4)
        
    return klik #to je trenutno stanje za vhodni user_id

def whos_next(game, data):
    '''
    Vrne next_role, ki je naslednji na vrsti ob upoštevanju prejšnjih vlog.
    Vsakič, ko se ta funkcija kliče se tudi premakne eno vlogo naprej. Če jo kličem 5x preskočim 5 vlog.
    Določim seznam vlog, ki se po vrsti prebujajo ponoči. Izpustim, tiste ki
    so že porihtane ob začetku igre(villager-None, werewolf-1, minion-2 in mason-3) 
    Deluje le za dinamične vloge, ker so statične zrihtane v .w\n
    Input:
        game, data...current game, data about roles(json)
    Output:
        all_roles_order...seznam vseh vlog(tudi na mizi) v nočnem vrstnem redu
        active_roles_order...seznam vlog, ki jih igrajo ljudje v nočnem vrstnem redu
    '''
    night = {} # slovar samo igralcev {'rolename':'night_order'}
    nightAll = {} # slovar vseh vlog v igri po vrsti
    all_roles_order = [] # seznam vseh vlog v igri po vrsti
    active_roles_order = [] # seznam vlog po vrsti za igralce
    cards = list(data['roles']) #role cards
    
    # sestavljam slovarja night in nightAll
    for player in game:
        just_role = player['role'].split(' ')[0]

        if player['user_id'] in [1, 2, 3] and player['played'] == False:
            for c in cards: #izpuščam statične vloge in sestavljam slovar vlog {'rolename':night_order}
                if c['night_order'] != None and c['name'] == just_role:# and (player['played'] == False): #spustim samo tiste, ki ne spijo ponoč in še niso bile na vrsti
                    nightAll[c['name']] = c['night_order']
        else:
            if player['played'] == False:   #samo če igralec še ni igral bo v končnem seznamu - tudi namizne karte morajo fake igrati, zato da ostali ne pogruntajo kdo je kdo
                for card in cards: #izpuščam statične vloge in sestavljam slovar vlog {'rolename':night_order}
                    if card['night_order'] != None and card['name'] == just_role: #spustim zaspance
                        night[card['name']] = card['night_order'] #dodam aktivno, še neigrano vlogo
                        nightAll[card['name']] = card['night_order']
    #urejam slovarje
    AllRolesOrder = collections.OrderedDict(sorted(nightAll.items(), key=lambda t:t[1]))
    ActiveRolesOrder = collections.OrderedDict(sorted(night.items(), key=lambda t:t[1]))

    # zaporedje vlog za vse vloge v igri
    for role in AllRolesOrder:
        all_roles_order.append(role)
    #print('\nall_roles_order >>>', all_roles_order)   

    # zaporedje vlog samo tiste, ki jih igrajo ljudje
    for active in ActiveRolesOrder:
        active_roles_order.append(active)   
    #print('\nactive_roles_order >>>', active_roles_order)

    if (not active_roles_order) and (not not all_roles_order):
        return all_roles_order, None #Noben aktiven več ni na vrsti
    elif (not not active_roles_order) and (not all_roles_order):
        return None, active_roles_order #Samo še aktivni so na vrsti
    else:
        return all_roles_order, active_roles_order

def openCards(cards, wolfy, listOrder, tip='dynamic'):
    '''
    END MESSAGE - This reveals all players in game and table cards and 
    forms a message to be sent on discord.\n
    Input:
        cards...game list of dictionaries, different name is to avoid same memory adresses
        wolfy...I need my bot to get real user names
        listOrder...pove v kakšnem vrstnem redu moram prikazovat karte
        tip...da vem al' izpisujem statične vloge al' končen rezultat igre
    Output:
        term...message for terminal
        msg...message for discord
    '''
    if tip == 'static':
        term = '\nSTART GAME:\n'
        msg = 'InTheBeginning:\n'
        tense = ' was ' #angleški čas past
        table_cards = '\nTable cards were...\n'
    else:
        term = '\nEND GAME:\n'
        msg = 'AtTheEnd:\n'
        tense = ' is ' #angleški čas present
        table_cards = '\nTable cards are...\n'
    
    for username in listOrder:          #končni rezultat igre
        for c in cards:  #poiščem userja, ki je trenutno v listOrder
            if c['name'] == username:
                karta = c
                break
        player_name = karta['name']
        if player_name == 'tableCard1':
            msg = msg + table_cards
        role_name = karta['role'].split(' ')[0]
        msg = msg + ' - ' + player_name + tense + role_name + '\n'
        term = term + ' - ' + player_name + ' ' + role_name + '\n'

    return term, msg