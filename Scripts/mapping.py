from thefuzz import fuzz
from Imports.database import Database

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

EXCECOES_MAPEAMENTO = {
    "maushold": "maushold family of four",
    "paldean tauros": "tauros paldea combat breed",
    "aegislash": "aegislash shield",
    "aegislash blade forme": "aegislash shield",
    "palafin": "palafin zero",
    "morpeko": "morpeko full belly",
    "mimikyu": "mimikyu disguised",
    "tatsugiri": "tatsugiri curly"
}

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
        
        print("Processando similaridades (Com Dicionário de Exceções)...")
        for scr_id, scr_orig, scr_clean in pokemons_scraper:
            
            # --- REGRA 1: VERIFICA SE ESTÁ NAS EXCEÇÕES MANUAIS ---
            if scr_clean in EXCECOES_MAPEAMENTO:
                nome_alvo_api = EXCECOES_MAPEAMENTO[scr_clean]
                
                # Busca os dados reais desse alvo na lista da API para manter o preview correto
                for api_id, api_orig, api_clean in pokemons_api:
                    if api_clean == nome_alvo_api:
                        resultados.append({
                            'scraper_orig': scr_orig,
                            'api_orig': api_orig,
                            'score': 100  # Forçamos o score 100 fixo para as nossas exceções
                        })
                        break
                continue  # Vai para o próximo Pokémon do scraper, pulando o Fuzzy Match!

            # --- REGRA 2: SE NÃO FOR EXCEÇÃO, RODA O FUZZY MATCHING NORMAL ---
            melhor_score = -1
            melhor_match_api_orig = None
            
            for api_id, api_orig, api_clean in pokemons_api:
                score = fuzz.token_sort_ratio(scr_clean, api_clean)
                
                if score > melhor_score:
                    melhor_score = score
                    melhor_match_api_orig = api_orig
            
            resultados.append({
                'scraper_orig': scr_orig,
                'api_orig': melhor_match_api_orig,
                'score': melhor_score
            })
        
        # Ordena a lista de resultados pelo SCORE de forma CRESCENTE (menores primeiro)
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