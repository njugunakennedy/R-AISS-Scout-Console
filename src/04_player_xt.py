import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURATION ---
CSV_FILE = 'full_match_data.csv'  # Linked to your generated data
OUTPUT_IMAGE = 'xt_stacked_leaderboard.png'
TEAM_NAME = 'Home'  # Change to 'Away' to see the other team

# 1. LOAD DATA
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded {len(df)} rows.")
except FileNotFoundError:
    print(f"Error: Could not find {CSV_FILE}. Run the generator first.")
    exit()

# 2. DEFINE THREAT FUNCTION (Simplified xT)
def get_threat_value(x, y):
    # In our generated data, X is ALWAYS 0-100 towards the opponent goal.
    # We do not need to flip for Away team here.
    
    # 1. Distance Threat (Closer to goal = Higher value)
    x_factor = (x / 100.0) ** 2  # Squaring rewards the final third heavily
    
    # 2. Centrality Threat (Central areas are better than wings)
    # y=50 is center. 
    y_dist_from_center = abs(y - 50)
    y_factor = 1 - (y_dist_from_center / 50) * 0.3
    
    return x_factor * y_factor

# 3. CALCULATE xT PER PLAYER
# Structure: { 'PlayerName': {'Pass': 0.0, 'Carry': 0.0} }
player_scores = {}

# We iterate through the dataframe to look at "Action Start" -> "Action End"
for i in range(len(df) - 1):
    curr_event = df.iloc[i]
    next_event = df.iloc[i+1]
    
    # Filter 1: Must be the team we are analyzing
    if curr_event['Team'] != TEAM_NAME:
        continue
    
    # Filter 2: The next event must belong to the SAME team (successful action)
    # and be in the same period (don't calculate xT across halftime)
    if next_event['Team'] == TEAM_NAME and curr_event['Period'] == next_event['Period']:
        
        start_threat = get_threat_value(curr_event['X'], curr_event['Y'])
        end_threat = get_threat_value(next_event['X'], next_event['Y'])
        
        xt_added = end_threat - start_threat
        
        # We only credit positive progression
        if xt_added > 0:
            p = curr_event['Player']
            if p not in player_scores:
                player_scores[p] = {'Pass': 0.0, 'Carry': 0.0}
            
            # Categorize the action
            if curr_event['Event'] in ['Pass', 'Cross']:
                player_scores[p]['Pass'] += xt_added
                
            elif curr_event['Event'] in ['Dribble']:
                player_scores[p]['Carry'] += xt_added

# 4. PREPARE DATAFRAME
data = []
for player, scores in player_scores.items():
    data.append({
        'Player': player,
        'Pass xT': scores['Pass'],
        'Carry xT': scores['Carry'],
        'Total xT': scores['Pass'] + scores['Carry']
    })

leaderboard = pd.DataFrame(data)

if leaderboard.empty:
    print(f"No positive xT data found for {TEAM_NAME}.")
    exit()

# Sort by Total xT (Ascending for horizontal bar chart)
leaderboard = leaderboard.sort_values('Total xT', ascending=True)

# 5. PLOT STACKED BAR CHART
fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')

# Plot 'Pass' first
p1 = ax.barh(leaderboard['Player'], leaderboard['Pass xT'], color='#3b82f6', label='Passing xT')

# Plot 'Carry' on top (using 'left' parameter to stack)
p2 = ax.barh(leaderboard['Player'], leaderboard['Carry xT'], left=leaderboard['Pass xT'], color='#f59e0b', label='Carrying xT')

# 6. STYLING & LABELS
team_label = "Lincoln FC" if TEAM_NAME == 'Home' else "Easter FC"
ax.set_title(f'Expected Threat (xT) Leaders - {team_label}', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Total xT Added', fontsize=10, fontweight='bold', color='#555')

# Add Total Value Labels at the end of each bar
for i, total in enumerate(leaderboard['Total xT']):
    ax.text(total + 0.01, i, f"{total:.2f}", va='center', fontweight='bold', fontsize=9, color='#333')

# Legend
ax.legend(loc='lower right', frameon=True)

# Grid and Spines
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT_IMAGE, dpi=300)
print(f"Stacked xT Chart saved as {OUTPUT_IMAGE}")
plt.show()