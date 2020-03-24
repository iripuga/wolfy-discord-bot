'''
Modul za igro werewolfes preko discorda.
'''

some_change = 2;

from random import shuffle, randint
from numpy import linspace
import json

#Uvozim json podatke o igri in igralcih
data = json.load(open('.game_data.json', 'r'))

### Funkcije
def activate(members):
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
      


















####################################################### DUMP #####################################################
def _assign_roles0(idata=data, desires=None):   
    '''
    Shuffle new roles for another game of werewolfes
    Input:
        idata...role and members data dictionary(look up)
        desires...list of desired roles which must match len(players)
    Output:
        assigned...dict of reshuffled 'roles with ther description' in one string. Format is {'user_id': 'role-description'}.
    '''
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
################################################################################################################
















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
    players = activate(members) #get list of active player id's which need role assignment
    
    #RANDOM SHUFFLE - določim indexe za vloge iz seznama members. samo toliko kot je igralcev v igri
    r_idx = []
    for num in range(len(players)):   
        r_idx.append(num)
    for mix in range(1351):   #every day i'm shuffling...premiksam, da je izbira vlog naključna
        shuffle(r_idx)  
    
    if desires == None:
        i = 0
        for member in members:
            for playerID in players:
                if playerID == member['user_id']:
                    get_role = int(r_idx[i]) #poiščem vlogo glede na index v seznamu premešanih indeksov
                    i = i + 1
                    ROLE = roles[get_role]['name'] + ' - ' + roles[get_role]['description']

                    member['role'] = ROLE
                    assigned_roles.append(member)
                else:
                    pass
    else:
        raise NotImplementedError('No desires!')
    
    return assigned_roles

def list_active_roles(game_roles):
    #Dobim seznam imen vlog iz slovarja {id: role}. Samo imena vlog
    justroles=''
    for player in game_roles:
        role = player['role'].split(' ')[0]
        justroles = justroles + role + '\n'
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

def msg4user(player):
    '''
    Funkcija sestavi sporočilo, ki ga ob začetku igre pošljem uporabniku
    Input:
        player...slovar - podatki o igralcu
    Output:
        msg_role...sporočilo, ki gre direkt v await user.send()
        sameRoles...dict of players with same role {rolename: [ID of players with this role]}
    '''
    role = player['role']
    role_name = role.split(' ')[0]
    msg_role = f"👀\n{role}\nGo get \'em! 👋"
    
    return msg_role
    
def change_status(data, user_id): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! MENJAVA SE NE UPOŠTEVA PRI !w
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
        















### For testing
game = assign_roles(data)    #dict of active player:roles
msg1 = msg4user(game[0])


'''
justroles = list_active_roles(game)
justid = list_active_id(game)
print(game)
print()
print(justroles)
print(justid)
#print(type(justid[0]),'\n')
print(msg1, msg2)





i = 0
for player in active.keys():
    player = str(player)
    print(f'{player} is #{active[player]}')
'''