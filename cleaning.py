import re
from database import Database 

def sanitizar_nome(nome):
    if not nome:
        return ""
    
    # 1. Transforma em minúsculo
    nome_limpo = nome.lower()
    
    # 2. Substitui traços (-), sublinhados (_) e pontos por espaços simples
    nome_limpo = re.sub(r'[-_\.]', ' ', nome_limpo)
    
    # 3. Remove múltiplos espaços extras e espaços nas pontas
    nome_limpo = " ".join(nome_limpo.split())
    
    return nome_limpo

# --- FUNÇÕES PARA A TABELA POKEMONS (SCRAPER) ---

def fetch_pokemons_to_sanitize(cursor):
    """Busca os pokemons que ainda não possuem o name_clean preenchido."""
    query = "SELECT id, name FROM Pokemons WHERE name_clean IS NULL"
    cursor.execute(query)
    return cursor.fetchall()  # Retorna uma lista de tuplas: [(id, name), ...]

def update_pokemon_clean_name(cursor, pokemon_id, name_clean):
    """Atualiza o campo name_clean com base no ID."""
    query = "UPDATE Pokemons SET name_clean = %s WHERE id = %s"
    cursor.execute(query, (name_clean, pokemon_id))


# --- FUNÇÕES PARA A TABELA POKEMON_DATA (API) ---

def fetch_pokemon_data_to_sanitize(cursor):
    """Busca os dados da API que ainda não possuem o name_clean preenchido."""
    query = "SELECT id, name FROM Pokemon_data WHERE name_clean IS NULL"
    cursor.execute(query)
    return cursor.fetchall()

def update_pokemon_data_clean_name(cursor, pokemon_id, name_clean):
    """Atualiza o campo name_clean na tabela da API com base no ID."""
    query = "UPDATE Pokemon_data SET name_clean = %s WHERE id = %s"
    cursor.execute(query, (name_clean, pokemon_id))


# --- O MOTOR DO SCRIPT (ONDE TUDO ACONTECE) ---

def executar_limpeza_geral():
    # Instancia a classe de banco de dados que você criou
    db = Database()
    
    # Abre a conexão usando o seu gerenciador de contexto (commit automático no final)
    with db.connect() as cursor:
        if cursor is None:
            print("Erro: Não foi possível conectar ao banco de dados.")
            return

        print("=== Iniciando Sanitização da Tabela Pokemons (Scraper) ===")
        pokemons_scraper = fetch_pokemons_to_sanitize(cursor)
        
        for p_id, original_name in pokemons_scraper:
            # AQUI estamos chamando a função de sanitização!
            nome_tratado = sanitizar_nome(original_name)
            # E aqui salvamos no banco
            update_pokemon_clean_name(cursor, p_id, nome_tratado)
            
        print(f"Sucesso: {len(pokemons_scraper)} registros atualizados na tabela Pokemons.")

        print("\n=== Iniciando Sanitização da Tabela Pokemon_data (API) ===")
        pokemons_api = fetch_pokemon_data_to_sanitize(cursor)
        
        for p_id, original_name in pokemons_api:
            # AQUI chamamos a função para os dados da API!
            nome_tratado = sanitizar_nome(original_name)
            # E salvamos na tabela da API
            update_pokemon_data_clean_name(cursor, p_id, nome_tratado)
            
        print(f"Sucesso: {len(pokemons_api)} registros atualizados na tabela Pokemon_data.")

# Garante que o script só vai rodar se você executar este arquivo diretamente
if __name__ == "__main__":
    executar_limpeza_geral()