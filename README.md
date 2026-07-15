# Market Microstructure Systematic Risk Simulator

A Streamlit-based simulation sandbox for exploring how AI-driven agents, sentiment shocks, and options hedging can amplify market stress into systemic risk and flash-crash dynamics.

[![Live Status on Render](https://img.shields.io/badge/Render-Live%20Status-success?logo=render)](https://your-app-name.onrender.com)

[![Open Live App](https://img.shields.io/badge/Live%20Demo-Open%20App-blue?logo=render)](https://your-app-name.onrender.com)

> Replace the Render URL above with your deployed app link once the project is live.

## What this project does

- Simulates a multi-agent market with an NLP sentiment agent, a quantitative hedging agent, and an options market maker.
- Injects macroeconomic panic scenarios and visualizes how forced hedging can cascade into wider market stress.
- Supports live market initialization using the Polygon.io API for a more realistic starting state.

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