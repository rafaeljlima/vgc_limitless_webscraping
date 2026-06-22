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


def import_pokedex():

    db = Database()

    pokemon_list = get_all_pokemon()

    print(f"{len(pokemon_list)} Pokémon encontrados.")

    with db.connect() as cursor:

        for pokemon in pokemon_list:

            try:
                data = get_pokemon_data(
                    pokemon["url"]
                )

                name = data["name"]

                types = [
                    t["type"]["name"]
                    for t in data["types"]
                ]

                type1 = types[0]
                type2 = types[1] if len(types) > 1 else None

                stats = {}

                for stat in data["stats"]:
                    stats[
                        stat["stat"]["name"]
                    ] = stat["base_stat"]

                cursor.execute(
                    """
                    INSERT IGNORE INTO Pokemon_Data (
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
                    VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
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

                print(
                    f"Importado: {name}"
                )

            except Exception as e:
                print(
                    f"Erro em {pokemon['name']}: {e}"
                )


if __name__ == "__main__":
    import_pokedex()