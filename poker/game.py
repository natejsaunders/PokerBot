from random import shuffle

class Game():

    VALID_ACTIONS = ['RAISE', 'CALL', 'FOLD']

    def __init__(self, number_of_players):
        self.players = [ Player() for Player.id_counter in range(number_of_players)]
    
        # Setting starting chips
        for player in self.players:
            player.chips = 500

    def reset_cards(self):
        # Generating standard deck
        self.deck = []
        for i in range(52):
            self.deck.append(Card(i % 4, i // 4))
        shuffle(self.deck)
        
        for player in self.players:
            player.hand = []

    # Starts a game of poker
    def begin_round(self):
        self.reset_cards()
        
        # ID of the current players turn
        self.current_player_turn = 0

        self.pot = 0

        # Setting up initial cards
        self.community = []
        for i in range(5): self.community.append(self.deck.pop())
        for player in self.players:
            for i in range(2): player.hand.append(self.deck.pop())
        
        self.players_in = self.players.copy()
        self.cards_revealed = 0

    # Return info for players to use
    def info(self):
        return { 'community': [self.community[i] for i in range(self.cards_revealed)],
                 'hand': self.players[self.current_player_turn].hand }

    # Returns whether the action was valid or not
    def action(self, action, amount=0):
        if action not in Game.VALID_ACTIONS: return False

        if action == 'FOLD':
            if len(self.players_in) == 1: 
                self.end_round()
                return True

    # Finalise round if everyone folds or if it goes to heads up
    def end_round(self):
        if len(self.players_in) == 0:
            return
        elif len(self.players_in) == 1:
            self.players_in[0].chips += self.pot
            return
        else:
            # Work out winner or split pot
            pass
        


class Player():

    id_counter = 0

    def __init__(self):
        self.id = Player.id_counter

        self.hand = []
        self.chips = 0


class Card():
    def __init__(self, suit, value):
        self.suit = suit
        self.value= value

    def __str__(self):
        suits = [ '♠', '♣', '♡', '♢' ]
        values = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        return suits[self.suit] + values[self.value]
