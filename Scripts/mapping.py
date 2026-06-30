from thefuzz import fuzz
from PkmScrapper.Imports.database import Database

def fetch_all_scraper_pokemons(cursor):
    """Busca ID e nome_clean de todos os pokémons do Scraper."""
    query = "SELECT id, name, name_clean FROM Pokemons"
    cursor.execute(query)
    return cursor.fetchall() # Retorna [(id, name, name_clean), ...]

def fetch_all_api_pokemons(cursor):
    """Busca ID e nome_clean de todos os pokémons da API."""
    query = "SELECT id, name, name_clean FROM Pokemon_data"
    cursor.execute(query)
    return cursor.fetchall() # Retorna [(id, name, name_clean), ...]

def gerar_preview_casamento():
    db = Database()
    
    with db.connect() as cursor:
        if cursor is None:
            print("Erro ao conectar ao banco.")
            return
        
        print("Buscando dados do banco...")
        pokemons_scraper = fetch_all_scraper_pokemons(cursor)
        pokemons_api = fetch_all_api_pokemons(cursor)
        
        resultados = []
        
        print("Processando similaridades (Fuzzy Matching)...")
        # Para cada pokémon do seu scraper...
        for scr_id, scr_orig, scr_clean in pokemons_scraper:
            melhor_score = -1
            melhor_match_api_orig = None
            melhor_match_api_clean = None
            
            # Compara contra TODOS os pokémons que vieram da API
            for api_id, api_orig, api_clean in pokemons_api:
                # Usando o token_sort_ratio como o Ronaldinho sugeriu
                score = fuzz.token_sort_ratio(scr_clean, api_clean)
                
                # Se achou um score maior, atualiza o melhor match para este pokémon
                if score > melhor_score:
                    melhor_score = score
                    melhor_match_api_orig = api_orig
                    melhor_match_api_clean = api_clean
            
            # Guarda o resultado encontrado para este pokémon do scraper
            resultados.append({
                'scraper_orig': scr_orig,
                'api_orig': melhor_match_api_orig,
                'score': melhor_score
            })
        
        # Ordena a lista de resultados pelo SCORE de forma CRESCENTE (menores primeiro)
        # Assim você vê logo no topo da tabela onde o algoritmo começou a errar ou fraquejar
        resultados_ordenados = sorted(resultados, key=lambda x: x['score'])
        
        # Exibe os resultados formatados no terminal
        print("\n" + "="*80)
        print(f"{'NOME SCRAPER':<28} | {'NOME API':<28} | {'SCORE':<5}")
        print("="*80)
        
        for r in resultados_ordenados:
            print(f"{r['scraper_orig']:<28} | {r['api_orig']:<28} | {r['score']:<5}")
            
        print("="*80)
        print(f"Total de Pokémons analisados: {len(resultados)}")

if __name__ == "__main__":
    gerar_preview_casamento()