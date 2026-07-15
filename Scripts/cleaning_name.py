import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

import re
from imports.database import Database 

def sanitizar_nome(nome):
    if not nome:
        return ""
    
    nome_limpo = nome.lower()
    nome_limpo = nome_limpo.replace("♀", " female")
    nome_limpo = nome_limpo.replace("♂", " male")
    nome_limpo = re.sub(r'[-_\.]', ' ', nome_limpo)
    nome_limpo = " ".join(nome_limpo.split())
    
    return nome_limpo

def fetch_pokemons_to_sanitize(cursor):
    query = "SELECT id, name FROM Pokemons WHERE name_clean IS NULL"
    cursor.execute(query)
    return cursor.fetchall()

def update_pokemon_clean_name(cursor, pokemon_id, name_clean):
    query = "UPDATE Pokemons SET name_clean = %s WHERE id = %s"
    cursor.execute(query, (name_clean, pokemon_id))

def fetch_pokemon_data_to_sanitize(cursor):
    query = "SELECT id, name FROM Pokemon_data WHERE name_clean IS NULL"
    cursor.execute(query)
    return cursor.fetchall()

def update_pokemon_data_clean_name(cursor, pokemon_id, name_clean):
    query = "UPDATE Pokemon_data SET name_clean = %s WHERE id = %s"
    cursor.execute(query, (name_clean, pokemon_id))

def executar_limpeza_geral():
    db = Database()

    with db.connect() as cursor:
        if cursor is None:
            print("Erro: Não foi possível conectar ao banco de dados.")
            return

        print("=== Iniciando Sanitização da Tabela Pokemons (Scraper) ===")
        pokemons_scraper = fetch_pokemons_to_sanitize(cursor)
        
        for p_id, original_name in pokemons_scraper:
            nome_tratado = sanitizar_nome(original_name)
            update_pokemon_clean_name(cursor, p_id, nome_tratado)
            
        print(f"Sucesso: {len(pokemons_scraper)} registros atualizados na tabela Pokemons.")

        print("\n=== Iniciando Sanitização da Tabela Pokemon_data (API) ===")
        pokemons_api = fetch_pokemon_data_to_sanitize(cursor)
        
        for p_id, original_name in pokemons_api:
            nome_tratado = sanitizar_nome(original_name)
            update_pokemon_data_clean_name(cursor, p_id, nome_tratado)
            
        print(f"Sucesso: {len(pokemons_api)} registros atualizados na tabela Pokemon_data.")

if __name__ == "__main__":
    executar_limpeza_geral()