import requests
from database import Database

BASE_URL = "https://pokeapi.co/api/v2/pokemon"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_all_pokemon():
    response = requests.get(
        f"{BASE_URL}?limit=100000",
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.json()["results"]


def get_pokemon_data(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def get_move_data(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.json()


def import_pokedex():

    db = Database()
    pokemon_list = get_all_pokemon()

    print(f"{len(pokemon_list)} Pokémon encontrados.")

    move_cache = {}

    pokemon_counter = 0
    move_counter = 0
    error_occurred = False

    with db.connect() as cursor:

        for pokemon in pokemon_list:

            try:
                data = get_pokemon_data(pokemon["url"])

                name = data["name"]

                types = [t["type"]["name"] for t in data["types"]]
                type1 = types[0]
                type2 = types[1] if len(types) > 1 else None

                stats = {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in data["stats"]
                }

                cursor.execute(
                    """
                    INSERT IGNORE INTO Pokemon_data (
                        name,
                        type1,
                        type2,
                        hp,
                        attack,
                        defense,
                        special_attack,
                        special_defense,
                        speed
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        name,
                        type1,
                        type2,
                        stats["hp"],
                        stats["attack"],
                        stats["defense"],
                        stats["special-attack"],
                        stats["special-defense"],
                        stats["speed"]
                    )
                )

                pokemon_counter += 1

                if pokemon_counter % 150 == 0:
                    print(f"{pokemon_counter} Pokémon processados...")

                for move in data["moves"]:

                    move_name = move["move"]["name"]
                    move_url = move["move"]["url"]

                    if move_name not in move_cache:

                        move_data = get_move_data(move_url)

                        damage_class = move_data["damage_class"]["name"]
                        move_type = move_data["type"]["name"]
                        accuracy = move_data["accuracy"]
                        power = move_data["power"]

                        cursor.execute(
                            """
                            INSERT IGNORE INTO Moves_data (
                                name,
                                damage_class,
                                type,
                                accuracy,
                                power
                            )
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (
                                move_name,
                                damage_class,
                                move_type,
                                accuracy,
                                power
                            )
                        )

                        move_counter += 1

                        if move_counter % 500 == 0:
                            print(f"{move_counter} moves registrados...")

            except Exception as e:
                error_occurred = True
                print(f"Erro em {pokemon['name']}: {e}")

    print("\n=== PROCESSO FINALIZADO ===")
    print(f"Total de moves registrados: {move_counter}")

    if error_occurred:
        print("Finalizado com erros.")
    else:
        print("Finalizado sem erros.")


if __name__ == "__main__":
    import_pokedex()