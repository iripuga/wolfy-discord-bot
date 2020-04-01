'''
Modul za igro werewolfes preko discorda.
'''
from random import shuffle, randint
from numpy import linspace
import json
import collections
from discord.ext.commands import Bot
wolfy = Bot(command_prefix='.')

#Uvozim json podatke o igri in igralcih
data = json.load(open('.game_data.json', 'r'))

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
    for mix in range(1351):   #every day i'm shuffling...premiksam, da je izbira vlog naključna
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
    else:
        raise NotImplementedError('Data type of \'igame\' unknown')
    return ogame

def list_active_roles(game_roles):
    #Dobim seznam imen vlog iz slovarja {id: role}. Samo imena vlog
    justroles=''

    print('game >>>', game_roles, '\n')
    for mix in range(1042):
        shuffle(game_roles)
    print('shuffled >>>', game_roles, '\n')
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
                user = wolfy.get_user(player['user_id'])
                list4msg = list4msg + ' - '+ str(user.name) + '\n'
                players4role[user.name] = user.id  #samo ime je dovolj za pošiljat
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
    Finds role in active game data, by searching for its rolename. Returns discord object User\n
    Input:
        igame...game data in list, each element is a dict
        searchPar...search parameter to help me find my user. Possible combinations:\n
         - par2find = rolename, method='by_rolename'
         - par2find = discord username, method='by_username'
         - par2find = 'tableCard#', method='on_table' !!!Tukaj izjemoma vrnem kar id, ker ne morem narest wolfy objekta!!!
        wolfy...ma bot
        method...na kakšen način iščem uporabnika
    Output:
        user...discord object User - player who we are looking for by searchPar
    '''
    game = transcribe(igame)
    tableID = [1, 2, 3]
    user = None
    if method == 'by_rolename':
        rolename = searchPar
        rolename.upper();
        for player in game:
            if (player['role'].split(' ')[0] == rolename) and (player['user_id'] not in tableID):
                user = wolfy.get_user(player['user_id'])
                break
    elif method == 'by_username':
        username = searchPar
        for player in game:
            if (player['name'] == username) and (player['user_id'] not in tableID):
                user = wolfy.get_user(player['user_id'])
                break
    elif method == 'on_table':
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
    return user

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
    print('id(igame) >>>', id(igame))
    for player in igame:
        #print('player >>>', player)
        #print('player_i >>>', transcribe(player))
        player_i = transcribe(player)
        if player_i['user_id'] == idA:
            tmpA = transcribe(player_i['role'])
            print('id(tmpA) >>>', id(tmpA))
            print('id(player_i) >>>', id(player_i))
            switched = switched + player_i['name'] + '(' + player_i['role'].split(' ')[0] + ') '
        elif player_i['user_id'] == idB:
            tmpB = transcribe(player_i['role'])
            print('id(tmpB) >>>', id(tmpB))
            print('id(player_i >>>', id(player_i))
            switched = switched + player_i['name'] + '(' + player_i['role'].split(' ')[0] + ') '
    switched = switched + 'to '
    #switching roles
    print('id(ogame) >>>', id(ogame))
    for playa in ogame:
        #print('>>> playa_i', playa)
        playa_i = transcribe(playa)
        #print('>>> playa_i', playa_i)
        if playa_i['user_id'] == idA:
            playa_i['role'] = transcribe(tmpB)
            playme = transcribe(playa_i)
            print('id(playa_iB) >>>', id(playme))
            #print('id(playa_i) >>>', id(playa_i))
            switched = switched + playa_i['name'] + '(' + playa_i['role'].split(' ')[0] + ') '
        elif playa_i['user_id'] == idB:
            playa_i['role'] = transcribe(tmpA)
            playme = transcribe(playa_i)
            print('id(playa_iA) >>>', id(playme))
            switched = switched + playa_i['name'] + '(' + playa_i['role'].split(' ')[0] + ') '
        else:
            playme = transcribe(playa_i)

        dynogame.append(playme)
    switched = switched + 'ID: ' + str(igame is ogame)

    return dynogame, switched

def change_status(user_id): ### NE DELA - MENJAVA SE NE UPOŠTEVA PRI .w
    '''
    Function changes status of current user to on/off. Updated dictionary is then written to hidden file .game_data.json from which this game runs
    Input:
        data...slovar igre 
        user_id...kdo hoče menjat status
    '''
    #Uvozim json podatke o igri in igralcih
    gdata = json.load(open('.game_data.json', 'r'))
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
    with open('.game_data.json', 'w', encoding='utf-8') as f:       
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
    Important vars:
        active_roles_order...seznam vlog, za ponoč v vrstnem redu
        night...slovar {'rolename':'night_order'}
    Output:
        next_role...naslednji night_role, tip int
    '''
    night = {}; active_roles_order = [] #hranim iste podatke samo na drugačen način
    cards = data['roles'] #role cards
    for player in game:
        if player['user_id'] in [n+1 for n in range(3)]:
            pass
        else:
            if player['played'] == False:   #samo če še ni igral bo v končnem seznamu
                active_role = player['role'].split(' ')[0]
                for card in cards: #izpuščam statične vloge in sestavljam slovar vlog {'rolename':night_order}
                    if (card['night_order'] != None) and (card['night_order'] > 3): #spustim prve 4
                        if card['name'] == active_role:
                            night[card['name']] = card['night_order'] #dodam aktivno, še neigrano vlogo
    
    nightOrder = collections.OrderedDict(sorted(night.items(), key=lambda t:t[1]))
    
    for active in nightOrder:
        active_roles_order.append(active)   
    if active_roles_order == []:
        return None #Noben več ni na vrsti
    #print('b', night)
    print('a', active_roles_order)

    #ta prva dinamična vloga je SEER 
    #active, active_roles_order = at_night(game, data) #slovar, urejen seznam vseh aktivnih vlog
    next_rolename = active_roles_order[0]   #noben od teh še ni igral
    for player in game:
        playersRole = player['role'].split(' ')[0]
        if playersRole == next_rolename:
            next_role = playersRole #tuki dobim številko, ki pove katera vloga je na vrsti
            player['played'] = True #ta igralec je zdaj zabeležen, kot da je že odigral
        #od zdaj naprej KODIRAM direkt z imeni, saj so že po vrsti urejena v seznam
    return next_role

