import os
import sys

# Descobre o caminho absoluto do diretório onde o script 'cleaning_move.py' está guardado
script_dir = os.path.dirname(os.path.abspath(__file__))

# Sobe um nível para chegar na raiz do projeto (PkmScrapper) onde fica a pasta 'imports'
projeto_raiz = os.path.abspath(os.path.join(script_dir, ".."))

# Adiciona a raiz do projeto no caminho de busca do Python
if projeto_raiz not in sys.path:
    sys.path.append(projeto_raiz)

import re
from difflib import SequenceMatcher
from imports.database import Database 

SCORE_MINIMO = 82

def sanitizar_nome(nome):
    if not nome:
        return ""
    nome_limpo = nome.lower()
    nome_limpo = re.sub(r'[-_\.]', ' ', nome_limpo)
    nome_limpo = " ".join(nome_limpo.split())
    return nome_limpo

def calcular_score(string1, string2):
    """Calcula a similaridade entre duas strings de 0 a 100."""
    return int(SequenceMatcher(None, string1, string2).ratio() * 100)

# --- FUNÇÕES DE BUSCA E ATUALIZAÇÃO ---

def fetch_moves_to_sanitize(cursor):
    """Busca movimentos do Scraper que ainda não têm name_clean."""
    cursor.execute("SELECT id, name FROM Moves WHERE name_clean IS NULL")
    return cursor.fetchall()

def update_move_clean_name(cursor, move_id, name_clean):
    """Atualiza o name_clean na tabela Moves."""
    cursor.execute("UPDATE Moves SET name_clean = %s WHERE id = %s", (name_clean, move_id))

def fetch_moves_data_to_sanitize(cursor):
    """Busca movimentos da API que ainda não têm name_clean."""
    cursor.execute("SELECT id, name FROM Moves_data WHERE name_clean IS NULL")
    return cursor.fetchall()

def update_moves_data_clean_name(cursor, move_id, name_clean):
    """Atualiza o name_clean na tabela Moves_data."""
    cursor.execute("UPDATE Moves_data SET name_clean = %s WHERE id = %s", (name_clean, move_id))

def fetch_all_cleaned_moves(cursor):
    """Busca todos do scraper para mapear."""
    cursor.execute("SELECT id, name_clean, name FROM Moves")
    return cursor.fetchall()

def fetch_all_cleaned_moves_data(cursor):
    """Busca todos da API para comparar."""
    cursor.execute("SELECT id, name_clean, name FROM Moves_data")
    return cursor.fetchall()

def limpar_mapeamento_anterior(cursor):
    """Garante uma execução limpa limpando o mapeamento antigo."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE Moves_mapping;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

def inserir_mapeamento(cursor, scraper_id, api_id, score):
    """Insere o link de alias na tabela final."""
    query = """
    INSERT INTO Moves_mapping (move_scraper_id, move_api_id, score) 
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE move_api_id = VALUES(move_api_id), score = VALUES(score);
    """
    cursor.execute(query, (scraper_id, api_id, score))

# --- MOTOR DE EXECUÇÃO REAL ---

def executar_processamento_moves():
    db = Database()
    
    with db.connect() as cursor:
        if cursor is None:
            print("❌ Erro: Não foi possível conectar ao banco de dados.")
            return

        # ---------------------------------------------------------------------
        # FASE 1: HIGIENIZAÇÃO (Sanitização dos campos de texto)
        # ---------------------------------------------------------------------
        print("=== 1. Iniciando Sanitização dos Nomes ===")
        
        moves_scraper_pendentes = fetch_moves_to_sanitize(cursor)
        for m_id, original_name in moves_scraper_pendentes:
            update_move_clean_name(cursor, m_id, sanitizar_nome(original_name))
            
        moves_api_pendentes = fetch_moves_data_to_sanitize(cursor)
        for m_id, original_name in moves_api_pendentes:
            update_moves_data_clean_name(cursor, m_id, sanitizar_nome(original_name))
            
        print(f"   ↳ {len(moves_scraper_pendentes)} registros sanitizados na tabela Moves.")
        print(f"   ↳ {len(moves_api_pendentes)} registros sanitizados na tabela Moves_data.")

        # ---------------------------------------------------------------------
        # FASE 2: RELACIONAMENTO & GRAVAÇÃO (Fuzzy Matching com filtro Score >= 82)
        # ---------------------------------------------------------------------
        print("\n=== 2. Calculando Links e Gravando no Banco ===")
        print("   ⚠️  Limpando registros antigos da tabela Moves_mapping...")
        limpar_mapeamento_anterior(cursor)

        moves_scraper = fetch_all_cleaned_moves(cursor)
        moves_api = fetch_all_cleaned_moves_data(cursor)
        
        total_gravados = 0
        total_ignorados = 0

        for s_id, s_clean, s_original in moves_scraper:
            melhor_match_id = None
            maior_score = -1
            
            for api_id, api_clean, api_original in moves_api:
                score = calcular_score(s_clean, api_clean)
                
                if score == 100:
                    melhor_match_id = api_id
                    maior_score = score
                    break
                    
                if score > maior_score:
                    maior_score = score
                    melhor_match_id = api_id

            # Aplica a sua trava de segurança combinada (Score >= 82)
            if melhor_match_id is not None and maior_score >= SCORE_MINIMO:
                inserir_mapeamento(cursor, s_id, melhor_match_id, maior_score)
                total_gravados += 1
            else:
                total_ignorados += 1

        print(f"\n🚀 Processo concluído com sucesso!")
        print(f"   🔹 Total de movimentos mapeados (Score >= {SCORE_MINIMO}%): {total_gravados}")
        print(f"   🔸 Total de movimentos ignorados por score baixo: {total_ignorados}")

if __name__ == "__main__":
    executar_processamento_moves()