from pypokerengine.api.game import setup_config, start_poker
from examples.players import fish_player
import MonteCarlo_player_setup

config = setup_config(max_round=10, initial_stack=100, small_blind_amount=5)
config.register_player(name="p1", algorithm= MonteCarlo_player_setup.MonteCarloPlayer())
config.register_player(name="p2",algorithm= MonteCarlo_player_setup.MonteCarloPlayer())
game_result = start_poker(config, verbose=1)
print(game_result)