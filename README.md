# ⚽ R-AISS-Scout-Console

A comprehensive match analysis tool built with Python. This project help scouts generates match data (Opta-style event data) and visualizes it using industry-standard metrics like Expected Threat (xT), Momentum, and Progressive Actions (Pass, Shot, Tackle) with precise pitch coordinates. User can also manage Match Context: Track game time, periods, and team performance in real-time. Export Data: Instant export of match events to CSV for integration with analysis tools.

## 📊 Visualizations Included
1.  **Match Momentum (xT):** A timeseries chart showing attacking threat over time.
2.  **Passing & Carry Maps:** Visualizing progressive lanes on a pitch.
3.  **Shot Maps:** Shot locations including outcomes (Goals, Saves, Blocks).
4.  **Heatmaps:** Spatial density of team possession.
5.  **Player Radars:** Attacking vs. Defensive contribution profiles.
6.  **xT Leaderboards:** Stacked bar charts for Pass vs. Carry threat creation.

## 🛠️ Tech Stack
* **Python 3.9+**
* **mplsoccer:** For plotting accurate football pitches.
* **Pandas:** For data manipulation and event filtering.
* **Matplotlib / Seaborn:** For custom visualization styling.
* **Scipy:** For Gaussian smoothing of momentum data.

## 🚀 How to Run
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate Data:**
    Run the data generator to create a unique match:
    ```bash
    python src/01_generate_data.py
    ```

3.  **Generate Visuals:**
    Run any of the analysis scripts, for example:
    ```bash
    python src/02_heatmap.py
    python src/06_shot_map.py
    ```

## 📂 Project Structure
* `src/`: Contains all analysis scripts.
* `data/`: Stores the generated CSV match data.
* `output/`: Stores the resulting high-resolution PNGs.

---
*Created as a Python Sports Analytics Portfolio Project.*
