import os, sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

from thefuzz import fuzz
from imports.database import Database

def fetch_all_scraper_pokemons(cursor):
    query = "SELECT id, name, name_clean FROM Pokemons"
    cursor.execute(query)
    return cursor.fetchall()

def fetch_all_api_pokemons(cursor):
    query = "SELECT id, name, name_clean FROM Pokemon_data"
    cursor.execute(query)
    return cursor.fetchall()

def salvar_mapeamento(cursor, dados_mapeamento):
    query = """
        REPLACE INTO Pokemon_mapping (pokemon_scraper_id, pokemon_api_id, score)
        VALUES (%s, %s, %s)
    """
    cursor.executemany(query, dados_mapeamento)

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

def executar_mapeamento():
    db = Database()
    
    with db.connect() as cursor:
        if cursor is None:
            print("Erro ao conectar ao banco.")
            return
        
        print("Buscando dados do banco...")
        pokemons_scraper = fetch_all_scraper_pokemons(cursor)
        pokemons_api = fetch_all_api_pokemons(cursor)
        
        dados_para_salvar = []
        preview_relatorio = []
        
        print("Processando mapeamento estratégico...")
        for scr_id, scr_orig, scr_clean in pokemons_scraper:
            
            if scr_clean in EXCECOES_MAPEAMENTO:
                nome_alvo_api = EXCECOES_MAPEAMENTO[scr_clean]
                
                for api_id, api_orig, api_clean in pokemons_api:
                    if api_clean == nome_alvo_api:
                        dados_para_salvar.append((scr_id, api_id, 100))
                        preview_relatorio.append({
                            'scraper_orig': scr_orig,
                            'api_orig': api_orig,
                            'score': 100
                        })
                        break
                continue

            melhor_score = -1
            melhor_match_id = None
            melhor_match_api_orig = None
            
            for api_id, api_orig, api_clean in pokemons_api:
                score = fuzz.token_sort_ratio(scr_clean, api_clean)
                
                if score > melhor_score:
                    melhor_score = score
                    melhor_match_id = api_id
                    melhor_match_api_orig = api_orig
            
            if melhor_match_id is not None:
                dados_para_salvar.append((scr_id, melhor_match_id, melhor_score))
                preview_relatorio.append({
                    'scraper_orig': scr_orig,
                    'api_orig': melhor_match_api_orig,
                    'score': melhor_score
                })
        
        print(f"Salvando {len(dados_para_salvar)} registros na tabela Pokemon_mapping...")
        salvar_mapeamento(cursor, dados_para_salvar)
        print("Sucesso: Mapeamento persistido com êxito!")

        resultados_ordenados = sorted(preview_relatorio, key=lambda x: x['score'])
        
        print("\n" + "="*80)
        print(f"{'NOME SCRAPER':<28} | {'NOME API':<28} | {'SCORE':<5}")
        print("="*80)
        for r in resultados_ordenados:
            print(f"{r['scraper_orig']:<28} | {r['api_orig']:<28} | {r['score']:<5}")
        print("="*80)
        print(f"Total de Pokémons mapeados e salvos: {len(dados_para_salvar)}")

if __name__ == "__main__":
    executar_mapeamento()