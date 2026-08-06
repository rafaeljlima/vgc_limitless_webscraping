<div align="center">
  <!-- Language Switcher -->
  <a href="./README.pt-BR.md">
    <img src="https://img.shields.io/badge/🇧🇷_Português-333333?style=for-the-badge&logoColor=white" alt="Versão em Português">
  </a>
  <a href="./README.md">
    <img src="https://img.shields.io/badge/🇺🇸_English-007ACC?style=for-the-badge&logoColor=white" alt="English Version">
  </a>
</div>

# vgc_limitless_webscraping

---

## Problem & Goal

In Pokémon VGC (Video Game Championship) competitions, team building is often guided by intuition, personal experience, or simply copying popular compositions.

> [!IMPORTANT]
> **Core Question:** Is it possible to build a top-tier competitive team strictly based on statistical evidence from recent tournaments?

> [!NOTE]
> **Author's Note:** This is my first end-to-end data analysis project. Code development for extraction, cleaning, and SQL queries utilized AI assistance (*AI-assisted coding* / *vibe coding*), allowing the main focus to remain on hypothesis formulation, statistical analysis, and strategic decision-making for the metagame.

---

## Approach & Methodology

Development of an end-to-end data pipeline:

`Web Scraping / Pokémon API` ➔ `Relational Database` ➔ `Data Cleaning & Preprocessing` ➔ `Performance & Winrate Analysis`

The objective was to drive **100% of team composition decisions** for a tournament hosted on the Limitless platform.

### 1. Web Scraping (Extraction)
* **Architecture Shift:** Initially tested with Selenium, the scraper was migrated to **BeautifulSoup** for higher efficiency and speed when processing large volumes of data.
* **Targeted Collection:** Extraction was mapped to crawl all result pages applying specific format filters, structuring detailed information for each tournament, match, player, team, and Pokémon used.
* **Data Modeling Decision (SQL):** Enforced **no UNIQUE constraints** on player names. Since the platform allows free pseudonyms, this constraint would cause false associations between teams from different players who happened to share the same nickname.

### 2. Pokémon API Integration & Fuzzy Matching
* **Data Enrichment:** The initial scraping lacked essential statistical attributes such as elemental types and base stats. To bridge this gap, a dedicated script was built to consume an external API.
* **Entity Resolution (*TheFuzz*):** Without a native primary key linking tournament Pokémon names to API records, the **TheFuzz** library was used for fuzzy string matching. Similarity score thresholds were manually calibrated to ensure accurate data linking.

### 3. Data Cleaning & Preprocessing
* **Dataset Sanitation:** Noise and inconsistencies were filtered out, such as incorrectly registered tournaments and instances containing illegal Pokémon or items according to the targeted rule set.
* **Standardizing Mega Evolution Identification:** Replaced sub-string searches (`LIKE '%ite'`) with a constant module (`imports/constants.py`) containing an explicit list of *Mega Stones*. This refactoring eliminated false positives (such as the item *Eviolite*) and scaled the pipeline to support future metagames.

---

## Insights & Solutions

### 1. Selecting the Mega Evolution (Foundation)

* **Starting Point:** Under the analyzed regulation (Regulation M-A), all top-performing teams run at least one Mega Evolution.
* **The Meta Trap:** **Mega Charizard Y** and **Mega Floette** heavily dominate usage and win rates. However, because they sit at the top of the meta, most opponents build specific counter-strategies against them. To avoid this bias, the goal was to identify a high-performing alternative with lower predictability.
* **Performance Filters:**
  * **Base Speed:** Analysis revealed that exceeding 60 Base Speed is sufficient to stabilize high win rates, proving that chasing the fastest Pokémon was not a decisive factor.
  * **Damage Category:** Special Attack-focused Megas statistically outperformed Physical Attackers.
  * **Defensive Typing:** Needed a typing that resisted key threats from Charizard Y (Fire) and Floette (Fairy). Fire-typing met both criteria.

> [!NOTE]
> **The Solution:** **Mega Delphox** satisfied all requirements: Fire-typing, high Special Attack, and win rates equivalent to top-meta choices, but with a significantly lower usage rate.

---

### 2. Rest of the Team Composition

* **Team Architecture:** The most statistically successful team archetype in this format consists of **3 physical attackers, 2 special attackers, and 1 support**.
* **Partner Selection:**
  * **Sneasler:** Top partner by usage rate alongside Mega Delphox, providing high offensive pressure and support utility.
  * **Garchomp:** Second-highest synergy and usage partner with the core choice.
  * **Clefable (Support):** Redirection moves (*Follow Me* / *Rage Powder*) did not drastically alter overall win rate, yet Pokémon with these moves appeared in virtually all top teams. Comparing frequent compositions, Clefable delivered the best performance.
  * **Mega Gyarados (Second Mega):** Teams running two Megas showed a higher overall win rate than single-Mega teams. Mega Gyarados was selected for physical presence and secondary support.
  * **Alolan Ninetales:** Filling the final spot (second special attacker), it demonstrated strong win rates and numeric synergy alongside Mega Delphox.

---

### 3. Moveset & Item Selection

* **Mega Delphox:** *Heat Wave*, *Psychic*, and *Protect* appeared in nearly 100% of successful samples. For the fourth slot, comparative analysis proved that **Encore** generated a significantly higher positive impact on win rate than *Nasty Plot* or *Calm Mind*.
* **Remaining Teammates:** Followed strict top-usage choices for items and movesets. The only exception was **Garchomp**, whose item data was overly fragmented; as a tie-breaker, *Life Orb* was selected (introduced in the subsequent Regulation M-B and historically established for Garchomp), marking the sole non-statistical choice in the research.

---

## Analysis Limitations

* **Rule Set Change (Sample Bias):** Collected data reflects Regulation M-A. The upcoming tournament will use Regulation M-B, introducing new Pokémon and items not present in the historical dataset.
* **Player Skill Factor:** Win rates reflect average player skill within the sample. The author's relative inexperience in live competitive play acts as an unisolated variable.
* **Missing Team Preview Data:** The scraper collects full 6-Pokémon team compositions and match outcomes, but cannot capture which 4 Pokémon were actually brought into battle.
* **Lack of Matchup Matrix:** Matchup-specific performance data (Team A vs. Team B) was not structured, only isolated component performance.
* **Resource Access Constraints:** Statistically, Mega Floette and Basculegion would be ideal fits over Mega Gyarados and Alolan Ninetales, but their unavailability in-game forced alternative choices.

---

## Technical Structure & Setup

```text
├── scripts/    # Scraper execution, cleaning routines, and analysis Jupyter Notebooks.
├── sql/        # DDL scripts for relational database creation and CSV exports.
└── imports/    # Auxiliary connection modules and utilities.
```

### Local Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a config.py file inside the imports/ directory with your database credentials:
```python
DB_CONFIG = {
    "host": "your_host",
    "database": "your_database",
    "user": "your_user",
    "password": "your_password"
}
```