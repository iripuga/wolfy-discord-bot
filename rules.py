'''
Edit and update .json data for werewolfes game - ZORC wass hier
'''
import json

### json DATA for game functionalities
data = {
    'members':
        [{'name': 'iripuga', 'user_id': 689399469090799848, 'status': 'on', 'played': False}, 
         {'name': 'rok', 'user_id': 261105970548178944, 'status': 'off', 'played': False},
         {'name': 'zorkoporko', 'user_id': 593722710706749441, 'status': 'off', 'played': False},
         {'name': 'kristof', 'user_id': 689072253002186762, 'status': 'off', 'played': False},
         {'name': 'klemzo', 'user_id': 641347330804678667, 'status': 'off', 'played': False},
         {'name': 'lovric', 
          'user_id': 702488609478934630,# TODO - 548304226988720149: 548304226988720149, #za lovriča je 'user_id' v resnici id od channelja "#wolfy" na serverju "#Lovric", ker pač mora bit neki posebnega
          'status': 'on', 
          'played': False}, 
         {'name': '5ra404', 'user_id': 314081364414562325, 'status': 'off', 'played': False},
         {'name': 'tableCard1', 'user_id': 1, 'status': 'on', 'played': False},  #tri karte na sredini mize - vse morajo navidezno igrati igro
         {'name': 'tableCard2', 'user_id': 2, 'status': 'on', 'played': False},
         {'name': 'tableCard3', 'user_id': 3, 'status': 'on', 'played': False}],
    'roles':
       [#{'name': 'VILLAGER', 'description': 'The Villager has no special ability, but he is definitely not a werewolf.', 'night_order': None},  #lohk jih kr tuki razporediš po zaporednih številkah. Če se nč z vlogo ne zgodi je order 0
       	#{'name': 'VILLAGER', 'description': 'The Villager has no special ability, but he is definitely not a werewolf.', 'night_order': None},
        #{'name': 'VILLAGER', 'description': 'The Villager has no special ability, but he is definitely not a werewolf.', 'night_order': None},
        #{'name': 'WEREWOLF', 'description': 'At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'night_order': 1},
	    {'name': 'WEREWOLF', 'description': 'At night all Werewolves open their eyes and look for other werewolves. If no one else opens their eyes, the other werewolves are in the center.', 'night_order': 1},
        #{'name': 'MASON', 'description': 'The Mason wakes up at night and looks for the other Mason. If the Mason doesnt see another Mason, it means the other Mason is in the center.', 'night_order': 3}, 
	    {'name': 'MASON', 'description': 'The Mason wakes up at night and looks for the other Mason. If the Mason doesnt see another Mason, it means the other Mason is in the center.', 'night_order': 3},
	    {'name': 'ROBBER', 'description': 'At night, the Robber may choose to rob a card from another player and place his Robber card where the other card was. Then the Robber looks at his new role card.', 'night_order': 5},
	    {'name': 'TROUBLEMAKER', 'description': 'At night the Troublemaker may switch the cards of two other players without looking at those cards.', 'night_order': 6},
       	{'name': 'SEER', 'description': 'At night, the Seer may look eighter at one other players card or at two of the center cards, but does not move them.', 'night_order': 4},
        {'name': 'INSOMNIAC', 'description': 'The Insomniac wakes up and looks at their card (to see if it has changed).', 'night_order': 8},
	    {'name': 'DRUNK', 'description': 'The Drunk exchanges his card with a card from the center, they do not look at their new role.', 'night_order': 7},
        {'name': 'MINION', 'description': 'The Minion wakes up and sees who the Werewolves are. If the Minion dies and no Werewolves die, the Minion and the Werewolves win.', 'night_order': 2},
        {'name': 'HUNTER', 'description': 'If the Hunter dies, the player he is pointing at dies as well.', 'night_order': None},
        {'name': 'TANNER', 'description': 'The Tanner is on his own team and he wins only if he gets killed.', 'night_order': None}], 
    }

with open('.gameData.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print('\nActive roles:')
for role in data['roles']:
    print(role['name'])

print('\nActive players:')
for player in data['members']:
    if (player['status'] == 'on') and (player['user_id'] not in [1,2,3]):
        print(player['name'])
print()
