import random
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate, _fill_community_card, \
    _pick_unused_card

NB_SIMULATION = 1000
def _montecarlo_simulation(nb_player, hole_card, community_card):
    community_card = _fill_community_card(community_card, used_card=hole_card+community_card)
    unused_cards = _pick_unused_card((nb_player-1)*2, hole_card + community_card)
    opponents_hole = [unused_cards[2*i:2*i+2] for i in range(nb_player-1)]
    opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
    my_score = HandEvaluator.eval_hand(hole_card, community_card)
    return 1 if my_score >= max(opponents_score) else 0

def estimate_hole_card_win_rate(nb_simulation, nb_player, hole_card, community_card=None):
    if not community_card: community_card = []
    win_count = sum([_montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
    return 1.0 * win_count / nb_simulation

class MonteCarloPlayer(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.wins = 0
        self.losses = 0
        self.bluffing = True
        self.turnCount = 0
        self.prevRound = 0

    # valid_actions[0] = fold, valid_actions[1] = call, and valid_actions[2] = raise
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        #determines the current round state so that we may better our AI's action accordingly
        try:
            opponent_action_dict = round_state['action_histories'][round_state['street']][-1]
        except:
            if round_state['street'] == 'turn':
                opponent_action_dict = round_state['action_histories']['flop'][-1]
            else:
                opponent_action_dict = round_state['action_histories']['preflop'][-1]

        #Need to take into account the community cards when calculating our winrate
        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        #Reset our initial variables before the start of each round
        if 'round_count' not in round_state.keys() and self.turn == 0:
            self.bluffing = False

        if 'round_count' in round_state.keys():
            if round_state['round_count'] != self.prevRound:
                self.prevRound = round_state['round_count']
                self.bluffing = False
                self.turnCount = 0

        pot_amount = round_state['pot']['main']['amount']
        stack = [player['stack'] for player in round_state['seats'] if player['uuid'] == self.uuid][0]
        raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
        opponent_action = opponent_action_dict['action']
        max = raise_amount_options['max']
        min = max = raise_amount_options['min']

        #Determine whether or not calling is a valid action during the current round state
        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0
        if can_call:
            # If so, compute the amount that needs to be called
            call_amount = [item for item in valid_actions if item['action'] == 'call'][0]['amount']
        else:
            call_amount = 0

        amount = None

        if opponent_action == "raise":
            if win_rate > .85:
                action = 'raise'
                amount = max
            elif win_rate > .75:
                action = 'raise'
                amount = int(((200-stack)/200)*(max-min)+min)
            elif win_rate > .55:
                action = 'call'
            else:
                if self.bluffing:
                    action = 'call'
                else:
                    num = random.uniform(0, 1)
                    if num > win_rate / 2:
                        action = 'fold'
                    elif can_call:
                        action = 'call'
        else:
            # raise less if opponent calls
            if win_rate > .85:
                action = 'raise'
                amount = int(((200-stack)/200)*(max-min)+min)
            elif win_rate > .75:
                action = 'raise'
                amount = int((.85((200-stack)/200))*(max-min)+min)
            elif win_rate > .45:
                action = 'call'
            else:
                num = random.uniform(0, 1)
                if self.bluffing:
                    if num > .5:
                        action = 'raise'
                        amount = int((stack / 100)/8*(max-min))
                        amount += min
                    else:
                        action = "call"
                else:
                    if num > win_rate:
                        action = 'fold'
                    elif num > win_rate / 2 and can_call:
                        action = 'call'
                    else:
                        action = 'raise'
                        # small bluff
                        amount = int((stack/100)/8*(max-min))
                        amount += min
                        self.bluffing = True

        if amount is None:
            items = [item for item in valid_actions if item['action'] == action]
            amount = items[0]['amount']

        if amount < 0 or self.turnCount == 0:
            action = 'call'
            items = [item for item in valid_actions if item['action'] == action]
            amount = items[0]['amount']

            if win_rate < .25:
                action = 'fold'

            if opponent_action == 'raise' and win_rate < .4:
                action = 'fold'

        if action == "raise" and amount > max:
            amount = max
        if action == "raise" and amount < min:
            amount = min

        self.turnCount += 1
        return action, amount

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        result = self.uuid in [item['uuid'] for item in winners]
        self.wins += int(result)
        self.losses += int(not result)
        pass

def setup_ai():
    return MonteCarloPlayer()
