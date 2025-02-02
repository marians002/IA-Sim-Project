import random
from simulator.game_simulator import GameSimulator
from data_loader import data_loader as dl
from data_loader.team import Team
from manager.baseball_manager import BaseballManager
from genetica.mlbeticA import get_lineup
from manager.pitcher_selection import *


def simulate_series(team1: Team, team2: Team, games):
    """
    Simulate a series of games between two teams.

    Parameters:
    -----------
    team1 : Team
        The first team participating in the series.
    team2 : Team
        The second team participating in the series.
    games : int
        The total number of games in the series.

    Returns:
    --------
    tuple
        A tuple containing the winning team and a list of statistics for all games in the series.
    """
    team1_wins = 0
    team2_wins = 0
    rot_t1 = 0
    rot_t2 = 0
    required_wins = (games // 2) + 1
    all_games_stats = []

    for _ in range(games):
        game_simulator = simulate_game(team1, team2, rot_t1, rot_t2)
        rot_t1 += 1
        rot_t2 += 1

        # Collect final statistics
        game_stats = game_simulator.get_final_statistics()
        all_games_stats.append(game_stats)

        # Determine the winner of the game
        if game_simulator.get_winner() == team1.team_name:
            team1_wins += 1
        else:
            team2_wins += 1

        # Check if any team has won the required number of games
        if team1_wins == required_wins:
            return team1, all_games_stats
        elif team2_wins == required_wins:
            return team2, all_games_stats
    return random.choice([team1, team2]), all_games_stats


def simulate_game(team1, team2, rot_t1=0, rot_t2=0):
    """
    Simulate a single game between two teams.

    Parameters:
    -----------
    team1 : Team
        The first team participating in the game.
    team2 : Team
        The second team participating in the game.
    rot_t1 : int, optional
        The current rotation index for team 1. Defaults to 0.
    rot_t2 : int, optional
        The current rotation index for team 2. Defaults to

    Returns:
    --------
    GameSimulator
        An instance of GameSimulator with the simulated game results.
    """
    t1_pitchers, t1_batters = dl.separate_pitchers_batters(team1)
    t2_pitchers, t2_batters = dl.separate_pitchers_batters(team2)

    # Get pitchers
    rotation_t1, bullpen_t1, rotation_t2, bullpen_t2, starter_t1, starter_t2 = get_rotations_bullpens(t1_pitchers, t2_pitchers, rot_t1, rot_t2)

    # Get lineups
    h_lineup = get_lineup(team1)
    a_lineup = get_lineup(team2)

    # Set pitcher according to rotation:
    h_lineup[0] = starter_t1
    a_lineup[0] = starter_t2

    game_simulator = GameSimulator(BaseballManager(), team1, team2, t1_batters, t2_batters,
                                   h_lineup, a_lineup, bullpen_t1, bullpen_t2)
    game_simulator.simulate_game()
    game_simulator.save_log()
    return game_simulator
