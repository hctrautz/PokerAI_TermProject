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
        self.n_simulations = 1000

    # valid_actions[0] = fold, valid_actions[1] = call, and valid_actions[2] = raise
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        #determines the current rounde state so that we may better our AI's action accordingly
        try:
            opponent_action_dict = round_state['action_histories'][round_state['street']][-1]
        except:
            if round_state['street'] == 'turn':
                opponent_action_dict = round_state['action_histories']['flop'][-1]
            else:
                opponent_action_dict = round_state['action_histories']['preflop'][-1]

        community_card = round_state['community_card']
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=NB_SIMULATION,
            nb_player=self.nb_player,
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(community_card)
        )

        pot_amount = round_state['pot']['main']['amount']
        ai_stack = [player['stack'] for player in round_state['seats'] if player['uuid'] == self.uuid][0]
        raise_amount_options = [item for item in valid_actions if item['action'] == 'raise'][0]['amount']
        opponent_action = opponent_action_dict['action']

        can_call = len([item for item in valid_actions if item['action'] == 'call']) > 0

        if win_rate >= 1.0 / self.nb_player:
            action = valid_actions[1]  # fetch CALL action info
        else:
            action = valid_actions[0]  # fetch FOLD action info


        return action['action'], action['amount']

    def receive_game_start_message(self, game_info):
        self.nb_player = game_info['player_num']

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return MonteCarloPlayer()
