#Importando bibliotecas e dependências do Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Importando funções de outros arquivos
from database import Database
from db_functions import *

#Função de scraping
def scrape_all_tournaments():
    #Carregando a url desejada
    url = "https://play.limitlesstcg.com/tournaments/completed?game=VGC&format=M-A&platform=all&type=online&time=4weeks"

    #Definindo opções acessadas para o navegador, nesse caso headless-new e com gpu desativada para evitar bugs e diminuir processamento
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    db = Database()

    try:
        driver.get(url)

        #Utilizando sempre wait until para cada pagina carregar antes de começar o scraping
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))

        #Utilizando a conexão do banco
        with db.connect() as cursor:

            #Definindo tabelas e linhas de acordo com o HTML da página
            table = driver.find_element(By.CLASS_NAME, "completed-tournaments")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]

            for t in range(len(rows)):

                table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))
                rows = table.find_elements(By.TAG_NAME, "tr")[1:]
                row = rows[t]

                cols = row.find_elements(By.TAG_NAME, "td")

                #Pegando cada elemento do torneio
                date = cols[1].text
                name = cols[2].text
                players = cols[5].text

                #Convertendo a data para formato sql
                date_mysql = convert_date_to_mysql(date)

                #Verificando se o torneio já existe no banco
                existing_id = tournament_exists(cursor, name, date_mysql, players)

                if existing_id:
                    continue

                #Inserindo os dados extraídos do torneio no banco
                tournament_id = insert_tournament(cursor, name, date_mysql, players)

                #Clicando no torneio
                cols[2].find_element(By.TAG_NAME, "a").click()

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))

                #Clicar em "Show all players" se existir
                try:
                    show_all = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "show-all")))
                    show_all.click()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))
                except:
                    pass

                #Carregamos a tabela dos jogadores do torneio
                players_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))
                player_rows = players_table.find_elements(By.TAG_NAME, "tr")[1:]

                for i in range(len(player_rows)):
                    
                    #Extraimos e inserimos as informações do jogador e resultados do time
                    players_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))
                    player_rows = players_table.find_elements(By.TAG_NAME, "tr")[1:]
                    prow = player_rows[i]

                    cols = prow.find_elements(By.TAG_NAME, "td")

                    player_name = cols[1].text

                    record_text = cols[4].text

                    # Validar se o jogador tem recorde guardado no site
                    parts = record_text.split("-")
                    if len(parts) != 3:
                        continue

                    wins, losses, draws = [x.strip() for x in parts]

                    player_id = insert_player(cursor, player_name)

                    team_id = insert_team(cursor, tournament_id, player_id, wins, losses, draws)

                    #Clicando para seguir com a extração do time, mas desconsiderando jogadores que não publicaram time
                    try:
                        cols[-1].find_element(By.TAG_NAME, "a").click()
                    except:
                        continue

                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "teamlist-pokemon")))

                    team_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "teamlist-pokemon")))
                    pokemons = team_div.find_elements(By.CLASS_NAME, "pkmn")

                    #Pegando os detalhes de cada pokémon do time
                    for p in pokemons:
                        pokemon_name = p.find_element(By.CSS_SELECTOR, ".name span").text
                        item = p.find_element(By.CLASS_NAME, "item").text
                        ability = p.find_element(By.CLASS_NAME, "ability").text

                        moves_elements = p.find_elements(By.CSS_SELECTOR, ".attacks li")
                        moves = [m.text for m in moves_elements]

                        pt_id = insert_pokemon_team(cursor, team_id, pokemon_name, item, ability)
                        insert_moves(cursor, pt_id, moves)

                    #Voltando para páginas anteriores, para reiniciar o processo e procurar por mais jogadores/times e depois por mais torneios
                    driver.back()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))

                driver.back()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))
    finally:
        driver.quit()

#Evitando execução adicional
if __name__ == "__main__":
    scrape_all_tournaments()