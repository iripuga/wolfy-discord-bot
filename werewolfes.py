'''
Modul za igro werewolfes preko discorda.
'''
from random import shuffle, randint
from numpy import linspace
import json
import collections

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

def list_active_roles(game_roles):
    #Dobim seznam imen vlog iz slovarja {id: role}. Samo imena vlog
    justroles=''
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
    list4msg = f' - To abstain from your power type: <w.{rolename.lower()} abstain>\n'  #list4msg...string formated list for easier output
    players4role = {}
    for player in game:
        if player['name'] in ['tableCard' + str(n+1) for n in range(3)]:    #za tableCards ne morem narest wolfy objekta user
            list4msg = list4msg + ' - '+ player['name'] + '\n'
            players4role[player['name']] = player['user_id']
        else:
            if player['role'].split(' ')[0] != rolename:  #vloga, ki je na vrsti ne sme bit na tem seznamu
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
        command = 'COMMAND: w.troublemaker <player1> <player2>'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'DRUNK':
        nice = 'Your\'re too drunk to do anything really, but you can play you role. You might become someone else...\n' + list4msg
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.drunk'
        msg2 = f'```yaml\n{command}\n```'
    elif rolename == 'INSOMNIAC':
        nice = 'Your turn! Check if you still have trouble sleeping.\n' + list4msg
        msg1 = f'```\n{nice}\n```'
        command = 'COMMAND: w.drunk'
        msg2 = f'```yaml\n{command}\n```'


    msg = msg1 + msg2
    return msg, players4role

def findUser(game, wolfy, searchPar, method='by_rolename'):
    '''
    Finds role in active game data, by searching for its rolename. Returns discord object User\n
    Input:
        game...game data in list, each element is a dict
        searchPar...search parameter to help me find my user. Possible combinations:\n
         - par2find = rolename, method='byRolename'
         - par2find = discord username, method='byUsername'
         - par2find = 'tableCard#', method='onTable' !!!Tukaj izjemoma vrnem kar id, ker ne morem narest wolfy objekta!!!
        wolfy...ma bot
        method...na kakšen način iščem uporabnika
    Output:
        user...discord object User - player who we are looking for by searchPar
    '''
    tableID = [1, 2, 3]
    if method == 'by_rolename':
        rolename = searchPar
        rolename.upper();
        user = None;
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
    ogame = igame
    switched = "switched "
    #saving in temp variables
    for player in igame:
        if player['user_id'] == idA:
            tmpA = player['role']
            switched = switched + player['name'] + '(' + player['role'].split(' ')[0] + ') '
        elif player['user_id'] == idB:
            tmpB = player['role']
            switched = switched + player['name'] + '(' + player['role'].split(' ')[0] + ') '
    switched = switched + 'to '
    #switching roles
    for player in ogame:
        if player['user_id'] == idA:
            player['role'] = tmpB
            switched = switched + player['name'] + '(' + player['role'].split(' ')[0] + ') '
        elif player['user_id'] == idB:
            player['role'] = tmpA
            switched = switched + player['name'] + '(' + player['role'].split(' ')[0] + ') '
    return ogame, switched

def change_status(data, user_id): ### NE DELA - MENJAVA SE NE UPOŠTEVA PRI .w
    '''
    Function changes status of current user to on/off. Updated dictionary is then written to hidden file .game_data.json from which this game runs
    Input:
        data...slovar igre 
        user_id...kdo hoče menjat status
    '''
    members = data['members']
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
        json.dump(data, f, ensure_ascii=False, indent=4)
        
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
        if player['played'] == False:   #samo če še ni igral bo v končnem seznamu
            active_role = player['role'].split(' ')[0]
            for card in cards: #izpuščam statične vloge in sestavljam slovar vlog {'rolename':night_order}
                if (card['night_order'] != None) and (card['night_order'] > 3): #spustim prve 4
                    if card['name'] == active_role:
                        night[card['name']] = card['night_order'] #dodam aktivno, še neigrano vlogo
    
    nightOrder = collections.OrderedDict(sorted(night.items(), key=lambda t:t[1]))
    
    for active in nightOrder:
        active_roles_order.append(active)
    #print('b', night)
    #print('a', active_roles_order)

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














### For testing
testgame = [{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'role': 'SEER - At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'played':False}, 
            {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'on', 'role': 'ROBBER - The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win.', 'played':False}, 
            {'name': 'tableCard1', 'user_id': 1, 'status': 'on', 'role': 'TROUBLEMAKER - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
            {'name': 'tableCard2', 'user_id': 2, 'status': 'on', 'role': 'INSOMNIAC - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}, 
            {'name': 'tableCard3', 'user_id': 3, 'status': 'on', 'role': 'DRUNK - The Villager has no special ability, but he is definitely not a werewolf.', 'played':False}]
ida = 689399469090799848
idb = 593722710706749441
game = testgame#assign_roles(data)    #dict of active player:roles
#nightrole = int(input('which role turn? '))
#for playa in game:
    #print(playa['role'].split(' ')[0], playa['played'])
nextrole = whos_next(game, data)
#print('\n',nextrole,'\n')

#for playa in game:
    #print(playa['role'].split(' ')[0], playa['played'])

####################################################### DUMP #####################################################
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