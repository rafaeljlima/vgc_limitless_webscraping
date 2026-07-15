# vgc_limitless_webscraping
Web scraper construído para escanear, tratar e povoar um banco de dados com resultados de campeonatos recentes de Pokémon VGC, servindo de base para análises de dados e geração de insights estatísticos.

O scraper varre o site Limitless buscando torneios que utilizam a Regulation M-A. A estrutura foi desenhada para facilitar a futura expansão para o regulamento M-B e a integração com outras plataformas de torneio.

Estrutura do Projeto:
    scripts/: Contém os scripts de execução do scraper, rotinas de limpeza de dados e o Jupyter Notebook contendo os gráficos e insights gerados.
    sql/: Contém o script DDL para a criação da estrutura do banco de dados relacional e as extrações em arquivos CSV usadas nas análises.
    imports/: Módulos auxiliares de conexão e utilitários.
    
Para rodar o projeto localmente, crie um arquivo chamado config.py dentro do diretório imports/ com as suas credenciais do banco de dados:
    DB_CONFIG = {
        "host": "seu_host",
        "database": "seu_banco",
        "user": "seu_usuario",
        "password": "sua_senha"
    }