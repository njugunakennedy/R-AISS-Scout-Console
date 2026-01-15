import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from matplotlib.lines import Line2D

# --- CONFIGURATION ---
CSV_FILE = 'full_match_data.csv'  # Matches the generator output
OUTPUT_IMAGE = 'carry_lanes_map.png'
TEAM_NAME = 'Home'  # Change to 'Home' (Lincoln) or 'Away' (Easter)

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows from {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. IDENTIFY CARRIES
# In our generated data, a "Dribble" event records the START location.
# The END location is where the NEXT event (Pass/Shot) happens.
df['End_X'] = df['X'].shift(-1)
df['End_Y'] = df['Y'].shift(-1)
df['Next_Team'] = df['Team'].shift(-1)

# Filter for Valid Carries:
# 1. Event must be 'Dribble'
# 2. Team must match target
# 3. Next event must be by the SAME team (possession kept)
carries = df[
    (df['Event'] == 'Dribble') & 
    (df['Team'] == TEAM_NAME) & 
    (df['Next_Team'] == TEAM_NAME)
].copy()

# Drop the last row if it was a dribble (since it has no end coordinates)
carries = carries.dropna(subset=['End_X', 'End_Y'])

# Calculate Distance (to find the best ones)
carries['Dist'] = ((carries['End_X'] - carries['X'])**2 + (carries['End_Y'] - carries['Y'])**2)**0.5

# Filter out tiny adjustments (< 3 meters roughly)
carries = carries[carries['Dist'] > 3]

if carries.empty:
    print(f"No valid carry data found for {TEAM_NAME}.")
    exit()

# 3. SEPARATE TYPES
# The generator puts "Prog Carry" in the Prog_Metric column
prog_carries = carries[carries['Prog_Metric'] == 'Prog Carry']
normal_carries = carries[carries['Prog_Metric'] != 'Prog Carry']

print(f"Found {len(carries)} carries ({len(prog_carries)} Progressive).")

# 4. DRAW PITCH (Dark Theme)
pitch = VerticalPitch(pitch_type='opta', half=False, pitch_color='#1e293b', line_color='#64748b')
fig, ax = pitch.draw(figsize=(10, 8))

# 5. PLOT NORMAL CARRIES (Blue Lines)
pitch.lines(
    carries['X'], carries['Y'],
    carries['End_X'], carries['End_Y'],
    ax=ax, color='#3b82f6', alpha=0.15, lw=3, label='Normal Carry', zorder=1
)

# 6. PLOT PROGRESSIVE CARRIES (Gold Arrows)
# We use arrows to highlight the driving force
pitch.arrows(
    prog_carries['X'], prog_carries['Y'],
    prog_carries['End_X'], prog_carries['End_Y'],
    ax=ax, color='#f59e0b', width=4, headwidth=6, headlength=5, alpha=0.9, label='Progressive Carry', zorder=2
)

# 7. ADD LABELS
# Annotate the Top 3 Longest Progressive Carries
for _, row in prog_carries.nlargest(3, 'Dist').iterrows():
    pitch.annotate(
        row['Player'], 
        xy=(row['End_X'], row['End_Y']), 
        ax=ax, color='white', fontsize=9, fontweight='bold', ha='center', va='bottom'
    )

# 8. LEGEND & TITLE
legend_elements = [
    Line2D([0], [0], color='#f59e0b', lw=4, label='Progressive Carry'),
    Line2D([0], [0], color='#3b82f6', lw=3, alpha=0.5, label='Normal Carry')
]
ax.legend(handles=legend_elements, loc='lower right', facecolor='#1e293b', edgecolor='white', labelcolor='white')

team_label = "Lincoln FC" if TEAM_NAME == 'Home' else "Easter FC"
ax.set_title(f"{team_label} - Carry Map", fontsize=18, fontweight='bold', color='white', pad=20)
fig.set_facecolor('#1e293b')

# 9. SAVE
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight', facecolor='#1e293b')
print(f"Carry map saved as {OUTPUT_IMAGE}")
plt.show()