#Importando bibliotecas para realizar requisições HTTP
import requests
from bs4 import BeautifulSoup

#Importando funções de outros arquivos
from database import Database
from db_functions import *

#URL base utilizada para montar links completos durante a navegação
BASE_URL = "https://play.limitlesstcg.com"

#Definindo cabeçalhos para simular um navegador comum
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

#Função auxiliar para realizar uma requisição e retornar o HTML tratado pelo BeautifulSoup
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

        page = 1
        max_page = None

        while True:

            paginated_url = url + f"&pg={page}"

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

            for row in tournament_rows:

                cols = row.find_all("td")

                if len(cols) < 6:
                    continue

                #Pegando cada elemento do torneio
                date = cols[1].get_text(strip=True)
                name = cols[2].get_text(strip=True)
                players = cols[5].get_text(strip=True)

                #Convertendo a data para formato sql
                date_mysql = convert_date_to_mysql(date)

                #Atualmente o limitless nao discerne M-B de M-A, então estou colocando um limite temporário na data até que isso seja tirado.
                MAX_DATE = "2026-06-16"

                if date_mysql > MAX_DATE:
                    continue

                #Verificando se o torneio já existe no banco
                existing_id = tournament_exists(
                    cursor,
                    name,
                    date_mysql,
                    players
                )

                if existing_id:
                    continue

                #Inserindo os dados extraídos do torneio no banco
                tournament_id = insert_tournament(
                    cursor,
                    name,
                    date_mysql,
                    players
                )

                #Obtendo o link da página do torneio
                tournament_link = cols[2].find("a")

                if not tournament_link:
                    continue

                tournament_url = (
                    BASE_URL +
                    tournament_link["href"]
                )

                #Carregando a página do torneio através de uma nova requisição GET
                try:
                    tournament_soup = get_soup(
                        tournament_url
                    )
                except Exception:
                    continue

                #Carregamos a tabela dos jogadores do torneio
                players_table = tournament_soup.find(
                    "table",
                    class_="striped"
                )

                if not players_table:
                    continue

                player_rows = players_table.find_all("tr")[1:]

                for prow in player_rows:

                    cols = prow.find_all("td")

                    if len(cols) < 5:
                        continue

                    #Extraimos e inserimos as informações do jogador e resultados do time
                    player_name = cols[1].get_text(
                        strip=True
                    )

                    record_text = cols[4].get_text(
                        strip=True
                    )

                    #Validar se o jogador tem recorde guardado no site
                    parts = record_text.split("-")

                    if len(parts) != 3:
                        continue

                    wins, losses, draws = [
                        x.strip()
                        for x in parts
                    ]

                    player_id = insert_player(
                        cursor,
                        player_name
                    )

                    team_id = insert_team(
                        cursor,
                        tournament_id,
                        player_id,
                        wins,
                        losses,
                        draws
                    )

                    #Obtendo o link do time do jogador, desconsiderando jogadores sem time publicado
                    team_anchor = cols[-1].find("a")

                    if not team_anchor:
                        continue

                    team_url = (
                        BASE_URL +
                        team_anchor["href"]
                    )

                    #Carregando a página do time através de uma nova requisição GET
                    try:
                        team_soup = get_soup(
                            team_url
                        )
                    except Exception:
                        continue

                    team_div = team_soup.find(
                        "div",
                        class_="teamlist-pokemon"
                    )

                    if not team_div:
                        continue

                    pokemons = team_div.find_all(
                        "div",
                        class_="pkmn"
                    )

                    #Pegando os detalhes de cada pokémon do time
                    for p in pokemons:

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
                            continue

                        pokemon_name = pokemon_name_element.get_text(strip=True)
                        item = item_element.get_text(strip=True)
                        ability = ability_element.get_text(strip=True)

                        moves = [
                            move.get_text(strip=True)
                            for move in p.select(".attacks li")
                        ]

                        pt_id = insert_pokemon_team(
                            cursor,
                            team_id,
                            pokemon_name,
                            item,
                            ability
                        )

                        insert_moves(cursor, pt_id, moves)

            if max_page and page >= max_page:
                break

            page += 1


#Evitando execução adicional
if __name__ == "__main__":
    scrape_all_tournaments()