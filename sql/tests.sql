use pkm_scraper;
#IMPORTANTE, CONSEGUI DETECTAR DOIS TORNEIOS QUE NAO SEGUIAM O REGULAMENTO M-A e DELETEI

-- 1. Remove os movimentos dos pokémons que jogaram nesses torneios
DELETE pm FROM Pokemon_moves pm
JOIN Pokemon_teams pt ON pm.idpokemon_team = pt.id
JOIN Teams tm ON pt.team_id = tm.id
WHERE tm.tournament_id IN (8, 151, 414);

-- 2. Remove os pokémons dos times que jogaram nesses torneios
DELETE pt FROM Pokemon_teams pt
JOIN Teams tm ON pt.team_id = tm.id
WHERE tm.tournament_id IN (8, 151, 414);

-- 3. Remove os times associados a esses torneios
DELETE FROM Teams 
WHERE tournament_id IN (8, 151, 414);

-- 4. Por fim, remove os torneios da tabela principal
DELETE FROM Tournaments 
WHERE id IN (8, 151, 414);

Select COUNT(*) from moves_data;
select count(*) from pokemon_data;

select count(*) from tournaments;
select count(*) from teams;
select count(*) from pokemon_teams;

select name from pokemon_data WHERE name like '%floette%';

SELECT
    i.name AS mega_stone
FROM Pokemon_teams pt
JOIN Items i
    ON pt.item_id = i.id
WHERE
    LOWER(i.name) LIKE '%ite'
    OR LOWER(i.name) LIKE '%ite x'
    OR LOWER(i.name) LIKE '%ite y'
    OR LOWER(i.name) LIKE '%ite z'
GROUP BY i.name
ORDER BY usage_percent DESC;

SELECT
    i.name AS mega_stone,

    ROUND(
        100.0 * SUM(t.wins)
        / NULLIF(SUM(t.wins) + SUM(t.losses), 0),
        2
    ) AS winrate,
    
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM Teams),
        2
    ) AS usage_percent

FROM Pokemon_teams pt

JOIN Items i
    ON pt.item_id = i.id

JOIN Teams t
    ON pt.team_id = t.id

WHERE
    LOWER(i.name) LIKE '%ite'
    OR LOWER(i.name) LIKE '%ite x'
    OR LOWER(i.name) LIKE '%ite y'

GROUP BY i.name

HAVING COUNT(*) >= 20

ORDER BY usage_percent DESC;

SELECT
    p.name AS pokemon_name,
    pd.name AS pokemon_data_name
FROM Pokemons p
LEFT JOIN Pokemon_data pd
    ON LOWER(p.name) = LOWER(pd.name)
LIMIT 100;


-- ========================================================
-- 1. VERIFICAR TABELA POKEMONS (SCRAPER)
-- ========================================================

-- Mostra a quantidade de Pokémons que NÃO foram preenchidos
SELECT COUNT(*) AS total_nao_sanitizados 
FROM Pokemons 
WHERE name_clean IS NULL OR name_clean = '';

-- Mostra os nomes originais dos que falharam (se houver algum)
SELECT id, name, name_clean 
FROM Pokemons 
WHERE name_clean IS NULL OR name_clean = ''
LIMIT 50;


-- ========================================================
-- 2. VERIFICAR TABELA POKEMON_DATA (API)
-- ========================================================

SELECT * FROM Pokemons LIMIT 50;

UPDATE Pokemons SET name_clean = NULL;
UPDATE Pokemon_data SET name_clean = NULL;

SELECT DISTINCT 
    t.id AS torneio_id,
    t.name AS nome_torneio,
    t.date AS data_torneio,
    p.name AS nome_no_scraper
FROM Tournaments t
JOIN Teams tm ON t.id = tm.tournament_id
JOIN Pokemon_teams pt ON tm.id = pt.team_id
JOIN Pokemons p ON pt.pokemon_id = p.id
WHERE p.name LIKE '%Amoonguss%'
ORDER BY t.date DESC;

SELECT 
    pt.id, 
    pt.team_id, 
    p.name AS nome_pokemon, 
    pt.item_id, 
    pt.ability_id, 
    tm.tournament_id, 
    tm.player_id
FROM Pokemon_teams pt
JOIN Teams tm ON pt.team_id = tm.id
JOIN Pokemons p ON pt.pokemon_id = p.id
WHERE tm.tournament_id = 151;

-- 1. Ver como o Aegislash está cadastrado na tabela do Scraper
SELECT id, name, name_clean FROM Pokemons WHERE name LIKE '%Aegislash%';

-- 2. Ver como o Aegislash está cadastrado na tabela da API
SELECT id, name, name_clean FROM Pokemon_data WHERE name LIKE '%Aegislash%';

SELECT id, name, name_clean 
FROM Pokemon_data
WHERE name LIKE '%raging%' OR name_clean LIKE '%raging%';

