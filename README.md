# CompDaily — Savings Growth Planner

A browser-based interactive compound-interest calculator built with Streamlit and Plotly.

## Run locally

1. Install Python 3.10 or newer.
2. Open Terminal in this folder.
3. Create and activate a virtual environment:

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Launch the app:

   ```bash
   streamlit run app.py
   ```

6. Streamlit will print a local URL (usually http://localhost:8501). Open it in your browser.

## Features

- Interactive inputs for balance, annual rate, time horizon, contributions, and compounding frequency
- Start-of-period or end-of-period contributions
- Interactive growth chart with hover, zoom, and pan
- Optional comparison against a second savings plan
- Annual checkpoint table and downloadable full CSV schedule
- Explanation of assumptions and limitations

All projections are estimates, not guaranteed investment outcomes.

# Version Française 

# CompDaily

# CompDaily — Planificateur de croissance de l’épargne

Une calculatrice interactive des intérêts composés accessible dans un navigateur, développée avec Streamlit et Plotly.


## Exécuter l’application localement

1. Installe Python 3.10 ou une version plus récente.
2. Ouvre le Terminal dans ce dossier.
3. Crée et active un environnement virtuel :

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

4. Installe les dépendances :

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Lance l’application :

   ```bash
   streamlit run app.py
   ```

6. Streamlit affichera une adresse URL locale, généralement `http://localhost:8501`. Ouvre cette adresse dans ton navigateur.

## Fonctionnalités

- Champs interactifs permettant de définir le solde initial, le taux annuel, l’horizon temporel, les cotisations et la fréquence de capitalisation
- Cotisations effectuées au début ou à la fin de chaque période
- Graphique interactif de la croissance de l’épargne avec survol, zoom et déplacement
- Comparaison facultative avec un deuxième plan d’épargne
- Tableau des valeurs annuelles et téléchargement du calendrier complet des projections au format CSV
- Explication des hypothèses et des limites du calcul

Toutes les projections sont des estimations et ne garantissent pas les rendements futurs des placements.

