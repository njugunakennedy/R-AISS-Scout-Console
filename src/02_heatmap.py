import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from mplsoccer import Pitch

# --- CONFIGURATION ---
CSV_FILE = 'data/full_match_data.csv' 
OUTPUT_IMAGE = 'output/heatmap_lincoln_vs_eastern.png'
TEAM_NAME = 'Home'  # Select which team's data to display

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Successfully loaded {len(df)} rows from {CSV_FILE}")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Make sure the data file exists.")
    exit()

# 2. DATA PREPROCESSING
# Filter for the specific team
df_filtered = df[df['Team'] == TEAM_NAME].copy()

# Ensure X and Y are numbers
df_filtered['X'] = pd.to_numeric(df_filtered['X'], errors='coerce')
df_filtered['Y'] = pd.to_numeric(df_filtered['Y'], errors='coerce')

# Drop missing values
df_filtered = df_filtered.dropna(subset=['X', 'Y'])

print(f"Plotting heatmap for {TEAM_NAME} ({len(df_filtered)} events)...")

# 3. SETUP THE PITCH
pitch = Pitch(pitch_type='opta', pitch_color='white', line_color='black', line_zorder=2)
fig, ax = pitch.draw(figsize=(10, 7))

# 4. PLOT THE HEATMAP
# Choose color based on team (Optional: customize as needed)
cmap_name = 'Reds' if TEAM_NAME == 'Home' else 'Blues'

kde = pitch.kdeplot(
    df_filtered.X,
    df_filtered.Y,
    fill=True,
    thresh=0.05,    
    n_levels=100,   
    cmap=cmap_name,
    alpha=0.8,      
    ax=ax
)

# 5. ADD INTENSITY BAR
norm = mcolors.Normalize(vmin=0, vmax=1)
sm = cm.ScalarMappable(cmap=cmap_name, norm=norm)
sm.set_array([]) 

cbar = plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Action Density', fontsize=12)

# 6. TITLES AND LABELS
# --- UPDATED TITLE HERE ---
ax.set_title("Lincoln FC vs Easter FC Heatmap", fontsize=18, fontweight='bold', pad=20)

# 7. SAVE & SHOW
plt.savefig(OUTPUT_IMAGE, dpi=300, bbox_inches='tight')
print(f"Heatmap saved as {OUTPUT_IMAGE}")
plt.show()