SELECT 
    m.name AS move_name,
    COUNT(*) AS total_uses,
    ROUND(100.0 * COUNT(*) / (
        SELECT COUNT(DISTINCT pt.team_id)
        FROM Pokemon_teams pt
        JOIN Pokemons p ON pt.pokemon_id = p.id
        WHERE LOWER(p.name) LIKE '%delphox%'
    ), 2) AS usage_percent
FROM Pokemon_teams pt
JOIN Pokemons p ON pt.pokemon_id = p.id
JOIN Pokemon_moves pm ON pt.id = pm.idpokemon_team
JOIN Moves m ON pm.idmove = m.id
WHERE LOWER(p.name) LIKE '%delphox%'
GROUP BY m.name
ORDER BY total_uses DESC;

WITH ClassificacaoMoves AS (
    SELECT 
        pt.team_id, 
        pt.id AS pokemon_team_id, 
        md.damage_class
    FROM Pokemon_moves pm
    JOIN Pokemon_teams pt ON pm.idpokemon_team = pt.id
    JOIN Moves m ON pm.idmove = m.id
    -- Alteração exclusiva: Incluindo a nova associação de mapeamento que criamos
    JOIN Moves_mapping mm ON m.id = mm.move_scraper_id
    JOIN Moves_data md ON mm.move_api_id = md.id
    WHERE LOWER(md.name) NOT LIKE '%protect%'
      AND LOWER(md.name) NOT LIKE '%detect%'
      AND LOWER(md.name) NOT LIKE '%spiky shield%'
      AND LOWER(md.name) NOT LIKE '%baneful bunker%'
      AND LOWER(md.name) NOT LIKE '%kings shield%'
),
ContagemPokemon AS (
    SELECT team_id, pokemon_team_id,
        SUM(CASE WHEN LOWER(damage_class) = 'physical' THEN 1 ELSE 0 END) AS qtd_phys,
        SUM(CASE WHEN LOWER(damage_class) = 'special' THEN 1 ELSE 0 END) AS qtd_spec,
        SUM(CASE WHEN LOWER(damage_class) = 'status' THEN 1 ELSE 0 END) AS qtd_status
    FROM ClassificacaoMoves
    GROUP BY team_id, pokemon_team_id
),
PapelPokemon AS (
    SELECT team_id,
        CASE 
            WHEN qtd_status >= qtd_phys AND qtd_status >= qtd_spec THEN 'Support'
            WHEN qtd_phys >= qtd_spec THEN 'Physical'
            ELSE 'Special'
        END AS papel
    FROM ContagemPokemon
),
DistribuicaoTime AS (
    SELECT team_id,
        SUM(CASE WHEN papel = 'Physical' THEN 1 ELSE 0 END) AS phys_slots,
        SUM(CASE WHEN papel = 'Special' THEN 1 ELSE 0 END) AS spec_slots,
        SUM(CASE WHEN papel = 'Support' THEN 1 ELSE 0 END) AS supp_slots
    FROM PapelPokemon
    GROUP BY team_id
)
SELECT team_id 
FROM DistribuicaoTime 
WHERE phys_slots = 1 AND spec_slots = 1 AND supp_slots = 1
LIMIT 1;

SELECT 
    pt.team_id,
    t.wins,
    t.losses,
    ROUND(100.0 * t.wins / NULLIF(t.wins + t.losses, 0), 2) AS winrate
FROM Pokemon_teams pt
JOIN Teams t ON pt.team_id = t.id
JOIN Pokemon_mapping pmap ON pt.pokemon_id = pmap.pokemon_scraper_id
JOIN Pokemon_data pdata ON pmap.pokemon_api_id = pdata.id
WHERE LOWER(pdata.name) IN ('delphox', 'gyarados', 'garchomp', 'sneasler')
GROUP BY pt.team_id, t.wins, t.losses
HAVING COUNT(DISTINCT pdata.id) = 4;

SELECT 
    pdata.name AS pokemon_name,
    i.name AS item_name,
    h.name AS ability_name, -- Ajuste o nome da tabela/coluna de habilidades se for diferente no seu banco
    GROUP_CONCAT(mdata.name SEPARATOR ' | ') AS moveset
FROM Pokemon_teams pt
JOIN Pokemon_mapping pmap ON pt.pokemon_id = pmap.pokemon_scraper_id
JOIN Pokemon_data pdata ON pmap.pokemon_api_id = pdata.id
LEFT JOIN Items i ON pt.item_id = i.id
LEFT JOIN Abilities h ON pt.ability_id = h.id -- Ajuste aqui se a relação de habilidade estiver em outra tabela
LEFT JOIN Pokemon_moves pm ON pt.id = pm.idpokemon_team
LEFT JOIN Moves_mapping mm ON pm.idmove = mm.move_scraper_id
LEFT JOIN Moves_data mdata ON mm.move_api_id = mdata.id
WHERE pt.team_id = 8604
GROUP BY pt.id, pdata.name, i.name, h.name;