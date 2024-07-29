from random import shuffle

class Game():

    VALID_ACTIONS = ['BET', 'FOLD']

    # How many community cards drawn each round
    ROUNDS = [3, 1, 1]

    def __init__(self, number_of_players):
        self.players = [ Player() for Player.id_counter in range(number_of_players)]
    
        # Setting starting chips
        for player in self.players:
            player.chips = 500

        self.big_blind = 3
        self.small_blind = 1

        self.button_player = 0


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
        self.current_player_turn =  self.button_player + 2 % len(self.players)

        self.previous_bet = self.big_blind

        # Subtracting big and small blind
        self.pot = self.big_blind + self.small_blind
        self.players[max(self.button_player - 1, 0)].chips -= self.small_blind
        self.players[min((self.button_player + 1), len(self.players) - 1)].chips -= self.big_blind

        # Setting up initial cards
        self.community = []
        for i in range(5): self.community.append(self.deck.pop())
        for player in self.players:
            for i in range(2): player.hand.append(self.deck.pop())
        
        #self.players_in = self.players.copy()
        self.cards_revealed = 0

    # Return info for players to use
    def info(self):
        return { 'community': [str(self.community[i]) for i in range(self.cards_revealed)],
                 'hand': [str(c) for c in self.get_current_player().hand] }

    # Returns whether the action was valid or not
    def action(self, action, amount=0):
        if action not in Game.VALID_ACTIONS: return False

        player = self.get_current_player()

        if action == 'FOLD':

            player.is_out = True

            if len(self.get_players_in()) == 1:
                self.end_round()
                return True
        elif action == 'BET':
            if amount < self.previous_bet:
                return False
            elif amount < player.chips:
                return False
            elif amount != self.previous_bet and amount < self.previous_bet * 2:
                return False
            
            self.previous_bet = amount
            self.pot += amount
            player.chips -= amount
        
        self.current_player_turn += 1

    def get_current_player(self):
        if self.current_player_turn >= len(self.players): self.current_player_turn %= len(self.players)
        current_player = self.players[self.current_player_turn]

        while current_player.is_out:
            if self.current_player_turn >= len(self.players): self.current_player_turn %= len(self.players)
            current_player = self.players[self.current_player_turn]
            self.current_player_turn += 1

        return current_player
    
    def get_players_in(self):
        p_in = []
        for p in self.players:
            if not p.is_out:
                p_in.append(p)
        return p_in

    # Finalise round if everyone folds or if it goes to heads up
    def end_round(self):
        if len(self.get_players_in()) == 0:
            pass
        elif len(self.get_players_in()) == 1:
            self.get_players_in()[0].chips += self.pot
        else:
            # Work out winner or split pot
            pass

        self.button_player += 1
        if self.button_player >= len(self.players):
            self.button_player = 0

class Player():

    id_counter = 0

    def __init__(self):
        self.id = Player.id_counter

        self.hand = []
        self.chips = 0

        self.is_out = False


class Card():
    def __init__(self, suit, value):
        self.suit = suit
        self.value= value

    def __str__(self):
        suits = [ '♠', '♣', '♡', '♢' ]
        values = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        return suits[self.suit] + values[self.value]
