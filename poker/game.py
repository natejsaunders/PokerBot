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

        self.end_round_info = {

        }

    # Return info for players to use
    def info(self, player_id=0):
        if self.awaiting_action:
            return { 'community': [str(self.community[i]) for i in range(self.cards_revealed)],
                    'hand': [str(c) for c in self.get_current_player().hand],
                    'chips': self.get_current_player().chips,
                    'chips_in': self.get_current_player().chips_in,
                    'pot': self.pot,
                    'player_chips': [p.chips for p in self.players],
                    'player_chips_in': [p.chips_in for p in self.players_in] }
        else:
            return self.end_round_info
    
    # Cycles through players until all have bet the same amount
    # Return whether to continue the game
    def new_betting_round(self):
        self.cards_revealed = Game.CARDS_REVEALED[min(self.round_count, 2)]

        # Final betting round end game round
        if self.round_count >= 3: 
            self.end_round()
            return False

        self.current_player_turn =  self.button_player + 2 % len(self.players)

        for in_player in self.players_in:
            in_player.chips_in = 0
            in_player.had_go = False

        self.round_count += 1
        
        return True

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

            if betting_round_over: 
                if not self.new_betting_round(): return { 'valid': True, 'reason': "End of round" }
            
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

            self.end_round_info = {
                'winners': [self.players_in[0]],
                'winnings': self.pot
            }
        else:
            # Work out winner or split pot
            winning_players = [self.players_in[0]]
            winning_players[0].score = winning_players[0].calculate_score(self.community)
            for player in self.players_in:
                if player in winning_players: continue
                player.score = player.calculate_score(self.community)

                if player.score == winning_players[0].score:
                    winning_players.append(player)
                else:
                    better = False
                    for h in range(min(len(player.score), len(winning_players[0].score))):
                        if player.score[h][0] > winning_players[0].score[h][0]:
                            better = True
                            break
                        elif player.score[h][0] < winning_players[0].score[h][0]:
                            break
                        else:
                            if player.score[h][1] > winning_players[0].score[h][1]:
                                better = True
                                break
                    if better: winning_players = [player]

            to_get = self.pot // len(winning_players)
            for p in winning_players: p.chips += to_get

            self.end_round_info = {
                'winners': [winning_players],
                'winnings': to_get
            }
            print(self.score_to_english(winning_players[0].score))


        self.button_player = (self.button_player + 1) % len(self.players)

    def get_player_from_id(self, id):
        for p in self.players:
            if p.id == id: return p
        return None

    # Turns a score (which is basically unreadable) into nice english
    def score_to_english(self, score):
        if score[0] == (10, 14): return "Royal Flush"
        elif score[0][0] == 10: return f"{Card.value_to_str(score[0][1])} high Straigh Flush"
        elif score[0][0] == 9: return f"{Card.value_to_str(score[0][1])} Quads with a {Card.value_to_str(score[1][1])} kicker"
        elif score[0][0] == 8: return f"{Card.value_to_str(score[0][1])}'s full of {Card.value_to_str(score[1][1])}'s"
        elif score[0][0] == 6: return f"{Card.value_to_str(score[0][1])} high Flush"
        elif score[0][0] == 5: return f"{Card.value_to_str(score[0][1])} high Straight"
        elif score[0][0] == 4: return f"{Card.value_to_str(score[0][1])} Trips with {Card.value_to_str(score[1][1])}, {Card.value_to_str(score[2][1])} kickers"
        elif score[0][0] == 3: return f"{Card.value_to_str(score[0][1])}, {Card.value_to_str(score[1][1])} Two Pair with a {Card.value_to_str(score[2][1])} kicker"
        elif score[0][0] == 1: return f"{Card.value_to_str(score[0][1])} Pair with {Card.value_to_str(score[1][1])}, {Card.value_to_str(score[2][1])}, {Card.value_to_str(score[3][1])} kickers"
        elif score[0][0] == 0: return f"High cards {Card.value_to_str(score[0][1])}, {Card.value_to_str(score[1][1])}, {Card.value_to_str(score[2][1])}, {Card.value_to_str(score[3][1])}, {Card.value_to_str(score[4][1])}, "

