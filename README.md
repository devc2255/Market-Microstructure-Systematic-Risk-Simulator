# Market Microstructure & Systemic Risk Simulator

A Streamlit-based simulation sandbox for exploring how AI-driven agents, sentiment shocks, and options hedging can amplify market stress into systemic risk and flash-crash dynamics.

**The applied simulation for the research paper *Engineering the Future of Capital Markets: A Multi-Agent Systemic Risk Analysis of AI in Trading and Banking*.**

A Streamlit-based simulation sandbox for exploring how AI-driven agents, macroeconomic sentiment shocks, and **Zero-Cost Collar** options hedging can amplify market stress into systemic risk and flash-crash dynamics. Engineered specifically for resource-constrained, zero-cost cloud environments.


[![Live Status on Render](https://img.shields.io/badge/Render-Live%20Status-success?logo=render)](https://market-microstructure-systemic-risk.onrender.com)

[![Paper](https://img.shields.io/badge/Research_Paper-Engineering_the_Future_of_Capital_Markets%3A_A_Multi--Agent_Systemic_Risk_Analysis-A200FF?style=for-the-badge)](https://ijirt.org/publishedpaper/IJIRT199058_PAPER.pdf)

## What this project does

* **Multi-Agent Ecosystem:** Simulates a market with an NLP sentiment agent, a quantitative hedging agent, and an options market maker.
* **Flash Crash Dynamics & VIX Spikes:** Injects macroeconomic panic scenarios, dynamically multiplying implied volatility ($\sigma \times 3.0$) to accurately model structural market fear and cascading forced hedging.
* **Live Market Seeding:** Supports live market initialization using the Polygon.io API for a more realistic starting state.
* **Granular Portfolio Risk Management:** Acts as a portfolio management sandbox, allowing users to dynamically select target hedge amounts.
* **Microstructure Mechanics (Lot Sizes):** Enforces real-world options lot constraints (100 shares per contract), tracking and exposing fractional "Orphan Shares" to unhedged market liquidity vacuums.
* **Interactive P&L & Gamified Risk Grading:** Calculates exact dollar amounts saved vs. lost post-simulation, assigning a 5-tier dynamic risk grade (from *Catastrophic Exposure* to *Ironclad Hedge*) based on the user's hedge ratio and risk management decisions.
* **Cloud-Optimized Rendering:** Features memory-safe UI frame batching to prevent WebSocket crashes and browser RAM overloads on free-tier cloud architectures.

## Tech stack

* Python
* Streamlit
* Plotly
* Polygon.io API
* NumPy
* SciPy

## Getting started

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install the dependencies:
```bash
pip install -r requirements.txt

```


4. Set your Polygon API key as an environment variable:
```bash
export POLYGON_KEY="your_api_key"

```


5. Run the app:
```bash
streamlit run app.py

```



## Render deployment

To deploy this project on Render:

1. Create a new Web Service on Render and connect this repository.
2. Use the following build command:
```bash
pip install -r requirements.txt

```


3. Use the following start command:
```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0

```


4. Add your Polygon API key as an environment variable named `POLYGON_KEY`.
5. Replace the placeholder URL in the badge above with your live Render deployment link.

## Project structure

* `app.py` — main Streamlit dashboard
* `matching_engine.py` — market simulation engine
* `simulation_agents.py` — agent behavior logic
* `data_ingestion.py` — Polygon data integration
* `options_pricer.py` — option pricing utilities

## 📄 Academic Citation

If you are reviewing this codebase for academic or institutional purposes, please refer to the foundational published research:

* **Chhaya, D. V., & Patel, S. (2026). Engineering In Financial Markets. International Journal of Innovative Research in Technology (IJIRT), 12(11), 11002–11010.**
* **Application:** This repository serves as the live, interactive data model demonstrating the paper's theoretical framework regarding AI-driven microstructure risks.

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
