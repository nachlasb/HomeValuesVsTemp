# Import modules
import csv
from datetime import datetime

# Instantiate variables
output_headers = ['dt', 'State', 'Average Temperature']
us_temps = []

# Access source .csv data
with open('GlobalLandTemperaturesByState.csv') as global_temp_source:
    global_temps_reader = csv.DictReader(global_temp_source)    # Creates reader object
    for row in global_temps_reader:                             # Iterates through row to parse global data and appends only US States
        if row['Country'] == 'United States':
            dt = datetime.strptime(row['dt'], '%Y-%m-%d')       # Convert dt to datetime value
            if dt >= datetime(1999, 12, 31):                    # Matches ZHVI dataset cutoff 
                us_temps.append({'dt': row['dt'], 'State': row['State'], 'Average Temperature': row['AverageTemperature']})
                       # Results in us_temps, a list, populated with datecode, State, and Average Temp values for US

# Creates new US_state_temps.csv output file
with open('US_state_temps.csv', 'w', newline='') as output_file:
    writer = csv.writer(output_file)                             # Creates writer object
    writer.writerow(output_headers)                              # Writes column headers
    for row in us_temps:                                         # Iterates through list to write entry line-by-line
        dt = datetime.strptime(row['dt'], '%Y-%m-%d')
        writer.writerow([row['dt'], row['State'], row['Average Temperature']])

# Instantiate dictionaries
temps = {}
values = {}

# Read the data from US_state_temps.csv and create dictionary in format {dt: [(State, avg_temp)]} for each row
with open('US_state_temps.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        dt, state, avg_temp = row
        if dt not in temps:
            temps[dt] = []
        temps[dt].append((state, avg_temp))

# Create dictionary of home values data
# Call reader to read home values data from ZHVI.csv    
# Iterate through rows of home values and create new dictionary with {dt: {State1: avg_value, State2: avg_value..}}
with open('ZHVI.csv', 'r') as home_values_data:
    home_values_reader = csv.reader(home_values_data)
    header = next(home_values_reader)
    for row in home_values_reader:
        dt, *avg_home_values = row
        avg_home_values = [0 if value == '' else int(value) for value in avg_home_values]
        values[dt] = dict(zip(header[1:], avg_home_values))
        

# Merge the temps and values dictionaries on matching date values
# Creates list of combinations and only appends merged list if combination is non-existent
merged = []
combinations = set()
for temp_dt in temps:
    if temp_dt in values:
        for state, avg_temp in temps[temp_dt]:
            combination = (temp_dt, state, avg_temp)
            if combination not in combinations:
                merged.append((temp_dt, state, avg_temp, values[temp_dt].get(state, 0)))
                combinations.add(combination)

# Iterates through merged list and writes data into output CSV line-by-line
with open('merged_output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['dt', 'State', 'Average Temperature', 'Average Value'])
    for row in merged:
        writer.writerow(row)

# Import modules
import plotly.express as px
import pandas as pd

# Load the cleaned data into a pandas dataframe
df = pd.read_csv("merged_output.csv")

# Convert the dt column to a datetime type
df['dt'] = pd.to_datetime(df['dt'])

# Sort the dataframe by the State column to display alphabetized states
df = df.sort_values(by='State')

# Create the 3D chloropleth using plotly
fig = px.scatter_3d(df, x='State', y='dt', z='Average Value', color='Average Temperature', size_max=10, opacity=0.7)

# Adjust the scale of the axes 
fig.update_layout(scene = dict(aspectmode = "manual", aspectratio = dict(x=2, y=1, z=1)))

# Add title to figure 
fig.update_layout(title={
        'text': "Average US Home Prices and Surface Temperatures Over Time",
        'font': {'size': 28},
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'})

# Write the figure to an HTML file and display in console
fig.write_html("Average US Home Prices and Surface Temperatures Over Time.html")
fig.show()
