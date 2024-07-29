import poker

game = poker.Game(5)

game.begin_round()

for p in game.players: print([str(c) for c in p.hand])

for i in range(5):
    print(game.info())
    game.action('FOLD')