# vgc_limitless_webscraping

---

## Problema & Objetivo

Nas competições de Pokémon VGC (Video Game Championship), a montagem de times costuma ser guiada por intuição, experiência pessoal ou pela simples cópia de composições populares. 

> **Provocação Central:** É possível construir um time competitivo de alto nível baseado estritamente em evidências estatísticas de torneios recentes?

---

## Abordagem

Desenvolvimento de uma pipeline de dados completa:

`Web Scraping / Pokémon API` ➔ `Banco Relacional` ➔ `Tratamento e Limpeza` ➔ `Análise de Performance e Winrate`

O objetivo foi direcionar **100% das decisões de composição** para um torneio realizado na plataforma Limitless.

---

## Insights & Soluções

### 1. Escolha da Mega Evolução (Fundação)

* **Ponto de Partida:** No regulamento analisado (Regulation M-A), todas as equipes de alto desempenho utilizam ao menos uma Mega Evolução.
* **A Armadilha do Meta:** **Mega Charizard Y** e **Mega Floette** lideram isoladamente em taxa de uso e vitórias. No entanto, por integrarem o topo do metagame, a maioria dos oponentes já constrói estratégias específicas para anulá-los. Para fugir desse viés, buscou-se uma alternativa de alto rendimento, mas com menor previsão de combate.
* **Filtros de Desempenho:**
  * **Velocidade Base:** A análise indicou que ultrapassar 60 de Speed base é suficiente para estabilizar a taxa de vitória em patamares elevados, mostrando que buscar o Pokémon mais rápido não era um fator determinante.
  * **Categoria de Dano:** Megas focadas em Ataque Especial apresentaram desempenho estatístico superior às de Ataque Físico.
  * **Tipagem Defensiva:** Era necessário um tipo que resistisse às ameaças de Charizard Y (Fogo) e Floette (Fada). O tipo Fogo atendeu a ambos os critérios.

> **A Solução:** A **Mega Delphox** reuniu todos os requisitos: tipagem Fogo, alto Ataque Especial e estatísticas de vitória equivalentes às opções do topo do meta, porém com uma taxa de uso significativamente menor.

---

### 2. Composição do Restante do Time

* **Arquitetura da Equipe:** A estrutura estatística de maior sucesso no formato é composta por **3 atacantes físicos, 2 atacantes especiais e 1 suporte**.
* **Definição dos Parceiros:**
  * **Sneasler:** Primeiro Pokémon com maior taxa de uso ao lado de Mega Delphox, agregando valor ofensivo e utilidade de suporte.
  * **Garchomp:** Segundo parceiro de maior sinergia e uso estatístico com a base escolhida.
  * **Clefable (Suporte):** Na busca por suportes, notou-se que golpes de redirecionamento (*Follow Me* / *Rage Powder*) não alteravam出 drasticamente o winrate geral. Avaliando as composições fixas mais frequentes, Clefable destacou-se com o melhor rendimento.
  * **Mega Gyarados (Segunda Mega):** A análise de times que utilizavam duas Megas mostrou uma taxa de vitória superior àqueles com apenas uma. Mega Gyarados foi escolhido por entregar presença física e suporte secundário.
  * **Ninetales de Alola:** Fechando a estrutura (segundo atacante especial), apresentou excelente taxa de vitória e sinergia em números integrada ao lado de Mega Delphox.

---

### 3. Seleção de Moveset e Itens

* **Mega Delphox:** *Heat Wave*, *Psychic* e *Protect* figuraram em quase 100% das amostras de sucesso. Para a quarta vaga, a análise comparativa provou que o movimento **Encore** gerava um impacto em winrate significativamente superior a *Nasty Plot* e *Calm Mind*.
* **Demais Integrantes:** A regra geral seguiu a escolha estrita dos itens e golpes de maior uso. A única exceção pontual foi o **Garchomp**, que apresentava dados de itens muito dispersos; para o desempate, optou-se pelo item *Life Orb*, introduzido no regulamento M-B seguinte e historicamente consolidado para o Pokémon.

---

## Limitações da Análise

* **Mudança de Regulamento (Viés de Amostra):** Os dados coletados referem-se à Regulation M-A. O torneio disputado utilizará a Regulation M-B, que introduz novos Pokémon e itens não contemplados na base histórica.
* **Fator Piloto:** O winrate reflete a habilidade média dos jogadores da amostra. A inexperiência do autor em cenários competitivos reais atua como uma variável externa não isolada pelo modelo.
* **Ausência de Dados de Seleção (Team Preview):** O scraper coleta a composição de 6 Pokémon e o resultado da partida, mas não registra quais 4 Pokémon foram efetivamente escolhidos para entrar em campo.
* **Ausência de Matriz de Confrontos (Matchups):** Não foram estruturados dados de desempenho de um time específico enfrentando outro time específico, apenas o rendimento isolado dos componentes.
* **Restrição de Acesso a Recursos:** Estatisticamente, Mega Floette e Basculegion seriam os encaixes ideais para fechar a equipe, mas a indisponibilidade desses Pokémon no jogo limitou sua escolha.

---

## Estrutura Técnica & Como Executar

```text
├── scripts/    # Execução do scraper, rotinas de limpeza e Jupyter Notebook das análises.
├── sql/        # Scripts DDL para criação do banco de dados relacional e exportações CSV.
└── imports/    # Módulos auxiliares de conexão e utilitários.
```

### Instalação Local

1. Instale as dependências listadas no projeto:
```bash
pip install -r requirements.txt
```

2. Crie o arquivo `config.py` dentro do diretório `imports/` com as credenciais do seu banco de dados:
```python
DB_CONFIG = {
    "host": "seu_host",
    "database": "seu_banco",
    "user": "seu_usuario",
    "password": "sua_senha"
}
```