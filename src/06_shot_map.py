import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from matplotlib.lines import Line2D

# --- CONFIGURATION ---
CSV_FILE = 'data/full_match_data.csv'  # Linked to the generator output
OUTPUT_IMAGE = 'output/shot_map_outcomes.png'
TEAM_NAME = 'Home'             # Change to 'Home' or 'Away'

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows from {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. FILTER FOR SHOTS
# In the new generator, all shots are labeled "Shot" in the Event column
df_shots = df[df['Event'] == 'Shot'].copy()

# Filter for the specific team
df_shots = df_shots[df_shots['Team'] == TEAM_NAME]

if df_shots.empty:
    print(f"No shots found for {TEAM_NAME} team.")
    exit()

# 3. SETUP THE PITCH
# half=True zooms in on the attacking half (better for shot maps)
pitch = VerticalPitch(pitch_type='opta', half=True, pitch_color='#f5f5f5', 
                      line_color='#d3d3d3', line_zorder=1)
fig, ax = pitch.draw(figsize=(10, 8))

# 4. PLOT SHOTS BY OUTCOME
# We iterate through the shots and choose markers based on the 'Qualifier'
for _, row in df_shots.iterrows():
    
    # CASE 1: GOAL
    if row['Qualifier'] == 'Goal':
        pitch.scatter(
            x=row['X'], y=row['Y'], ax=ax, 
            s=600, marker='*', color='gold', edgecolor='black', zorder=3, label='Goal'
        )
    
    # CASE 2: SAVED
    elif row['Qualifier'] == 'Saved':
        pitch.scatter(
            x=row['X'], y=row['Y'], ax=ax, 
            s=300, marker='o', color='#3b82f6', edgecolor='white', alpha=0.9, zorder=2
        )

    # CASE 3: OFF TARGET
    elif row['Qualifier'] == 'Off Target':
        pitch.scatter(
            x=row['X'], y=row['Y'], ax=ax, 
            s=300, marker='x', color='#ef4444', linewidth=3, alpha=0.8, zorder=2
        )
        
    # CASE 4: BLOCKED
    elif row['Qualifier'] == 'Blocked':
        pitch.scatter(
            x=row['X'], y=row['Y'], ax=ax, 
            s=300, marker='s', color='#64748b', edgecolor='white', alpha=0.8, zorder=2
        )

# 5. LEGEND & STATS
# Custom legend
legend_elements = [
    Line2D([0], [0], marker='*', color='w', label='Goal', markerfacecolor='gold', markersize=18, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Saved', markerfacecolor='#3b82f6', markersize=12, markeredgecolor='white'),
    Line2D([0], [0], marker='x', color='w', label='Off Target', markeredgecolor='#ef4444', markersize=12, markeredgewidth=2),
    Line2D([0], [0], marker='s', color='w', label='Blocked', markerfacecolor='#64748b', markersize=12, markeredgecolor='white'),
]

ax.legend(handles=legend_elements, loc='lower center', ncol=4, fontsize=10, frameon=True, facecolor='white', framealpha=0.9)

# Summary Title
total_shots = len(df_shots)
goals = len(df_shots[df_shots['Qualifier'] == 'Goal'])
team_label = "Lincoln FC" if TEAM_NAME == 'Home' else "Easter FC"

ax.set_title(f"{team_label} - Shot Map\n{goals} Goals / {total_shots} Shots", fontsize=18, fontweight='bold', color='#1e293b', pad=20)

# 6. SAVE
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Shot Map saved as {OUTPUT_IMAGE}")
plt.show()