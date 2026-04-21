def insert_tournament(cursor, name, date, players):
    query = """
    INSERT INTO Tournaments (name, date, qtplayers)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (name, date, players))
    return cursor.lastrowid


def insert_player(cursor, name):
    query = "INSERT INTO Players (name) VALUES (%s)"
    cursor.execute(query, (name,))
    return cursor.lastrowid


def insert_team(cursor, tournament_id, player_id, wins, losses, draws):
    query = """
    INSERT INTO Teams (tournament_id, player_id, wins, losses, draws)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (tournament_id, player_id, wins, losses, draws))
    return cursor.lastrowid


def get_or_create(cursor, table, name):
    query = f"SELECT id FROM {table} WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()

    if result:
        return result[0]

    query = f"INSERT INTO {table} (name) VALUES (%s)"
    cursor.execute(query, (name,))
    return cursor.lastrowid


def insert_pokemon_team(cursor, team_id, pokemon, item, ability):
    pokemon_id = get_or_create(cursor, "Pokemons", pokemon)
    item_id = get_or_create(cursor, "Items", item)

    ability = ability.replace("Ability: ", "")
    ability_id = get_or_create(cursor, "Abilities", ability)

    query = """
    INSERT INTO Pokemon_teams (team_id, pokemon_id, item_id, ability_id)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (team_id, pokemon_id, item_id, ability_id))

    return cursor.lastrowid


def insert_moves(cursor, pokemon_team_id, moves):
    for move in moves:
        move_id = get_or_create(cursor, "Moves", move)

        query = """
        INSERT INTO Pokemon_moves (idpokemon_team, idmove)
        VALUES (%s, %s)
        """
        cursor.execute(query, (pokemon_team_id, move_id))