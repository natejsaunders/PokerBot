import poker

game = poker.Game(5)

game.begin_round()

for p in game.players: print([str(c) for c in p.hand])

while True:
    do = ''
    bet = 0
    print(game.info())
    action_result = {'valid': False}
    while not action_result['valid']:
        do = input('Action: ')
        if do.lower().startswith('b'):
            bet = int(input('Amount: '))
            do = 'BET'
        else:
            do = 'FOLD'

        action_result = game.action(do, bet)
        print(action_result['reason'])
    