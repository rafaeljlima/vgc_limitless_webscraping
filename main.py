from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from database import Database
from db_functions import *

def scrape_all_tournaments():
    url = "https://play.limitlesstcg.com/tournaments/completed?game=VGC&format=M-A&platform=all&type=online&time=4weeks"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    db = Database()

    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))

        with db.connect() as cursor:

            table = driver.find_element(By.CLASS_NAME, "completed-tournaments")
            rows = table.find_elements(By.TAG_NAME, "tr")[1:]

            for t in range(len(rows)):

                table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))
                rows = table.find_elements(By.TAG_NAME, "tr")[1:]
                row = rows[t]

                cols = row.find_elements(By.TAG_NAME, "td")

                date = cols[1].text
                name = cols[2].text
                players = cols[5].text

                date_mysql = "2026-04-20"

                cols[2].find_element(By.TAG_NAME, "a").click()

                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))

                tournament_id = insert_tournament(cursor, name, date_mysql, players)

                players_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))
                player_rows = players_table.find_elements(By.TAG_NAME, "tr")[1:]

                for i in range(len(player_rows)):

                    players_table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))
                    player_rows = players_table.find_elements(By.TAG_NAME, "tr")[1:]
                    prow = player_rows[i]

                    cols = prow.find_elements(By.TAG_NAME, "td")

                    player_name = cols[1].text

                    record_text = cols[4].text
                    wins, losses, draws = [x.strip() for x in record_text.split("-")]

                    player_id = insert_player(cursor, player_name)

                    team_id = insert_team(cursor, tournament_id, player_id, wins, losses, draws)

                    cols[-1].find_element(By.TAG_NAME, "a").click()

                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "teamlist-pokemon")))

                    team_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "teamlist-pokemon")))
                    pokemons = team_div.find_elements(By.CLASS_NAME, "pkmn")

                    for p in pokemons:
                        pokemon_name = p.find_element(By.CSS_SELECTOR, ".name span").text
                        item = p.find_element(By.CLASS_NAME, "item").text
                        ability = p.find_element(By.CLASS_NAME, "ability").text

                        moves_elements = p.find_elements(By.CSS_SELECTOR, ".attacks li")
                        moves = [m.text for m in moves_elements]

                        pt_id = insert_pokemon_team(cursor, team_id, pokemon_name, item, ability)
                        insert_moves(cursor, pt_id, moves)

                    driver.back()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "striped")))

                driver.back()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "completed-tournaments")))
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_all_tournaments()