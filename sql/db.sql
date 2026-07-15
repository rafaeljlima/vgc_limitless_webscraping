DROP DATABASE pkm_scraper;
CREATE DATABASE Pkm_scraper;
USE Pkm_scraper;

CREATE TABLE Tournaments (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    qtplayers INT NOT NULL
);

CREATE TABLE Pokemon_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type1 VARCHAR(30) NOT NULL,
    type2 VARCHAR(30),
    hp INT NOT NULL,
    attack INT NOT NULL,
    defense INT NOT NULL,
    special_attack INT NOT NULL,
    special_defense INT NOT NULL,
    speed INT NOT NULL
);

CREATE TABLE Moves_data(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    damage_class VARCHAR(30) NOT NULL,
    type VARCHAR(30) NOT NULL,
    accuracy INT,
    power INT
);

CREATE TABLE Pokemons (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
    
CREATE TABLE Players (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Moves (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Items (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Abilities (
	id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Teams (
	id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_id INT NOT NULL,
    player_id INT NOT NULL,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,

    FOREIGN KEY (tournament_id) REFERENCES Tournaments(id)
        ON DELETE CASCADE,

    FOREIGN KEY (player_id) REFERENCES Players(id)
);

CREATE TABLE Pokemon_teams (
	id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    pokemon_id INT NOT NULL,
    item_id INT NOT NULL,
    ability_id INT NOT NULL,
    
    FOREIGN KEY (team_id) REFERENCES Teams(id)
        ON DELETE CASCADE,

    FOREIGN KEY (pokemon_id) REFERENCES Pokemons(id),

    FOREIGN KEY (item_id) REFERENCES Items(id),

    FOREIGN KEY (ability_id) REFERENCES Abilities(id)
);

CREATE TABLE Pokemon_moves (
	id INT AUTO_INCREMENT PRIMARY KEY,
    idpokemon_team INT NOT NULL,
    idmove INT NOT NULL,
    
    FOREIGN KEY (idpokemon_team) REFERENCES Pokemon_teams(id)
        ON DELETE CASCADE,

    FOREIGN KEY (idmove) REFERENCES Moves(id)
);

ALTER TABLE Pokemon_data ADD COLUMN name_clean VARCHAR(100);
ALTER TABLE Pokemons ADD COLUMN name_clean VARCHAR(100);

CREATE TABLE Pokemon_mapping (
    pokemon_scraper_id INT,
    pokemon_api_id INT,
    score INT,
    PRIMARY KEY (pokemon_scraper_id),
    FOREIGN KEY (pokemon_scraper_id) REFERENCES Pokemons(id),
    FOREIGN KEY (pokemon_api_id) REFERENCES Pokemon_data(id)
);

ALTER TABLE Tournaments ADD COLUMN format VARCHAR(100);
UPDATE Tournaments SET format = 'M-A';

ALTER TABLE Moves_data ADD COLUMN name_clean VARCHAR(100);
ALTER TABLE Moves ADD COLUMN name_clean VARCHAR(100);

CREATE TABLE Moves_mapping (
    move_scraper_id INT,
    move_api_id INT,
    score INT,
    PRIMARY KEY (move_scraper_id),
    FOREIGN KEY (move_scraper_id) REFERENCES Moves(id),
    FOREIGN KEY (move_api_id) REFERENCES Moves_data(id)
);