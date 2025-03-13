import pandas as pd
import geopandas as gpd
import os
import math

""" GTFS-GeoCutter is a Python script designed to extract a subset of a GTFS (General Transit Feed Specification) 
dataset based on a geographic boundary.It preserves the relational integrity of the GTFS data while filtering 
to include only transit information relevant to a specific geographic area."""

gtfsFolder = r"C:\Users\svenk\Downloads\latesta"
importPolygonFile = r"C:\Users\svenk\Downloads\latesta\cutPolygon.gpkg"
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
    keepIds["stop_id"] = stopsIds

    # extend the keep ids with the parent stations
    stopsParents = stops.parent_station.tolist()
    keepIds["stop_id"].extend(stopsParents)

def CutIdById(inputId, cutId, filename, gtfsFolder):
    df = pd.read_csv(rf"{gtfsFolder}\{filename}", sep=",")
    dfFiltered = df[df[inputId].isin(keepIds[inputId])]
    keepIds[cutId] = dfFiltered[cutId].tolist()

CutPointsByGeoPackage(importPolygonFile, gtfsFolder)

CutIdById("stop_id", "trip_id", "stop_times.txt", gtfsFolder)
CutIdById("trip_id", "route_id", "trips.txt", gtfsFolder)
CutIdById("trip_id", "service_id", "trips.txt", gtfsFolder)
CutIdById("route_id", "agency_id", "routes.txt", gtfsFolder)

# Add Stops along the pt routes that are not in the import polygon
TripsData = pd.read_csv(rf"{gtfsFolder}\{'trips.txt'}", sep=",")
for routeId in keepIds["route_id"]:
    dfFiltered = TripsData[TripsData["route_id"] == routeId]
    tripIdsList = dfFiltered["trip_id"].tolist()
    for tripId in tripIdsList:
        if tripId not in keepIds["trip_id"]:
            keepIds["trip_id"].append(tripId)

StopTimesData = pd.read_csv(rf"{gtfsFolder}\{'stop_times.txt'}", sep=",")
for tripId in keepIds["trip_id"]:
    dfFiltered = StopTimesData[StopTimesData["trip_id"] == tripId]
    tripIdsList = dfFiltered["stop_id"].tolist()
    keepIds["stop_id"].extend(tripIdsList)

# Remove Duplicates from the stop_ids
keepIds["stop_id"] = list(set(keepIds["stop_id"]))

# Create the export folder
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
    if element[0] == "stop_times":
        element = ["stop_times", "trip_id"]
    print(element)
    df = pd.read_csv(rf"{gtfsFolder}\{element[0]}.txt", sep=",")
    dfFiltered = df[df[element[1]].isin(keepIds[element[1]])]

    if element[0] == "stops":
        dfFiltered['location_type'] = dfFiltered['location_type'].fillna("0").astype(int)

    if element[0] == "stop_times":
        dfFiltered['pickup_type'] = dfFiltered['pickup_type'].fillna("0").astype(int) 

    dfFiltered.to_csv(rf"{cuttedFolder}\{element[0]}.txt", index=False, sep = ",")

print("Done!")