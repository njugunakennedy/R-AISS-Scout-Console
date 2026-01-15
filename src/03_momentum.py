import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from scipy.ndimage import gaussian_filter1d

# --- CONFIGURATION ---
CSV_FILE = 'data/full_match_data.csv'   # Updated to match our data file
OUTPUT_IMAGE = 'output/momentum_timeline.png'
BALL_IMG = 'ball.png'  # Optional: Place a small png of a ball in the folder

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows.")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. CALCULATE THREAT (Simplified xT)
def calculate_threat(row):
    # In our generated data, BOTH teams attack towards X=100
    # Higher X = Closer to opponent goal = Higher Threat
    x = row['X']
    y = row['Y']
    
    # Base threat: Distance to goal (x^2 for exponential threat)
    dist_x = x / 100.0
    
    # Penalize being on the wing (0 or 100) vs center (50)
    # 1.0 at center, 0.8 at wings
    dist_y = 1 - (abs(y - 50) / 50.0) * 0.2 
    
    threat = (dist_x ** 1.5) * dist_y
    return threat

# Apply threat calculation
df['Threat'] = df.apply(calculate_threat, axis=1)

# 3. AGGREGATE MOMENTUM PER MINUTE
# Create a full timeline
minutes = pd.DataFrame({'Mins': range(0, df['Mins'].max() + 2)})

# Sum threat per minute for Home (Lincoln FC)
home_threat = df[df['Team'] == 'Home'].groupby('Mins')['Threat'].sum().reset_index()
home_threat = minutes.merge(home_threat, on='Mins', how='left').fillna(0)

# Sum threat per minute for Away (Eastern FC)
away_threat = df[df['Team'] == 'Away'].groupby('Mins')['Threat'].sum().reset_index()
away_threat = minutes.merge(away_threat, on='Mins', how='left').fillna(0)

# 4. SMOOTHING (Gaussian Filter)
# Sigma=1.5 gives a nice "wavy" feel without hiding the spikes
sigma = 1.5 
home_smooth = gaussian_filter1d(home_threat['Threat'], sigma=sigma)
away_smooth = gaussian_filter1d(away_threat['Threat'], sigma=sigma)

# Calculate Net Momentum (Home - Away)
momentum = home_smooth - away_smooth

# 5. PLOT
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')

# Define Colors
HOME_COLOR = '#3b82f6' # Blue (Lincoln)
AWAY_COLOR = '#ef4444' # Red (Eastern)

# Fill areas
# Home Dominance (Positive Momentum)
ax.fill_between(
    minutes['Mins'], 0, momentum,
    where=(momentum >= 0),
    interpolate=True, color=HOME_COLOR, alpha=0.7, label='Lincoln FC'
)

# Away Dominance (Negative Momentum)
ax.fill_between(
    minutes['Mins'], 0, momentum,
    where=(momentum < 0),
    interpolate=True, color=AWAY_COLOR, alpha=0.7, label='Easter FC'
)

# 6. ADD GOALS
# Logic: Find rows where Event is Shot AND Qualifier is Goal
goals = df[(df['Event'] == 'Shot') & (df['Qualifier'] == 'Goal')].copy()

for _, row in goals.iterrows():
    minute = row['Mins']
    # Place marker on the dominant side
    y_pos = max(momentum) * 0.8 if row['Team'] == 'Home' else min(momentum) * 0.8
    
    # Draw Dashed Line
    ax.plot([minute, minute], [0, y_pos], color='grey', linestyle='--', alpha=0.5)
    
    # Draw Ball or Marker
    try:
        img = plt.imread(BALL_IMG)
        imagebox = OffsetImage(img, zoom=0.03) 
        ab = AnnotationBbox(imagebox, (minute, y_pos), frameon=False)
        ax.add_artist(ab)
    except (FileNotFoundError, TypeError):
        # Fallback circle if image missing
        color = HOME_COLOR if row['Team'] == 'Home' else AWAY_COLOR
        ax.scatter(minute, y_pos, s=300, color='white', edgecolor=color, linewidth=2, zorder=5)
        ax.text(minute, y_pos, "GOAL", ha='center', va='center', fontsize=7, fontweight='bold', color='black')

    # Add Minute Text
    offset = max(momentum) * 0.1 if row['Team'] == 'Home' else -max(momentum) * 0.1
    ax.text(minute, y_pos + offset, f"{minute}'", ha='center', color='#333', fontsize=10, fontweight='bold')


# 7. STYLING
ax.axhline(0, color='black', linewidth=1, alpha=0.2) # Center line
ax.set_title("Lincoln FC vs Easter FC - Match Momentum", fontsize=18, fontweight='bold', pad=20, color='#1e293b')
ax.set_xlabel("Minute", fontsize=10, fontweight='bold', color='#555')
ax.set_ylabel("Threat Intensity (xT)", fontsize=10, fontweight='bold', color='#555')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_yticks([]) # Hide abstract Y numbers
ax.set_xlim(0, max(minutes['Mins']))

# Custom Legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color=HOME_COLOR, lw=4, label='Lincoln FC'),
    Line2D([0], [0], color=AWAY_COLOR, lw=4, label='Easter FC')
]
ax.legend(handles=legend_elements, loc='upper left', frameon=False)

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
print(f"Momentum chart saved as {OUTPUT_IMAGE}")
plt.show()