import streamlit as st
# ✅ Must be FIRST Streamlit command — do NOT put anything before this
st.set_page_config(page_title="F1 Race Simulation", layout="wide")

# Now import everything else
import fastf1
import pandas as pd
import time

# Enable FastF1 cache
fastf1.Cache.enable_cache('f1_cache')

# Load session function — defined AFTER set_page_config
@st.cache_resource
def load_session():
    session = fastf1.get_session(2024, 'Bahrain Grand Prix', 'R')
    session.load()
    return session

# Load with spinner
with st.spinner("🔄 Loading race session..."):
    session = load_session()

laps = session.laps
drivers = sorted(laps['Driver'].unique())
max_lap = int(laps['LapNumber'].max())

# Points system
def get_points(pos):
    point_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}
    return point_map.get(pos, 0)

# Title and setup
st.title("🏎️ Real-Time F1 Race Simulation Dashboard")
st.caption("Simulating 2024 Bahrain GP lap-by-lap (1.5s per lap)")

placeholder = st.empty()

# Lap-by-lap simulation
for lap_number in range(1, max_lap + 1):
    current_lap = laps[laps['LapNumber'] == lap_number].sort_values('Position')
    lap_display = []

    for _, row in current_lap.iterrows():
        driver = row['Driver']
        position = row['Position']
        tyre = row['Compound']
        lap_time = row['LapTime']
        pit_stops = laps[(laps['Driver'] == driver) & (laps['PitOutTime'].notna())].shape[0]

        # Lap time in seconds
        lap_time_sec = round(lap_time / pd.Timedelta(seconds=1), 3) if pd.notna(lap_time) else None

        # Gap to car ahead
        if position == 1:
            gap = 0.000
        else:
            ahead_driver = current_lap[current_lap['Position'] == position - 1]
            if not ahead_driver.empty and pd.notna(row['Time']) and pd.notna(ahead_driver['Time'].values[0]):
                gap = round((row['Time'] - ahead_driver['Time'].values[0]) / pd.Timedelta(seconds=1), 3)
            else:
                gap = None

        lap_display.append({
            'Driver': driver,
            'Lap': lap_number,
            'Position': position,
            'Tyre': tyre,
            'Lap Time (s)': lap_time_sec,
            'Gap to Front (s)': gap,
            'Pit Stops': pit_stops,
            'Points (est.)': get_points(position)
        })

    lap_df = pd.DataFrame(lap_display)
    lap_df = lap_df.sort_values(by='Position')
    placeholder.dataframe(lap_df, use_container_width=True)
    time.sleep(1.5)

st.success("🏁 Race Simulation Complete!")
