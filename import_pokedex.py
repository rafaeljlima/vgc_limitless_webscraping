#Importando bibliotecas para realizar requisições HTTP
import requests
import time

#Importando conexão com banco de dados
from database import Database

#URL base da PokeAPI para buscar dados de Pokémon
BASE_URL = "https://pokeapi.co/api/v2/pokemon"

#Headers para simular navegador e evitar bloqueios simples da API
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#Função que busca lista completa de Pokémon (nome + URL)
def get_all_pokemon():

    response = requests.get(
        f"{BASE_URL}?limit=100000",
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    #Retorna só a lista de resultados da API
    return response.json()["results"]

#Função que busca dados completos de um Pokémon específico
def get_pokemon_data(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        #Se der erro na requisição, propaga o erro pra ser tratado no loop principal
        raise e

#Função que busca dados completos de um move específico
def get_move_data(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        #Se der erro na requisição, propaga o erro pra ser tratado no loop principal
        raise e

#Função principal que importa Pokédex inteira pro banco
def import_pokedex():

    #Conexão com banco de dados
    db = Database()

    #Lista de todos os Pokémon disponíveis na API
    pokemon_list = get_all_pokemon()

    print(f"{len(pokemon_list)} Pokémon encontrados.")

    #Cache pra evitar repetir requests de moves iguais
    move_cache = {}

    #Contadores de progresso
    pokemon_counter = 0
    move_counter = 0

    #Controle de erro geral do processo
    error_occurred = False

    #Lista de Pokémon que falharam na requisição
    failed_pokemons = []

    #Abre conexão com o banco
    with db.connect() as cursor:

        #Loop principal de todos os Pokémon
        for pokemon in pokemon_list:

            try:

                #Busca dados completos do Pokémon na API
                data = get_pokemon_data(pokemon["url"])

                #Nome do Pokémon
                name = data["name"]

                #Extrai tipos (type1 e type2)
                types = [t["type"]["name"] for t in data["types"]]
                type1 = types[0]
                type2 = types[1] if len(types) > 1 else None

                #Organiza stats em um dicionário
                stats = {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in data["stats"]
                }

                #Insere dados do Pokémon no banco
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

                #Print de progresso a cada 100 Pokémon
                if pokemon_counter % 100 == 0:
                    print(f"{pokemon_counter} Pokémon processados...")

                #Loop dos moves que o Pokémon pode aprender
                for move in data["moves"]:

                    move_name = move["move"]["name"]
                    move_url = move["move"]["url"]

                    #Só processa move se ainda não estiver no cache
                    if move_name not in move_cache:

                        #Busca dados completos do move na API
                        move_data = get_move_data(move_url)

                        #Extrai informações do move
                        damage_class = move_data["damage_class"]["name"]
                        move_type = move_data["type"]["name"]
                        accuracy = move_data["accuracy"]
                        power = move_data["power"]

                        #Insere move no banco
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

                        #Marca move como já processado no cache
                        move_cache[move_name] = True

                        move_counter += 1

                        #Print de progresso a cada 100 moves novos
                        if move_counter % 100 == 0:
                            print(f"{move_counter} moves únicos registrados...")

            except Exception as e:

                #Marca erro geral
                error_occurred = True

                #Guarda nome do Pokémon que falhou
                failed_pokemons.append(pokemon["name"])

                print(f"Erro em {pokemon['name']}: {e}")

    #Resumo final do processo
    print("\n=== PROCESSO FINALIZADO ===")

    print(f"Total de Pokémon processados: {pokemon_counter}")
    print(f"Total de movimentos únicos registrados: {move_counter}")
    print(f"Moves armazenados no cache: {len(move_cache)}")

    print(f"\nPokémon que falharam ({len(failed_pokemons)}):")
    print(failed_pokemons)

    if error_occurred:
        print("\nFinalizado com erros.")
    else:
        print("\nFinalizado sem erros.")


if __name__ == "__main__":
    import_pokedex()
    
"""
PRINTS DA ÚLTIMA EXECUÇÃO

Erro em raging-bolt: 502 Server Error: Bad Gateway for url: https://pokeapi.co/api/v2/pokemon/1021/
1100 Pokémon processados...
800 moves únicos registrados...
Erro em pikachu-original-cap: 502 Server Error: Bad Gateway for url: https://pokeapi.co/api/v2/pokemon/10094/
1200 Pokémon processados...
Erro em charizard-gmax: 502 Server Error: Bad Gateway for url: https://pokeapi.co/api/v2/pokemon/10196/
1300 Pokémon processados...
Erro em meowstic-female-mega: list index out of range ( "abilities":[] )

=== PROCESSO FINALIZADO ===
Total de Pokémon processados: 1347
Total de movimentos únicos registrados: 832
Moves armazenados no cache: 832

Pokémon que falharam (4):
['raging-bolt', 'pikachu-original-cap', 'charizard-gmax', 'meowstic-female-mega']

Finalizado com erros.
"""