def openCards(cards, wolfy, tip='dynamic'):
    '''
    This reveals all players in game and table cards and forms a message
    to be sent on discord.\n
    Input:
        cards...game list of dictionaries, different name is to avoid same memory adresses
        wolfy...I need my bot to get real user names
        type...za izpisat statične vloge in ne končne
    Output:
        term...message for terminal
        msg...message for discord
    '''
    if tip == 'static':
        term = '\n<<< START GAME >>>\n'
        msg = 'InTheBeginning:\n'
        table_cards = '\nTable cards were\n'
    else:
        term = '\n<<< END GAME >>>\n'
        msg = 'AtTheEnd:\n'
        table_cards = '\nTable cards are\n'
    
    for player in cards:          #končni rezultat igre
        playerID = player['user_id']
        #show table cards
        if playerID in [(n+1) for n in range(3)]:
            role_name = player['role'].split(' ')[0]
            table_cards = table_cards + ' - ' + role_name + '\n'
            term = term + 'tableCard' + str(playerID) + ' ' + role_name + '\n'
        else:
            user = wolfy.get_user(playerID)
            player_name = user.name
            role_name = player['role'].split(' ')[0]
            msg = msg + ' - ' + player_name + ' was ' + role_name + '\n'
            term = term + player_name + ' ' + role_name + '\n'
    msg = msg + table_cards

    return term, msg











