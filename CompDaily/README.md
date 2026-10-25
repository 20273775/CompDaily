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
# CompDaily
