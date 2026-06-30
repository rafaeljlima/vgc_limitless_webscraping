#Importando bibliotecas para realizar requisições HTTP
import requests
from bs4 import BeautifulSoup

#Importando funções de outros arquivos
from Imports.database import Database
from Imports.db_functions import *

#URL base utilizada para montar links completos durante a navegação
BASE_URL = "https://play.limitlesstcg.com"

#Definindo cabeçalhos para simular um navegador comum
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#Função GET de requisição para retornar o HTML tratado pelo BeautifulSoup
def get_soup(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return BeautifulSoup(response.text, "html.parser")

#Função de scraping
def scrape_all_tournaments():

    #Carregando a url desejada
    url = (
        "https://play.limitlesstcg.com/tournaments/completed"
        "?game=VGC"
        "&format=M-A"
        "&platform=all"
        "&type=online"
        "&time=all"
    )

    #Inicializando conexão com banco
    db = Database()

    #Utilizando a conexão do banco
    with db.connect() as cursor:

        #Definindo páginação inicial e limite
        page = 1
        max_page = None

        while True:

            #incluindo paginação atual na url da página
            paginated_url = url + f"&page={page}"

            #Carregando a página principal de torneios através de uma requisição GET
            tournaments_soup = get_soup(paginated_url)

            #Definindo tabela e linhas de acordo com o HTML da página
            tournaments_table = tournaments_soup.find(
                "table",
                class_="completed-tournaments"
            )

            if not tournaments_table:
                break

            tournament_rows = tournaments_table.find_all("tr")[1:]

            if page == 1:
                pagination = tournaments_soup.select_one(".pagination")
                if pagination:
                    max_page = int(pagination["data-max"])

            #Prints opcionais de retorno para acompanhar progresso do scraping em cada página
            print(f"\n{'='*80}")
            print(f"PROCESSANDO PÁGINA {page}")
            print(f"{'='*80}")

            for row in tournament_rows:

                cols = row.find_all("td")

                if len(cols) < 6:
                    continue

                #Resgatando o retorno html de data do torneio na váriavel
                date_iso = row.get("data-date")

                if not date_iso:
                    continue

                #Ignorando horas e pegando somente os caracteres de data
                date_mysql = date_iso[:10]

                #Resgatando as outras váriaveis
                name = cols[2].get_text(strip=True)
                players = cols[5].get_text(strip=True)

                #Prints opcionais de retorno para acompanhar progresso do scraping em cada torneio
                print("\n" + "-"*80)
                print(f"TORNEIO: {name}")
                print(f"DATA: {date_mysql}")
                print(f"PLAYERS SITE: {players}")

                #Definindo data máxima de torneio para essa pesquisa em específico, data máxima da regulação M-A
                MAX_DATE = "2026-06-16"

                if date_mysql > MAX_DATE:
                    print("IGNORADO POR DATA")
                    continue

                #Apartir daqui, resgatando cada valor um a um, sempre tratando erros caso haja ausência de algum valor considerado crucial ...
                #  e resgatando valores para prints de acompanhamento ao longo dos loops
                existing_id = tournament_exists(
                    cursor,
                    name,
                    date_mysql,
                    players
                )

                if existing_id:
                    print("TORNEIO JÁ EXISTE")
                    continue

                tournament_id = insert_tournament(
                    cursor,
                    name,
                    date_mysql,
                    players
                )

                print(f"TORNEIO INSERIDO -> ID {tournament_id}")

                tournament_link = cols[2].find("a")

                if not tournament_link:
                    print("SEM LINK DE TORNEIO")
                    continue

                tournament_url = (
                    BASE_URL +
                    tournament_link["href"]
                )

                print(f"URL TORNEIO: {tournament_url}")

                try:
                    tournament_soup = get_soup(
                        tournament_url
                    )
                except Exception as e:
                    print(f"ERRO AO ABRIR TORNEIO: {e}")
                    continue

                players_table = tournament_soup.find(
                    "table",
                    class_="striped"
                )

                if not players_table:
                    print("TABELA DE PLAYERS NÃO ENCONTRADA")
                    continue

                player_rows = players_table.find_all("tr")[1:]

                print(
                    f"JOGADORES ENCONTRADOS NA TABELA: {len(player_rows)}"
                )

                player_counter = 0
                team_counter = 0
                pokemon_counter = 0

                for prow in player_rows:

                    cols = prow.find_all("td")

                    if len(cols) < 5:
                        continue

                    player_name = cols[1].get_text(
                        strip=True
                    )

                    record_text = cols[4].get_text(
                        strip=True
                    )

                    parts = record_text.split("-")

                    if len(parts) != 3:
                        print(
                            f"PLAYER IGNORADO SEM RECORD: {player_name}"
                        )
                        continue

                    wins, losses, draws = [
                        x.strip()
                        for x in parts
                    ]

                    player_counter += 1

                    print()
                    print(f"PLAYER #{player_counter}")
                    print(f"NOME: {player_name}")
                    print(
                        f"RECORD: {wins}-{losses}-{draws}"
                    )

                    player_id = insert_player(
                        cursor,
                        player_name
                    )

                    print(f"PLAYER ID: {player_id}")

                    team_id = insert_team(
                        cursor,
                        tournament_id,
                        player_id,
                        wins,
                        losses,
                        draws
                    )

                    team_counter += 1

                    print(f"TEAM ID: {team_id}")

                    team_anchor = cols[-1].find("a")

                    if not team_anchor:
                        print("SEM TEAM PUBLICADO")
                        continue

                    team_url = (
                        BASE_URL +
                        team_anchor["href"]
                    )

                    print(f"TEAM URL: {team_url}")

                    try:
                        team_soup = get_soup(
                            team_url
                        )
                    except Exception as e:
                        print(
                            f"ERRO AO ABRIR TEAM: {e}"
                        )
                        continue

                    team_div = team_soup.find(
                        "div",
                        class_="teamlist-pokemon"
                    )

                    if not team_div:
                        print("TEAMLIST NÃO ENCONTRADA")
                        continue

                    pokemons = team_div.find_all(
                        "div",
                        class_="pkmn"
                    )

                    print(
                        f"POKÉMONS ENCONTRADOS NO TIME: {len(pokemons)}"
                    )

                    for index, p in enumerate(pokemons, start=1):

                        pokemon_name_element = p.select_one(
                            ".name span"
                        )

                        item_element = p.find(
                            "div",
                            class_="item"
                        )

                        ability_element = p.find(
                            "div",
                            class_="ability"
                        )

                        if (
                            not pokemon_name_element
                            or not item_element
                            or not ability_element
                        ):
                            print(
                                f"POKÉMON #{index} INVÁLIDO"
                            )
                            continue

                        pokemon_name = pokemon_name_element.get_text(
                            strip=True
                        )

                        item = item_element.get_text(
                            strip=True
                        )

                        ability = ability_element.get_text(
                            strip=True
                        )

                        moves = [
                            move.get_text(strip=True)
                            for move in p.select(".attacks li")
                        ]

                        print(
                            f"POKÉMON #{index}: {pokemon_name}"
                        )

                        print(
                            f"ITEM: {item}"
                        )

                        print(
                            f"ABILITY: {ability}"
                        )

                        print(
                            f"MOVES ({len(moves)}): {moves}"
                        )

                        pt_id = insert_pokemon_team(
                            cursor,
                            team_id,
                            pokemon_name,
                            item,
                            ability
                        )

                        print(
                            f"POKEMON_TEAM ID: {pt_id}"
                        )

                        insert_moves(
                            cursor,
                            pt_id,
                            moves
                        )

                        pokemon_counter += 1

                print("\nRESUMO DO TORNEIO")
                print(
                    f"PLAYERS PROCESSADOS: {player_counter}"
                )
                print(
                    f"TEAMS CRIADOS: {team_counter}"
                )
                print(
                    f"POKÉMONS INSERIDOS: {pokemon_counter}"
                )
                print("-"*80)

            if max_page and page >= max_page:
                break

            page += 1

#Evitando execução adicional
if __name__ == "__main__":
    scrape_all_tournaments()