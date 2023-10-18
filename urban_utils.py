# %%
from ipyleaflet import (
    Map,
    basemap_to_tiles,
    basemaps,
    DrawControl,
    WidgetControl,
    LayersControl,
)
from ipyleaflet import Map, DrawControl, basemap_to_tiles, basemaps, GeoJSON
from ipywidgets import Button, Layout, VBox
import numpy as np
from tqdm.auto import tqdm
import time
import requests
import os
import json
import pandas as pd
import shapely
import fiona
import math
import netCDF4 as nc


# %%
class InteractiveMap:
    # Initialize variables to store coordinates
    aoi_coordinates = []
    aoi_extent_coordinates = []
    aoi_geoms = []
    aoi_shapes = []
    basemap = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)
    combined_rows = []
    geo_em_file_extent_coordinates = []
    geo_em_file_extent_shape = []
    geo_em_file_extent_data = []
    geo_em_file_extent_geoms = []
    isControlAdded = False

    def __init__(self, center=(40.41671327747509, -3.702635610085826), zoom=0):
        self.map = Map(basemap=self.basemap, center=center, zoom=zoom)

        # Create a DrawControl for drawing rectangles
        self.draw_control = DrawControl(
            rectangle={"shapeOptions": {"color": "#f06eaa"}}
        )
        self.map.add_control(self.draw_control)

        # Other controls
        self.layerscontrol = LayersControl(position="bottomright")
        self.map.add_control(self.layerscontrol)

        # Create a custom control for additional functionality
        self.custom_control = CustomControl(self.map)

        # Register the draw event handler
        self.draw_control.on_draw(self.handle_draw)

    def handle_draw(self, target, action, geo_json):
        if action == "created":
            coordinates = geo_json["geometry"]["coordinates"]

            # Calculate in case weird shape
            aoi_lons = np.array(coordinates[0])[:, 0]
            aoi_lats = np.array(coordinates[0])[:, 1]

            aoi_last_coordinates = [
                [
                    [aoi_lons.min(), aoi_lats.min()],
                    [aoi_lons.min(), aoi_lats.max()],
                    [aoi_lons.max(), aoi_lats.max()],
                    [aoi_lons.max(), aoi_lats.min()],
                ]
            ]
            self.aoi_coordinates.append(coordinates)
            self.aoi_extent_coordinates.append(aoi_last_coordinates)
            self.aoi_geoms.append({"coordinates": coordinates, "type": "Polygon"})
            self.aoi_shapes.append(shapely.geometry.shape(self.aoi_geoms[-1]))
            # print("Rectangle coordinates:", coordinates)
            action = "standby"

    def display(self):
        return self.map

    def get_OSM_tileRange(self):
        """
        This function calculates all four corners of the OSM tiles that intersect the input shape
        """

        # Check if there is a shape yet
        if len(self.aoi_coordinates) == 0:
            print("No shape drawn yet.")
        else:
            # Get corners of shape
            (
                c1,
                c2,
                c3,
                c4,
            ) = self.aoi_extent_coordinates[
                -1
            ][-1]

            # Separate corners into lat and lon
            lon_deg_1, lat_deg_1 = c1
            lon_deg_2, lat_deg_2 = c2
            lon_deg_3, lat_deg_3 = c3
            lon_deg_4, lat_deg_4 = c4

            # calculate
            zoom = 15
            n = 2**zoom
            xtile_1 = int(n * ((lon_deg_1 + 180) / 360))
            ytile_1 = int(
                n
                * (
                    1
                    - (
                        np.log(
                            np.tan(np.deg2rad(lat_deg_1))
                            + 1 / np.cos(np.deg2rad(lat_deg_1))
                        )
                        / np.pi
                    )
                )
                / 2
            )
            xtile_2 = int(n * ((lon_deg_2 + 180) / 360))
            ytile_2 = int(
                n
                * (
                    1
                    - (
                        np.log(
                            np.tan(np.deg2rad(lat_deg_2))
                            + 1 / np.cos(np.deg2rad(lat_deg_2))
                        )
                        / np.pi
                    )
                )
                / 2
            )
            xtile_3 = int(n * ((lon_deg_3 + 180) / 360))
            ytile_3 = int(
                n
                * (
                    1
                    - (
                        np.log(
                            np.tan(np.deg2rad(lat_deg_3))
                            + 1 / np.cos(np.deg2rad(lat_deg_3))
                        )
                        / np.pi
                    )
                )
                / 2
            )
            xtile_4 = int(n * ((lon_deg_4 + 180) / 360))
            ytile_4 = int(
                n
                * (
                    1
                    - (
                        np.log(
                            np.tan(np.deg2rad(lat_deg_4))
                            + 1 / np.cos(np.deg2rad(lat_deg_4))
                        )
                        / np.pi
                    )
                )
                / 2
            )

            # print(int(xtile_1), int(ytile_1))
            # print(int(xtile_2), int(ytile_2))
            # print(int(xtile_3), int(ytile_3))
            # print(int(xtile_4), int(ytile_4))

            corner_tiles = np.array(
                [
                    [xtile_1, ytile_1],
                    [xtile_2, ytile_2],
                    [xtile_3, ytile_3],
                    [xtile_4, ytile_4],
                ]
            )

            range_tiles = [
                [min(corner_tiles[:, 0]), min(corner_tiles[:, 1])],
                [max(corner_tiles[:, 0]), max(corner_tiles[:, 1])],
            ]

            return range_tiles

    def download_OSM_buildings(self, show_tiles=False):
        """
        This function downloads the individual tiles that intersect with the selection for a given range of tiles and adds them to the map m.
        """

        # calculate corners numbers of tiles for a given rectangle/shape
        range_tiles = self.get_OSM_tileRange()

        # Check and create directory
        path2save = "OSM_tiles"
        isExist = os.path.exists(path2save)
        if isExist:
            print(f"Tiles will be stored in {path2save}")
        else:
            print(f"Creating directory to store files: {path2save}")
            os.makedirs(path2save)
            print("The new directory is created!")

        # Register files stored
        files_stored = []

        xtile_1 = range_tiles[0][0]
        ytile_1 = range_tiles[0][1]
        xtile_4 = range_tiles[1][0]
        ytile_4 = range_tiles[1][1]

        print("Downloading tiles in area of interest")
        for xtile in tqdm(np.arange(xtile_1, xtile_4 + 1)):
            for ytile in tqdm(np.arange(ytile_1, ytile_4 + 1), leave=False):
                time.sleep(0.1)  # Sleep for 0.1 second
                # url
                url = f"https://data.osmbuildings.org/0.2/anonymous/tile/15/{xtile}/{ytile}.json"

                querystring = {
                    "limit": "2",
                    "divider": "3",
                    "zoom": "6",
                    "lat_ne": "36.5979",
                    "lon_ne": "28.1250",
                    "lat_sw": "34.3071",
                    "lon_sw": "25.3125",
                    "date_end": "last",
                    "quality": "7",
                }
                payload = ""
                headers = {
                    "Referer": "https://weathermap.netatmo.com/",
                    "Authorization": "Bearer 6324808d27fad0061300b3e6|02addc4ef6c48fb26a065faa6c788acf",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                }

                response = requests.request(
                    "GET", url, data=payload, params=querystring, headers=headers
                )

                # store
                file_store_path = f"{path2save}/{xtile}_{ytile}.json"
                with open(file_store_path, "w") as f:
                    f.write(response.content.decode("utf-8"))
                    files_stored.append(file_store_path)

                if show_tiles == True:
                    # add to map
                    geojson_data = json.loads(response.text)
                    geojson_layer = GeoJSON(data=geojson_data)
                    self.map.add_layer(geojson_layer)

        return files_stored

    def merge_tiles(self):
        """
        This function merges the OSM tiles that have been downloaded and stores with a given output file name
        """
        idx = 0
        # self.combined_rows = []
        hav_factor = self.haversine_factor()
        print("Merging files and croping for area of interest")
        for fn in tqdm(self.files_stored):
            try:
                with fiona.open(fn, "r") as f:
                    for row in f:
                        row = dict(row)
                        shape = shapely.geometry.shape(row["geometry"])

                        if self.aoi_shapes[-1].contains(shape):
                            if "id" in row:
                                del row["id"]
                            perimeter = shape.length * hav_factor
                            planar_area = shape.area * hav_factor**2
                            row["properties"] = {
                                "id": idx,
                                "height": row["properties"]["height"],
                                # "levels":row["properties"]["levels"],
                                "perimeter": perimeter,
                                "planar_area": planar_area,
                            }
                            idx += 1
                            self.combined_rows.append(row)

            except:
                pass

        # save merge
        schema = {
            "id": "int",
            "geometry": "Polygon",
            "properties": {
                "id": "int",
                "height": "int",
                # "levels":"int",
                "perimeter": "int",
                "planar_area": "int",
            },
        }

        with fiona.open(
            self.merge_file_name, "w", driver="GeoJSON", crs="EPSG:4326", schema=schema
        ) as f:
            f.writerecords(self.combined_rows)
            print(f"Merged file saved as: {self.merge_file_name}")

    def get_OSM_buildings_in_aoi(self, add_to_map=False, show_tiles=False):
        """
        This function uses the shain of functions to store and present the buildings in the area of interest
        """

        # download
        self.files_stored = self.download_OSM_buildings(self)

        # merge
        # name

        # self.merge_file_name = f'OSM_buildings_merged_latlon_{self.aoi_coordinates[-1][0][0][0]}_{self.aoi_coordinates[-1][0][0][1]}.json'
        self.merge_file_name = f"buildings_merged.json"
        self.merge_tiles()

        if show_tiles == True:
            # remove previous layers
            for i in range(len(files_stored)):
                self.map.remove_layer(self.map.layers[-1])

        # add file
        if add_to_map == True:
            with open(self.merge_file_name, "r") as f:
                geojson_data = json.load(f)
                geojson_layer = GeoJSON(data=geojson_data)
                self.map.add_layer(geojson_layer)
        else:
            with open(self.merge_file_name, "r") as f:
                geojson_data = json.load(f)
                geojson_layer = GeoJSON(data=geojson_data)

            # Create a custom control for additional functionality
            if self.isControlAdded == True:
                pass
            else:
                self.custom_control = CustomControl2(self.map)
                self.isControlAdded = True

        return self.merge_file_name

    def haversine_factor(self):
        latitude_degrees = self.aoi_coordinates[0][0][0][0]
        # Calculate the distance of one degree of latitude at the given latitude
        equator_distance_km = 111.32  # Approximate distance at the equator
        latitude_radians = math.radians(latitude_degrees)  # Convert latitude to radians
        distance_meters = equator_distance_km * 1000 * math.cos(latitude_radians)
        return distance_meters

    def add_geo_em_file(self, nc_file_path, add_to_map=True):
        # try:
        # Open the NetCDF file
        ncfile = nc.Dataset(nc_file_path, "r")

        # Read the relevant variables for extent
        try:
            xlon = ncfile.variables["XLONG"]
            xlat = ncfile.variables["XLAT"]
        except:
            try:
                xlon = ncfile.variables["XLONG_C"]
                xlat = ncfile.variables["XLAT_C"]
            except:
                try:
                    xlon = ncfile.variables["XLONG_M"]
                    xlat = ncfile.variables["XLAT_M"]
                except Exception as e:
                    print(
                        "No variable named: (XLONG/XLONG_C/XLONG_M) or (XLAT/XLAT_C/XLAT_M)"
                    )

        # Extract the minimum and maximum values to determine the extent
        # print(xlat)
        lon_min = xlon[0].min()
        lon_max = xlon[0].max()
        lat_min = xlat[0].min()
        lat_max = xlat[0].max()

        # Close the NetCDF file
        ncfile.close()

        # Return the extent as a tuple
        self.geo_em_file_extent_coordinates.append(
            [
                [lon_min, lat_min],
                [lon_min, lat_max],
                [lon_max, lat_max],
                [lon_max, lat_min],
            ]
        )
        json_string_base = '{"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": [{"type": "Feature", "properties": {"id": 0}, "geometry": {"type": "Polygon", "coordinates": [] }}]}'
        json_data_base = json.loads(json_string_base)
        json_data_base["features"][0]["geometry"][
            "coordinates"
        ] = self.geo_em_file_extent_coordinates
        self.geo_em_file_extent_data.append(json_data_base)
        self.geo_em_file_extent_geoms.append(
            {"coordinates": self.geo_em_file_extent_coordinates, "type": "Polygon"}
        )
        # self.geo_em_file_extent_shape.append(shapely.geometry.shape(self.aoi_geoms[-1]))
        self.geo_em_file_extent_shape.append(
            shapely.geometry.shape(self.geo_em_file_extent_geoms[-1])
        )

        self.aoi_coordinates.append([self.geo_em_file_extent_coordinates[-1]])
        self.aoi_extent_coordinates.append([self.geo_em_file_extent_coordinates[-1]])
        self.aoi_geoms.append(self.geo_em_file_extent_geoms[-1])
        self.aoi_shapes.append(self.geo_em_file_extent_shape[-1])

        if add_to_map == False:
            pass
        else:
            geojson_layer = GeoJSON(data=self.geo_em_file_extent_data[-1])
            self.map.add_layer(geojson_layer)

        # return (lon_min, lon_max, lat_min, lat_max)

        # except Exception as e:
        #    print(f"Error: {e}")
        #    return None

    def add_layer(self, layer):
        self.map.add_layer(layer)

    def add_buildings_to_map(self):
        with open("buildings_merged.json", "r") as f:
            geojson_data = json.load(f)
            geojson_layer = GeoJSON(data=geojson_data)
            self.map.add_layer(geojson_layer)


class CustomControl(InteractiveMap):
    def __init__(self, map_instance):
        self.map = map_instance
        self.button = Button(description="Download Buildings")
        self.button.on_click(self._on_button_click)
        self.layout = Layout(width="150px")  # Adjust width as needed
        self.control = WidgetControl(widget=VBox([self.button]), position="topright")
        self.map.add_control(self.control)

    def _on_button_click(self, b):
        # Define the behavior when the button is clicked
        # You can add your custom logic here
        self.get_OSM_buildings_in_aoi(self.map)


class CustomControl2(InteractiveMap):
    def __init__(self, map_instance):
        self.map = map_instance
        self.button2 = Button(description="Add buildings to map")
        self.button2.on_click(self._on_button_add_click)
        self.layout2 = Layout(width="150px")  # Adjust width as needed
        self.control2 = WidgetControl(widget=VBox([self.button2]), position="topright")
        self.map.add_control(self.control2)

    def _on_button_add_click(self, b):
        # Define the behavior when the button is clicked
        # You can add your custom logic here
        self.add_buildings_to_map()