class Player():

    id_counter = 0

    def __init__(self):
        self.id = Player.id_counter

        self.hand = []
        self.chips = 0
        self.chips_in = 0

        # All players must get a go before a betting round ends
        self.had_go = False

        self.score = []#[0 for i in range(9)]

    # Calculates a score
    # straight flush, quads, (full housex2), flush, straight, trips, (two pairx2), pair, high card
    def calculate_score(self, community):
        score = []

        cards = community + self.hand
        score_matrix = [[0 for i in range(14)] for ii in range(4)]

        for card in cards:
            score_matrix[card.suit][card.value] += 1
            # For Aces
            if card.value == 0:
                score_matrix[card.suit][13] += 1

        # Straight flush
        straight_count = 0
        highest_value = 0
        for suit in score_matrix:
            for i in range(len(suit)):
                value = suit[i]
                if value == 1:
                    straight_count += 1
                    highest_value = i
                elif straight_count < 5:
                    straight_count = 0
            if straight_count >= 5:
                return [(10, highest_value)]
            straight_count = 0
        
        # Quads
        value_counts = [0 for i in range(14)]
        for suit in score_matrix:
            for i in range(len(suit)):
                value_counts[i] += suit[i]
        if 4 in value_counts:
            score.append((9, value_counts.index(4)))
            highest_other_value = 0
            for i in range(len(value_counts)):
                if i > highest_other_value and value_counts[i] != 4 and value_counts[i] > 0:
                    highest_other_value = i
            score.append((0, highest_other_value))
            return score

        # Full House
        highest_three = 0
        highest_two = 0
        for i in range(len(value_counts)):
            if value_counts[i] == 3 and i > highest_three:
                highest_three = i
            if value_counts[i] == 2 and i > highest_two:
                highest_two = i
        if highest_two > 0 and highest_three > 0:
            score.append((8, highest_three))
            score.append((7, highest_two))
            return score
        
        # Flush
        suit_count = 0
        highest_in_suit = 0
        for suit in score_matrix:
            for i in range(len(suit)):
                suit_count += 1
                if i > highest_in_suit: highest_in_suit = i
            suit_count = 0
        if suit_count >= 5:
            return [(6, highest_in_suit)]
        
        # Straight
        straight_count = 0
        highest_value = 0
        for i in range(len(value_counts)):
            value = value_counts[i]
            if value > 0:
                straight_count += 1
                highest_value = i
            elif straight_count < 5:
                straight_count = 0
        if straight_count >= 5:
            return [(5, highest_value)]
        
        r = value_counts.copy()
        r.reverse()

        # Trips
        if highest_three > 0:
            score.append((4, highest_three))
            for i in range(len(r)):
                if r[i] != 3 and r[i] > 0:
                    score.append((0, len(r) - i - 1))

                    if len(score) >= 3: return score

        # Two Pair
        pair_count = value_counts.count(2)
        if highest_two == 13: pair_count -= 1 # Special case for aces
        if pair_count >= 2:
            score.append((3, highest_two))
            for i in range(len(r)):
                if r[i] == 2 and len(r) - i - 1 < highest_two:
                    score.append((2, len(r) - i - 1))
                    break
            for i in range(len(r)):
                if r[i] == 1:
                    score.append((0, len(r) - i - 1))
                    return score
                
        # Pair
        if pair_count == 1:
            score.append((1, highest_two))
            for i in range(len(r)):
                if r[i] == 1:
                    score.append((0, len(r) - i - 1))
                    if len(score) >= 4: return score

        # High Cards
        for i in range(len(r)):
            if r[i] == 1:
                score.append((0, len(r) - i - 1))
                if len(score) >= 5: return score
        
        # Only reaches here if the community cards input are invalid
        return [(0,0)]
        
    
    def print_matrix(self, mat):
        for i in range(len(mat)):
            print(mat[i])


class Card():
    
    suits = [ '♠', '♣', '♡', '♢' ]
    values = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    def __init__(self, suit, value):
        self.suit = suit
        self.value= value

    def value_to_str(value):
        if value == 13 or value == 0: return 'Ace'
        if value == 12: return 'King'
        if value == 11: return 'Queen'
        if value == 10: return 'Jack'
        if value == 9: return '10'
        
        return Card.values[value]
    
    def suit_to_str(self, suit):
        return Card.suits[suit]

    def __str__(self):
        return Card.suits[self.suit] + Card.values[self.value]
    
    def __lt__(self, other):
         return self.value < other.value
