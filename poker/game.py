from random import shuffle

class Game():

    VALID_ACTIONS = ['BET', 'FOLD']
    CARDS_REVEALED = [3, 4, 5]

    def __init__(self, number_of_players):
        self.players = [ Player() for Player.id_counter in range(number_of_players)]
    
        # Setting starting chips
        for player in self.players:
            player.chips = 500

        self.big_blind = 2
        self.small_blind = 1

        self.button_player = 0

        self.round_going = False
        self.awaiting_action = False


    def reset_cards(self):
        # Generating standard deck
        self.deck = []
        self.community = []
        for i in range(52):
            self.deck.append(Card(i % 4, i // 4))
        shuffle(self.deck)
        
        for player in self.players:
            player.hand = []

    # Starts a game of poker
    def begin_round(self):
        if self.round_going: return
        self.round_going = True

        self.reset_cards()
        
        # ID of the current players turn
        self.current_player_turn =  self.players[(self.button_player + 2) % len(self.players)].id

        # Setting up initial cards
        for i in range(5): self.community.append(self.deck.pop())
        for player in self.players:
            for i in range(2): player.hand.append(self.deck.pop())
            player.chips_in = 0
            player.is_out = False

            
        # Subtracting big and small blind
        self.pot = self.big_blind + self.small_blind
        self.players[max(self.button_player - 1, 0)].chips -= self.small_blind
        self.players[max(self.button_player - 1, 0)].chips_in = self.small_blind
        self.players[min((self.button_player + 1), len(self.players) - 1)].chips -= self.big_blind
        self.players[min((self.button_player + 1), len(self.players) - 1)].chips_in = self.big_blind
        
        self.cards_revealed = 0
        self.action_counter = 0
        self.awaiting_action = True

        self.round_count = 0

        self.players_in = self.players.copy()

    # Return info for players to use
    def info(self, player_id=0):
        if self.awaiting_action:
            return { 'community': [str(self.community[i]) for i in range(self.cards_revealed)],
                    'hand': [str(c) for c in self.get_current_player().hand],
                    'chips': self.get_current_player().chips,
                    'pot': self.pot,
                    'player_chips': [p.chips for p in self.players],
                    'player_chips_in': [p.chips_in for p in self.players_in] }
        else:
            return False
    
    # Cycles through players until all have bet the same amount
    def new_betting_round(self):
        self.cards_revealed = Game.CARDS_REVEALED[min(self.round_count, 2)]

        # Final betting round end game round
        if self.round_count >= 3: self.end_round()

        self.current_player_turn =  self.button_player + 2 % len(self.players)

        for in_player in self.players_in:
            in_player.chips_in = 0
            in_player.had_go = False

        self.round_count += 1

    # Returns whether the action was valid or not
    def action(self, action, amount=0):
        if not self.awaiting_action: return { 'valid': False, 'reason': "Game not ready for actions" }
        if action not in Game.VALID_ACTIONS: return { 'valid': False, 'reason': f"Invalid action: {action}" }

        player = self.get_current_player()

        if action == 'FOLD':

            self.players_in.remove(player)

            if len(self.players_in) == 1:
                self.end_round()

            self.current_player_turn %= len(self.players_in)

            return { 'valid': True, 'reason': "Fold successful" }
                
        elif action == 'BET':
            if amount+self.get_current_player().chips_in < self.get_current_player(-1).chips_in:
                return { 'valid': False, 'reason': f"Bet not high enough, previous is {self.get_current_player(-1).chips_in}" }
            elif amount > player.chips:
                return { 'valid': False, 'reason': f"Player does not have enough chips to make a bet of {amount}" }
            elif amount+self.get_current_player().chips_in != self.get_current_player(-1).chips_in and amount+self.get_current_player().chips_in < self.get_current_player(-1).chips_in * 2:
                return { 'valid': False, 'reason': f"Player must bet at least 2x the previous bet of {self.get_current_player(-1).chips_in} to raise" }
            
            self.pot += amount
            player.chips -= amount
            player.chips_in += amount

            self.get_current_player().had_go = True

            # Checking if betting should be over (all players same amount in or folded)
            betting_round_over = True
            for p in self.players_in:
                if p.id == player.id: pass
                if p.chips_in < player.chips_in or not p.had_go:
                    betting_round_over = False
                    break

            if betting_round_over: self.new_betting_round()
            
            self.current_player_turn = ((self.current_player_turn + 1) % len(self.players_in))
            return { 'valid': True, 'reason': "Bet successful" }
        
        return { 'valid': False, 'reason': "Unknown Error lol" }

    def get_current_player(self, offset=0):
        # Get index in players of current players turn
        
        return self.players_in[self.current_player_turn]

    # Finalise round if everyone folds or if it goes to heads up
    def end_round(self):
        self.awaiting_action = False

        if len(self.players_in) == 0:
            pass
        elif len(self.players_in) == 1:
            self.players_in[0].chips += self.pot
        else:
            # Work out winner or split pot
            pass

        self.button_player += 1
        if self.button_player >= len(self.players):
            self.button_player = 0

    def get_player_from_id(self, id):
        for p in self.players:
            if p.id == id: return p
        return None

class Player():

    id_counter = 0

    def __init__(self):
        self.id = Player.id_counter

        self.hand = []
        self.chips = 0
        self.chips_in = 0

        # All players must get a go before a betting round ends
        self.had_go = False


class Card():
    def __init__(self, suit, value):
        self.suit = suit
        self.value= value

    def __str__(self):
        suits = [ '♠', '♣', '♡', '♢' ]
        values = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

        return suits[self.suit] + values[self.value]
