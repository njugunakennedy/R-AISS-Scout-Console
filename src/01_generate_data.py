import pandas as pd
import random
import os

# --- CONFIGURATION ---
MATCH_ID = "match_1768464395999"
TARGET_ROWS = 350  # The script will naturally exceed this for a full half
HALF_LENGTH_MINS = 45

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Players list
PLAYERS = {
    'Home': [f'H{i}' for i in range(1, 12)], # H1=GK, H2-H11 Outfield
    'Away': [f'A{i}' for i in range(1, 12)]
}

# --- HELPER FUNCTIONS ---

def get_screen_coords(team, x, y):
    """
    Calculates Screen coordinates based on team.
    Home: 0->100 is Left->Right.
    Away: 0->100 is Right->Left (so we invert for screen).
    """
    if team == 'Home':
        return round(x, 1), round(y, 1)
    else:
        return round(100 - x, 1), round(100 - y, 1)

def check_progression(event_type, start_x, end_x, start_y, end_y):
    """
    Determines if an event is progressive.
    Criteria: Moves ball significantly closer to goal (X increases).
    """
    dist_forward = end_x - start_x
    
    # 1. Progressive Pass: Moves ball 10m+ forward (if not in def third) or into box
    if event_type == 'Pass':
        if start_x > 40 and dist_forward >= 10: return "Prog Pass"
        if start_x < 40 and dist_forward >= 15: return "Prog Pass" # stricter in own half
        if start_x < 83 and end_x >= 83 and end_y > 21 and end_y < 79: return "Prog Pass" # Into box
        
    # 2. Progressive Carry (Dribble)
    if event_type == 'Dribble':
        if dist_forward >= 10: return "Prog Carry"
        if start_x < 50 and end_x > 50: return "Prog Carry" # Crossing midfield
        
    # 3. Progressive Reception (calculated relative to previous pass start)
    # Note: This is usually handled in the main loop relative to the pass origin
    return ""

# --- SIMULATION ENGINE ---

data_rows = []
mins = 0
secs = 0
possession_team = 'Home'
# Start at center spot
curr_x, curr_y = 50.0, 50.0 