### For testing
testgame = [#{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'SEER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False}, 
                {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': 'DRUNK - ', 'played':False}, 
                {'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'ROBBER - ', 'played':False},
                {'name': 'kristof', 'user_id': 689072253002186762, 'status': 'on', 'role': 'VILLAGER - ', 'played':False}, 
                {'name': 'tableCard1', 'user_id': 1, 'status': 'on', 'role': 'SEER - ', 'played':True}, 
                {'name': 'tableCard2', 'user_id': 2, 'status': 'on', 'role': 'WEREWOLF - ', 'played':True}, 
                {'name': 'tableCard3', 'user_id': 3, 'status': 'on', 'role': 'MINION - ', 'played':True}]
usr_id = 689399469090799848
victim_id = 593722710706749441
#static = testgame#ww.assign_roles(data)  #dobim list vseh članov, ki so v igri -> To je dinamična igra, ki se skos spreminja
#dynamic = transcribe(static) #ta se bo spreminjala







####################################################### DUMP #####################################################
'''
choice = 't1'
for c in static:
    shortName = c['name'][0] + c['name'][-1]
    if shortName == choice:
        print(choice, '>>>', c['name'])
        choice = c['name']
        print(choice)
        break
card_id = findUser(static, wolfy, choice, method='on_table')
print(card_id)
'''

'''
choice = 'JanezDobrivnik'
print('\nstatic is dynamic?', static is dynamic, '\nstatic >>>\n', id(static), static)
print('dynamic >>>\n', id(dynamic), dynamic)
print('\nDO STUFF!\n')
#victim = findUser(dynamic, wolfy, choice, method='by_username')
dynamic, switch_msg = switch(dynamic, robber_id, victim_id)   #rob the victim
print('static is dynamic?', static is dynamic, '\nstatic >>>\n', id(static), static)
print('dynamic >>>\n', id(dynamic), dynamic)
print('MSG: ' + switch_msg)
'''


'''
def _assign_roles0(idata=data, desires=None):   
    
    Shuffle new roles for another game of werewolfes
    Input:
        idata...role and members data dictionary(look up)
        desires...list of desired roles which must match len(players)
    Output:
        assigned...dict of reshuffled 'roles with ther description' in one string. Format is {'user_id': 'role-description'}.
    
    #init variables
    assigned = {}
    playersID = activate(data['members']) #get list of active player id's which need role assignment
    roles = data['roles']
    r_idx = []
    
    #določim indexe za vloge iz seznama members. samo toliko kot je igralcev v igri
    for num in range(len(playersID)):   
        r_idx.append(num)
    for i in range(1351):   #every day i'm shuffling...premiksam, da je izbira vlog naključna
        shuffle(r_idx)  
        
    #Če ma kdo kake želje katere vloge naj bodo v igri, je zdaj čas, da pove    
    if desires == None:
        i = 0
        for playerID in playersID:
            get_role = int(r_idx[i]) #poiščem vlogo glede na index v seznamu premešanih indeksov
            i = i + 1
            ROLE = roles[get_role]['name'] + ' - ' + roles[get_role]['description']
            assigned[str(playerID)] =  ROLE    #sproti dodajam nove elemente v slovar 
    else:
        raise NotImplementedError('No desires!') #Tukaj pridejo želje
        
    return assigned  #dodeljene vloge

def at_night(game, data): #lahko bi dodal, da samo vprašam kdo je naslednji
    Vrne seznam vlog, ki se po vrsti prebujajo ponoči. Izpustim, tiste ki
    so že porihtane ob začetku igre(villager-None, werewolf-1, minion-2 in mason-3) 
    Vars:
        active_roles_order...seznam vlog, za ponoč v vrstnem redu
        night...slovar {'rolename':'night_order'}
    night = {}
    active_roles_order = []
    cards = data['roles'] #role cards
    for player in game:
        if player['played'] == False:   #samo če še ni igral bo v končnem seznamu
            active_role = player['role'].split(' ')[0]
            for card in cards: #izpuščam statične vloge in sestavljam slovar vlog {'rolename':night_order}
                if (card['night_order'] != None) and (card['night_order'] > 3):# and (card['night_order'] != 1) and (card['night_order'] != 2) and (card['night_order'] != 3):
                    if card['name'] == active_role:
                        night[card['name']] = card['night_order']
    nightOrder = collections.OrderedDict(sorted(night.items(), key=lambda t:t[1]))
    for active in nightOrder:
        active_roles_order.append(active)
    return night, active_roles_order
'''
##################################################################################################################