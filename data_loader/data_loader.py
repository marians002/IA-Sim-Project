import os
import statsapi
import jsonpickle
import pandas as pd
from data_loader.player import *
from data_loader.team import Team


def print_players(team):
    """
    Print the players of a given team.

    Args:
    team (Team): The team whose players are to be printed.
    """
    for player in team.players:
        print(f" \033[91m Player:\033[0m {player.first_name + ' ' + player.last_name}, Position: {player.pos}")


def print_team_rosters(team_rosters):
    """
    Print the rosters of all teams.

    Args:
    team_rosters (list): A list of Team objects.
    """
    for team in team_rosters:
        print("\033[96mTeam: \033[0m" + team.team_name)
        print_players(team)
        print()


def load_csv():
    """
    Load pitcher and batter data from CSV files.

    Returns:
    tuple: A tuple containing two pandas DataFrames, one for pitchers and one for batters.
    """
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, '../stats csv', 'pitchers 2022 PA50.csv')
    pitchers = pd.read_csv(csv_path).drop('year', axis=1)
    csv_path = os.path.join(current_dir, '../stats csv', 'batters 2022 PA50.csv')
    batters = pd.read_csv(csv_path).drop(['year', 'player_age'], axis=1)
    return pitchers, batters


def get_players(data, players, type_batter):
    """
    Populate the players list with Batter or Pitcher objects.

    Args:
    data (pd.DataFrame): DataFrame containing player data.
    players (list): List to be populated with player objects.
    type_batter (bool): If True, create Batter objects; otherwise, create Pitcher objects.
    """
    for _, row in data.iterrows():
        first_name, last_name = name_formatter(row['last_name, first_name'])
        player_data = [first_name, last_name] + list(row)[1:]
        if type_batter:
            players.append(Batter(player_data))
        else:
            players.append(Pitcher(player_data))


def name_formatter(last_name_first_name):
    """
    Split the full name into first and last names.

    Args:
    last_name_first_name (str): Full name in the format 'last_name, first_name'.

    Returns:
    tuple: A tuple containing the first name and last name.
    """
    comma_index = last_name_first_name.index(',')
    first_name = last_name_first_name[comma_index + 2:]
    last_name = last_name_first_name[:comma_index]
    return first_name, last_name


def get_team_rosters(year=2022):
    """
    Retrieve team rosters from statsapi.

    Args:
    year (int): The year for which to retrieve the rosters. Default is 2022.

    Returns:
    dict: A dictionary with team names as keys and lists of player tuples as values.
    """
    teams_data = statsapi.get('teams', {'sportId': 1})
    team_ids_names = [(team['id'], team['name']) for team in teams_data['teams']]

    team_rosters = {}
    for team_id, team_name in team_ids_names:
        roster = statsapi.get('team_roster', {'teamId': team_id, 'season': year})
        team_players = []
        for player in roster['roster']:
            player_name = player['person']['fullName']
            player_position = player['position']['abbreviation']
            team_players.append((player_name, player_position))
        team_rosters[team_name] = team_players

    return team_rosters


def add_players_to_teams(team_rosters, players):
    """
    Add players to their respective teams.

    Args:
    team_rosters (dict): Dictionary with team names as keys and lists of player tuples as values.
    players (list): List of player objects.

    Returns:
    list: A list of Team objects with players added.
    """
    teams = []
    i = 1
    for team_name, team_players in team_rosters.items():
        new_team = Team(team_name, id=i)
        i += 1
        for player_name, player_position in team_players:
            for player in players:
                if player.first_name + ' ' + player.last_name == player_name:
                    player.pos = [player_position]
                    new_team.add_player(player)
                    break
        teams.append(new_team)
    return teams


def get_teams():
    """
    Load teams and players from CSV files and statsapi.

    Returns:
    tuple: A tuple containing a list of Team objects and a list of player objects.
    """
    pitchers, batters = load_csv()
    players = []
    get_players(pitchers, players, False)
    get_players(batters, players, True)
    team_rosters = get_team_rosters(year=2022)
    teams = add_players_to_teams(team_rosters, players)
    return teams, players


def save_to_json(data, file_path):
    """
    Save data to a JSON file.

    Args:
    data (object): The data to be saved.
    file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as file:
        json_data = jsonpickle.encode(data)
        file.write(json_data)


def load_from_json(file_path):
    """
    Load data from a JSON file.

    Args:
    file_path (str): The path to the JSON file.

    Returns:
    object: The data loaded from the JSON file.
    """
    with open(file_path, 'r') as file:
        json_data = file.read()
        return jsonpickle.decode(json_data)


def separate_pitchers_batters(team):
    """
    Separate pitchers and batters from a team.

    Args:
    team (Team): The team whose players are to be separated.

    Returns:
    tuple: A tuple containing a list of pitchers and a list of batters.
    """
    pitchers = [player for player in team.players if isinstance(player, Pitcher) and not isinstance(player, Batter)]
    batters = [player for player in team.players if isinstance(player, Batter) and not isinstance(player, Pitcher)]
    batters = [player for player in batters if player.first_name != "Shohei"]
    return pitchers, batters


def load_data(verbose=False):
    """
    Load teams and players data, either from JSON files or by fetching and processing the data.

    Args:
    verbose (bool): If True, print the team rosters. Default is False.

    Returns:
    list: A list of Team objects.
    """
    teams_file = 'teams.json'
    players_file = 'players.json'

    if os.path.exists(teams_file) and os.path.exists(players_file):
        teams = load_from_json(teams_file)
        players = load_from_json(players_file)
    else:
        teams, players = get_teams()
        save_to_json(teams, teams_file)
        save_to_json(players, players_file)

    if verbose:
        print()
        print_team_rosters(teams)

    print("\033[92mTeams and players data loaded successfully.\033[0m")
    print()
    return teams
