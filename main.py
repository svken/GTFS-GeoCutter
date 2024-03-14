import pandas as pd
import geopandas as gpd
import os
import math

gtfsFolder = r"C:\Users\sven\Downloads\latest"
importPolygonFile = r"C:\Users\sven\Downloads\latest\cutPolygon.gpkg"
keepIds = {"stop_id":[], "trip_id":[], "route_id":[], "agency_id":[]}
cutCouples = [["stops", "stop_id"],["stop_times","stop_id"],["trips","trip_id"],["routes","route_id"],["agency","agency_id"]]
print("Start!")

# Function to cut the GTFS files by the import polygon
def CutPointsByGeoPackage(importPolygonFile, gtfsFolder):

    importPolygon = gpd.read_file(importPolygonFile)
    stops = pd.read_csv(gtfsFolder + "/stops.txt", sep=",")
    stops = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat))
    stops.crs = importPolygon.crs
    stops = gpd.clip(stops, importPolygon)
    stopsIds = stops.stop_id.tolist()
    stopsParents = stops.parent_station.tolist()
    keepIds["stop_id"] = stopsIds
    keepIds["stop_id"].extend(stopsParents)

CutPointsByGeoPackage(importPolygonFile, gtfsFolder)

def CutIdById(inputId, cutId, filename, gtfsFolder):
    df = pd.read_csv(rf"{gtfsFolder}\{filename}", sep=",")
    dfFiltered = df[df[inputId].isin(keepIds[inputId])]
    keepIds[cutId] = dfFiltered[cutId].tolist()

CutIdById("stop_id", "trip_id", "stop_times.txt", gtfsFolder)
CutIdById("trip_id", "route_id", "trips.txt", gtfsFolder)
CutIdById("trip_id", "service_id", "trips.txt", gtfsFolder)
CutIdById("route_id", "agency_id", "routes.txt", gtfsFolder)
df = pd.read_csv(rf"{gtfsFolder}\{'trips.txt'}", sep=",")
for element in keepIds["route_id"]:
    dfFiltered = df[df["route_id"] == element]
    tripIdsList = dfFiltered["trip_id"].tolist()
    for element in tripIdsList:
        if element not in keepIds["trip_id"]:
            keepIds["trip_id"].append(element)

df = pd.read_csv(rf"{gtfsFolder}\{'stop_times.txt'}", sep=",")
for element in keepIds["trip_id"]:
    dfFiltered = df[df["trip_id"] == element]
    tripIdsList = dfFiltered["stop_id"].tolist()
    keepIds["stop_id"].extend(tripIdsList)

keepIds["stop_id"] = list(set(keepIds["stop_id"]))

CutIdById("stop_id", "trip_id", "stop_times.txt", gtfsFolder)
CutIdById("trip_id", "route_id", "trips.txt", gtfsFolder)
CutIdById("trip_id", "service_id", "trips.txt", gtfsFolder)
CutIdById("route_id", "agency_id", "routes.txt", gtfsFolder)

cuttedFolder = gtfsFolder + "\cutted"
os.makedirs(cuttedFolder, exist_ok=True)

keepIds["stop_id"] =  [x for x in keepIds["stop_id"] if not math.isnan(x)]

# Add Parents from routed Stations to Stop Ids
stopsFile = pd.read_csv(rf"{gtfsFolder}\{'stops.txt'}", sep=",")
for element in keepIds["stop_id"]:
    stop = stopsFile[stopsFile["stop_id"] == element]
    try:
        parentStation = list(stop["parent_station"])[0]
    except:
        continue
    if parentStation not in keepIds["stop_id"]:
        keepIds["stop_id"].append(parentStation)


for element in cutCouples:
    print(element)
    df = pd.read_csv(rf"{gtfsFolder}\{element[0]}.txt", sep=",")
    dfFiltered = df[df[element[1]].isin(keepIds[element[1]])]

    if element[0] == "stops":
        dfFiltered['location_type'] = dfFiltered['location_type'].fillna("0").astype(int)
        #dfFiltered['parent_station'] = dfFiltered['parent_station'].fillna(math.nan).astype(int)

        #dfFiltered.loc[dfFiltered['location_type'] == 1, 'parent_station'] = "a"

    if element[0] == "stop_times":
        dfFiltered['pickup_type'] = dfFiltered['pickup_type'].fillna("0").astype(int)    
    dfFiltered.to_csv(rf"{cuttedFolder}\{element[0]}.txt", index=False, sep = ",")

#df.loc[df['location_type'] == 1, 'parent_station'] = pd.NA
#df['parent_station'] = df['parent_station'].fillna("0").astype(int)    
#df.to_csv(f"{gtfsFolder}/cutted/stops.txt", sep = ",", index=False)
#Field parent_station must be empty when location_type is 1.

print("Done!")