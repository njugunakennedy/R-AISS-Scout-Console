import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from matplotlib.lines import Line2D

# --- CONFIGURATION ---
CSV_FILE = 'data/full_match_data.csv'
OUTPUT_IMAGE = 'output/progressive_pass_lanes.png'
TEAM_NAME = 'Home'  # Change to 'Home' (Lincoln) or 'Away' (Easter)

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows from {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. PRE-PROCESS COORDINATES
# We need to know where the pass landed.
# We assume the "Next Event" marks the reception location.
df['End_X'] = df['X'].shift(-1)
df['End_Y'] = df['Y'].shift(-1)

# 3. FILTER FOR PASSES
# Filter conditions:
# 1. Event is 'Pass' (or 'Cross')
# 2. Team matches target
# 3. Outcome was Successful (Next event is same team)
passes = df[
    (df['Event'].isin(['Pass', 'Cross'])) & 
    (df['Team'] == TEAM_NAME) & 
    (df['Team'].shift(-1) == TEAM_NAME)
].copy()

# Drop incomplete rows
passes = passes.dropna(subset=['End_X', 'End_Y'])

# 4. SEPARATE PROGRESSIVE VS NORMAL
# The generator tags progressive passes in the 'Prog_Metric' column
prog_passes = passes[passes['Prog_Metric'] == 'Prog Pass']
normal_passes = passes[passes['Prog_Metric'] != 'Prog Pass']

print(f"Total Passes: {len(passes)}")
print(f"Progressive Passes: {len(prog_passes)}")

if prog_passes.empty:
    print(f"No progressive passes found for {TEAM_NAME}.")
    exit()

# 5. DRAW PITCH
pitch = VerticalPitch(pitch_type='opta', half=False, pitch_color='#1e293b', line_color='#64748b')
fig, ax = pitch.draw(figsize=(10, 8))

# 6. PLOT NORMAL PASSES (Background)
# Faint lines to show general structure
pitch.lines(
    normal_passes['X'], normal_passes['Y'],
    normal_passes['End_X'], normal_passes['End_Y'],
    ax=ax, color='#475569', alpha=0.1, lw=1, zorder=1
)

# 7. PLOT PROGRESSIVE PASSES (Highlighted)
# Bright Cyan lines with arrows
pitch.arrows(
    prog_passes['X'], prog_passes['Y'],
    prog_passes['End_X'], prog_passes['End_Y'],
    ax=ax, color='#06b6d4', width=3, headwidth=5, headlength=5, alpha=0.9, zorder=2
)

# Scatter points at the start of progressive passes
pitch.scatter(
    prog_passes['X'], prog_passes['Y'],
    ax=ax, color='#06b6d4', edgecolors='white', s=30, zorder=3
)

# 8. ANNOTATE TOP PASSER
# Find the player with the most progressive passes
top_passer = prog_passes['Player'].value_counts().idxmax()
count = prog_passes['Player'].value_counts().max()

# Add a note on the pitch
ax.text(50, 103, f"Most Threatening: {top_passer} ({count})", 
        ha='center', va='center', color='#06b6d4', fontsize=12, fontweight='bold')

# 9. LEGEND & TITLES
legend_elements = [
    Line2D([0], [0], color='#06b6d4', lw=3, label='Progressive Pass'),
    Line2D([0], [0], color='#475569', lw=1, label='Normal Pass')
]

ax.legend(handles=legend_elements, loc='lower right', facecolor='#1e293b', edgecolor='white', labelcolor='white')

team_label = "Lincoln FC" if TEAM_NAME == 'Home' else "Easter FC"
ax.set_title(f"{team_label} - Passing Lanes", fontsize=18, fontweight='bold', color='white', pad=20)
fig.set_facecolor('#1e293b')

# 10. SAVE
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight', facecolor='#1e293b')
print(f"Progressive Pass Map saved as {OUTPUT_IMAGE}")
plt.show()