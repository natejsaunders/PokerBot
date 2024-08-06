import poker



game = poker.Game(5)

for i in range(5): game.add_player(i)

go_id = 3

game.begin_round()

# while True:
#     do = ''
#     bet = 0
#     print(game.info())
#     action_result = {'valid': False}
#     while not action_result['valid']:
#         do = input('Action: ')
#         if do.lower().startswith('b'):
#             bet = int(input('Amount: '))
#             do = 'BET'
#         else:
#             do = 'FOLD'

#         action_result = game.action(do, bet)
#         print(action_result['reason'])


action_result = {'valid': True, 'reason': ""}
while action_result['reason'] != "End of round":
    go_id %= 5

    do = 'BET'
    gi = game.info()
    print(gi)
    action_result = {'valid': False}
    bet = max(gi['player_chips_in']) - gi['chips_in']
    action_result = game.action(go_id, do, bet)

    print(action_result['reason'])

    go_id += 1

end_gi = game.info()
print(end_gi)

# test_p = poker.Player()
# test_p.hand = [poker.Card(0, 7), poker.Card(0, 0)]
# community_test = [poker.Card(2, 9), poker.Card(3, 8), poker.Card(1, 6), poker.Card(2, 2), poker.Card(0, 11)]

# print(test_p.calculate_score(community_test))