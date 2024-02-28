import pandas as pd

path = r"C:\Users\svenk\Downloads\cutted\stops.txt"

# Load the CSV file
df = pd.read_csv(path, sep = ",")

# Delete a specific column, let's say 'column_to_delete'
df = df.drop('parent_station', axis=1)

# Save the DataFrame back to a CSV file
df.to_csv(path, index=False)