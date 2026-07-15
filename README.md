# Market Microstructure Systematic Risk Simulator

A Streamlit-based simulation sandbox for exploring how AI-driven agents, sentiment shocks, and options hedging can amplify market stress into systemic risk and flash-crash dynamics.

[![Live App on Render](https://img.shields.io/badge/Render-Live%20App-success?logo=render)](https://market-microstructure-systematic-risk.onrender.com/)

[![Research Paper](https://img.shields.io/badge/Research-Engineering_the_Future_of_Capital_Markets-A200FF?style=for-the-badge)](https://ijirt.org/publishedpaper/IJIRT199058_PAPER.pdf)

**The applied simulation for the research paper *Engineering the Future of Capital Markets: A Multi-Agent Systemic Risk Analysis of AI in Trading and Banking*.**

A Streamlit-based simulation sandbox for exploring how AI-driven agents, macroeconomic sentiment shocks, and **Zero-Cost Collar** options hedging can amplify market stress into systemic risk and flash-crash dynamics. Engineered specifically for resource-constrained, zero-cost cloud environments.

## What this project does

- Simulates a multi-agent market with an NLP sentiment agent, a quantitative hedging agent, and an options market maker.
- Injects macroeconomic panic scenarios and visualizes how forced hedging can cascade into wider market stress.
- Supports live market initialization using the Polygon.io API for a more realistic starting state.

## 🧠 The Quantitative Thesis (Research Integration)
This codebase visually and mathematically proves the danger of procyclical feedback loops discussed in the foundational research. When an exogenous macroeconomic shock occurs, institutional AI algorithms automatically execute **Zero-Cost Collars** to buy downside protection. The Options Market Makers selling this protection are mathematically forced to short-sell the underlying asset to remain delta-neutral. In a low-liquidity environment, this forced short-selling evaporates the order book, driving the price down further and triggering even more algorithmic hedging, resulting in a localized flash crash.

## ⚡ Engineering for Constraint (The Cloud Workaround)
Traditional microstructure simulations require heavy institutional compute. A core technical achievement of this project is its architectural optimization, allowing complex high-frequency interactions to run fluidly on **zero-cost, low-memory cloud environments** (e.g., Render's free tier).
* **UI Frame Batching:** Prevents React DOM/WebSocket bottlenecks by batching Plotly JSON visual renders, paired with a calculated thread sleep to clear browser paint queues.
* **Dynamic Memory Management:** Actively flushes and resets rendering arrays to stay well under the 512MB RAM limits of free container tiers.
* **Lightweight Data Seeding:** Utilizes single-call REST architecture to Polygon.io for market state initialization, avoiding the bandwidth drain of constant live data streams.

## Tech stack

- Python
- Streamlit
- Plotly
- Polygon.io API

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

- `app.py` — main Streamlit dashboard
- `matching_engine.py` — market simulation engine
- `simulation_agents.py` — agent behavior logic
- `data_ingestion.py` — Polygon data integration
- `options_pricer.py` — option pricing utilities


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
