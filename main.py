import pandas as pd
import geopandas as gpd
import os

print("running")
gtfsFolder = r"C:\Users\svenk\Downloads\latesta"
importPolygonFile = r"C:\Users\svenk\Downloads\latesta\cutPolygon.gpkg"
keepIds = {"stop_id":[], "trip_id":[], "route_id":[], "agency_id":[]}
cutCouples = [["stops", "stop_id"],["stop_times","stop_id"],["trips","trip_id"],["routes","route_id"],["agency","agency_id"]]

def CutPointsByGeoPackage(importPolygonFile, gtfsFolder):

    importPolygon = gpd.read_file(importPolygonFile)
    stops = pd.read_csv(gtfsFolder + "/stops.txt", sep=",")
    stops = gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops.stop_lon, stops.stop_lat))
    stops.crs = importPolygon.crs
    stops = gpd.clip(stops, importPolygon)
    stopsIds = stops.stop_id.tolist()
    keepIds["stop_id"] = stopsIds

CutPointsByGeoPackage(importPolygonFile, gtfsFolder)



def CutIdById(inputId, cutId, filename, gtfsFolder):
    df = pd.read_csv(rf"{gtfsFolder}\{filename}", sep=",")
    dfFiltered = df[df[inputId].isin(keepIds[inputId])]
    keepIds[cutId] = dfFiltered[cutId].tolist()

CutIdById("stop_id", "trip_id", "stop_times.txt", gtfsFolder)
CutIdById("trip_id", "route_id", "trips.txt", gtfsFolder)
CutIdById("trip_id", "service_id", "trips.txt", gtfsFolder)
CutIdById("route_id", "agency_id", "routes.txt", gtfsFolder)
print("Route ids:")
df = pd.read_csv(rf"{gtfsFolder}\{'trips.txt'}", sep=",")
for element in keepIds["route_id"]:
    dfFiltered = df[df["route_id"] == element]
    tripIdsList = dfFiltered["trip_id"].tolist()
    for element in tripIdsList:
        if element not in keepIds["trip_id"]:
            keepIds["trip_id"].append(element)
print("Trip ids:")
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

for element in cutCouples:
    print(element)
    df = pd.read_csv(rf"{gtfsFolder}\{element[0]}.txt", sep=",")
    dfFiltered = df[df[element[1]].isin(keepIds[element[1]])]
    dfFiltered.to_csv(rf"{cuttedFolder}\{element[0]}.txt", index=False)

# Add the outside stop ids




print("Done!")