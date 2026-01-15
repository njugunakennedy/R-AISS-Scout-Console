import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import PyPizza

# --- CONFIGURATION ---
CSV_FILE = 'data/full_match_data.csv'  # Linked to the generator output
OUTPUT_IMAGE = 'output/radar_chart_attack_defense.png'
# Choose a player likely to have mixed actions (e.g., a midfielder like H6, H8, A6, A8)
TARGET_PLAYER = 'H8'  

# Colors
ATTACK_COLOR = "#ef4444" # Red
DEFENSE_COLOR = "#3b82f6" # Blue
BG_COLOR = "#1A1A1D"
TEXT_COLOR = "white"

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows.")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. FILTER FOR PLAYER
player_df = df[df['Player'] == TARGET_PLAYER].copy()

if player_df.empty:
    print(f"Error: No data found for player {TARGET_PLAYER}. Check player ID.")
    exit()

print(f"Analyzing {len(player_df)} events for {TARGET_PLAYER}...")

# 3. DEFINE CATEGORIES & CALCULATE
# Based on the events the generator produces:
attack_events = ['Pass', 'Dribble', 'Reception', 'Cross', 'Shot']
defense_events = ['Interception'] # The generator primarily uses interceptions for defense

params = []
values = []
slice_colors = []

# --- Attacking Loop ---
for event in attack_events:
    count = len(player_df[player_df['Event'] == event])
    params.append(event)
    values.append(count)
    slice_colors.append(ATTACK_COLOR)

# --- Defensive Loop ---
for event in defense_events:
    count = len(player_df[player_df['Event'] == event])
    # Use abbreviation for chart neatness
    label = "Interc." if event == "Interception" else event
    params.append(label)
    values.append(count)
    slice_colors.append(DEFENSE_COLOR)


# 4. SETUP PIZZA CHART
# Dynamic Range Helper so charts look good regardless of counts
def get_max_range(val):
    # Ensure minimum scale of 5, otherwise scale to value + padding
    return max(val + 2, 5)

max_range = [get_max_range(v) for v in values]
min_range = [0] * len(params)

# Create the Pizza object
pizza = PyPizza(
    params=params,
    min_range=min_range,
    max_range=max_range,
    background_color=BG_COLOR,
    straight_line_color=TEXT_COLOR,
    last_circle_lw=1,
    other_circle_lw=1,
    inner_circle_size=20
)

# 5. DRAW CHART
fig, ax = pizza.make_pizza(
    values,
    figsize=(8, 8),
    param_location=110,
    # Here we pass the list of colors instead of a single color
    kwargs_slices=dict(
        facecolor=slice_colors, 
        edgecolor=BG_COLOR,
        linewidth=2,
        zorder=2
    ),
    kwargs_params=dict(
        color=TEXT_COLOR, 
        fontsize=11,
        fontweight='bold',
        va="center"
    ),
    kwargs_values=dict(
        color=TEXT_COLOR, 
        fontsize=10,
        fontweight='bold',
        # We use a neutral background for values to ensure readability over red/blue
        bbox=dict(edgecolor=TEXT_COLOR, facecolor="#333333", boxstyle="round,pad=0.2", lw=1),
        zorder=3
    )
)

# 6. TITLES & LEGEND
# Main Title
fig.text(
    0.515, 0.97, f"{TARGET_PLAYER} - Action Profile", 
    size=20, ha="center", color=TEXT_COLOR, fontweight='bold'
)

# Subtitle/Legend
fig.text(
    0.515, 0.93, 
    "■ Attacking Actions  |  ■ Defensive Actions", 
    size=12, ha="center", color="#94a3b8", fontweight='bold'
)
# Manually color the legend squares in the subtitle text using coordinates isn't easiest in matplotlib text.
# A simpler way is to add colored text bits:
fig.text(0.35, 0.93, "■", size=12, ha="center", color=ATTACK_COLOR)
fig.text(0.61, 0.93, "■", size=12, ha="center", color=DEFENSE_COLOR)


# 7. SAVE
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight', facecolor=BG_COLOR)
print(f"Attacking/Defensive Radar Chart saved as {OUTPUT_IMAGE}")
plt.show()