while mins < HALF_LENGTH_MINS:
    
    # --- 1. DETERMINE ACTOR ---
    # Randomly select a player from the possession team
    # (Bias towards midfielders/attackers for events)
    player_pool = PLAYERS[possession_team]
    # Simple logic: GK (idx 0) less likely to have ball high up pitch
    if curr_x > 30: 
        actor = random.choice(player_pool[1:]) 
    else:
        actor = random.choice(player_pool)

    # --- 2. DETERMINE NEXT ACTION ---
    # Weights change based on pitch location
    if curr_x > 80: # Final third
        action = random.choices(['Pass', 'Dribble', 'Cross', 'Shot'], weights=[40, 30, 15, 15])[0]
    else: # Midfield/Defense
        action = random.choices(['Pass', 'Dribble'], weights=[80, 20])[0]

    # --- 3. EXECUTE ACTION ---
    
    # Default values
    qualifier = ""
    prog_metric = ""
    event_secs = random.randint(1, 4) # Time taken for event
    
    # Calculate End Coordinates (Destination)
    # Tendency to move forward (X increases) but with variance
    dx = random.randint(-5, 20) 
    dy = random.randint(-25, 25)
    
    dest_x = max(0, min(100, curr_x + dx))
    dest_y = max(0, min(100, curr_y + dy))
    
    # -- A. DRIBBLE --
    if action == 'Dribble':
        prog_metric = check_progression('Dribble', curr_x, dest_x, curr_y, dest_y)
        
        # Log Dribble
        sx, sy = get_screen_coords(possession_team, curr_x, curr_y)
        data_rows.append([MATCH_ID, 1, possession_team, actor, 'Dribble', '', prog_metric, mins, secs, round(curr_x,1), round(curr_y,1), sx, sy])
        
        # Update state
        curr_x, curr_y = dest_x, dest_y
        secs += event_secs

    # -- B. PASS --
    elif action == 'Pass':
        # Determine success chance (lower if long pass)
        pass_dist = ((dest_x - curr_x)**2 + (dest_y - curr_y)**2)**0.5
        success_chance = 0.90 if pass_dist < 15 else 0.70
        is_success = random.random() < success_chance
        
        prog_metric = check_progression('Pass', curr_x, dest_x, curr_y, dest_y)
        
        # Log Pass
        sx, sy = get_screen_coords(possession_team, curr_x, curr_y)
        data_rows.append([MATCH_ID, 1, possession_team, actor, 'Pass', '', prog_metric, mins, secs, round(curr_x,1), round(curr_y,1), sx, sy])
        
        secs += 2 # Flight time
        
        if is_success:
            # -- C. RECEPTION (The "Prog Reception" Logic) --
            receiver = random.choice([p for p in PLAYERS[possession_team] if p != actor])
            
            # Check if it's a Progressive Reception
            # (If the pass was progressive, the reception likely is too, or if received in dangerous area)
            rec_metric = ""
            if prog_metric == "Prog Pass" or (dest_x > 70 and pass_dist > 10):
                rec_metric = "Prog Reception"
            
            # Log Reception
            sx_r, sy_r = get_screen_coords(possession_team, dest_x, dest_y)
            data_rows.append([MATCH_ID, 1, possession_team, receiver, 'Reception', '', rec_metric, mins, secs, round(dest_x,1), round(dest_y,1), sx_r, sy_r])
            
            curr_x, curr_y = dest_x, dest_y
            secs += 1
            
        else:
            # -- D. TURNOVER (Interception/Tackle) --
            opponent_team = 'Away' if possession_team == 'Home' else 'Home'
            opp_player = random.choice(PLAYERS[opponent_team])
            
            # Log Interception for opponent
            sx_opp, sy_opp = get_screen_coords(opponent_team, dest_x, dest_y) # Opponent perspective
            
            # Note: For the opponent, the ball is at "dest_x" of the attacker.
            # But we must convert Attacker's X to Defender's X (100 - x) for the row data
            # Logic: If Home is at X=80, Away is at X=20.
            def_x = 100 - dest_x
            def_y = 100 - dest_y
            
            data_rows.append([MATCH_ID, 1, opponent_team, opp_player, 'Interception', '', '', mins, secs, round(def_x,1), round(def_y,1), sx_opp, sy_opp])
            
            # Switch Possession
            possession_team = opponent_team
            curr_x, curr_y = def_x, def_y
            secs += 2

    # -- E. CROSS --
    elif action == 'Cross':
        # Move to wing first
        curr_y = 5 if random.random() < 0.5 else 95
        dest_x = 95
        dest_y = 50
        
        sx, sy = get_screen_coords(possession_team, curr_x, curr_y)
        data_rows.append([MATCH_ID, 1, possession_team, actor, 'Cross', '', '', mins, secs, round(curr_x,1), round(curr_y,1), sx, sy])
        
        # 50/50 Outcome
        if random.random() < 0.5:
             # Connected header?
             secs += 2
             action = 'Shot' # Lead immediately to shot
             curr_x, curr_y = dest_x, dest_y
        else:
             # Cleared
             secs += 3
             possession_team = 'Away' if possession_team == 'Home' else 'Home'
             curr_x, curr_y = 15, 50 # Box clearance area

    # -- F. SHOT --
    elif action == 'Shot':
        outcome = random.choices(['Goal', 'Saved', 'Off Target', 'Blocked'], weights=[10, 35, 35, 20])[0]
        qualifier = outcome
        
        sx, sy = get_screen_coords(possession_team, curr_x, curr_y)
        data_rows.append([MATCH_ID, 1, possession_team, actor, 'Shot', qualifier, '', mins, secs, round(curr_x,1), round(curr_y,1), sx, sy])
        
        # Reset after shot
        secs += 15 # Celebration / Goal kick setup
        possession_team = 'Away' if possession_team == 'Home' else 'Home'
        if outcome == 'Goal':
            curr_x, curr_y = 50, 50
        else:
            curr_x, curr_y = 5, 50

    # --- TIME MANAGEMENT ---
    if secs >= 60:
        mins += 1
        secs -= 60

# --- EXPORT ---
df = pd.DataFrame(data_rows, columns=[
    'MatchID', 'Period', 'Team', 'Player', 'Event', 'Qualifier', 
    'Prog_Metric', 'Mins', 'Secs', 'X', 'Y', 'ScreenX', 'ScreenY'
])

# Save to CSV
filename = 'data/full_match_data.csv'
df.to_csv(filename, index=False)

print(f"Successfully generated {len(df)} rows of match data.")
print(f"Preview of first 10 rows:")
print(df.head(10).to_string())
print(f"\nData saved to: {filename}")
