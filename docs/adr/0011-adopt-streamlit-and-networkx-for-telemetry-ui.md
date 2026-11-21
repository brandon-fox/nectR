# Adopt Streamlit and NetworkX for Telemetry UI

* Status: accepted
* Deciders: nectR System Design & Visualization Architecture
* Date: 2026-11-21

## Context and Problem Statement

`src/nectr/ui/__init__.py` is currently a placeholder, and maintainers need a read-only interactive dashboard for the Knowledge Graph, Collusion Matrix, Gini index, and Comb reserves.

## Considered Options

* **`streamlit` (Apache-2.0) + `networkx` (BSD-3-Clause) read-only dashboard**
* **`marimo` (Apache-2.0) reactive notebook UI**
* **Custom React + Vite frontend**

## Decision Outcome

Chosen option: "`streamlit` + `networkx` read-only dashboard", because Streamlit renders Python-native data, Matplotlib/Plotly charts, and NetworkX graphs with minimal boilerplate, zero Node.js build tooling, and strict read-only separation from `HiveServiceLayer`.

### Consequences

* Good, because `src/nectr/ui/` stays pure Python, fast to iterate, and isolated from write-side contract logic.
* Bad, because Streamlit reruns scripts on widget interaction, requiring `@st.cache_data` for large epoch logs.
