# %%
from ipyleaflet import (
    Map,
    basemap_to_tiles,
    basemaps,
    DrawControl,
    WidgetControl,
    LayersControl,
)
#Activate widgets to have the map work
#To do:
#Include Microsoft buildings to contrast and collapse whats not at least 90%
#Include urban fraction from vegetation fraction Copernicus
#Calculate building height distribuition properly (area) (check)
#Minimize number of levels
from ipyleaflet import Map, DrawControl, basemap_to_tiles, basemaps, GeoJSON
from ipywidgets import Button, Layout, VBox
import xarray as xr
import numpy as np
from tqdm.auto import tqdm
import time
import requests
import os
import zipfile
import io
import json
import pandas as pd
import shapely
from shapely.geometry import shape, MultiPolygon, Polygon
import fiona
import math
import netCDF4 as nc
import warnings
warnings.filterwarnings("ignore")
#remove?

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
    geo_em_file = []
    new_geo_em_file = []
    df_buildings_list =[]

    def __init__(self, center=(40.41671327747509, -3.702635610085826), zoom=0):
        
        # Get location for map
        try:
            import geocoder
            lat_me, lon_me = geocoder.ip('me').latlng
            center = (lat_me,lon_me)
            zoom = 10
        except:
            pass
        
        # Create map with specifics
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
        dsxrfile = xr.load_dataset(nc_file_path)
        self.geo_em_file.append(dsxrfile)

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


    def calculate_URB_PARAM(self, nc_file_path=None, nc_file_path_to_save=None, json_data_path=None, save_temp_files=False, mask_with_LU_INDEX=False):
        """This function calculates several urban parameters and ingests them into their respectives fields. Once run, the geo_em file is saved as geo_em_modified.nc. This file and the new fields are accessible in the following variable.
        
            # Plan Area Fraction
            self.new_geo_em_file[-1]['URB_PARAM'][0,90,:,:].plot()
            # Mean Building Height
            self.new_geo_em_file[-1]['URB_PARAM'][0,93,:,:].plot()
            # Total Building Area
            self.new_geo_em_file[-1]['URB_PARAM'][0,94,:,:].plot()
            # Building Height Distribution (117-131)
            for idx in range(117, 132):
            self.new_geo_em_file[-1]['URB_PARAM'][0,idx,:,:].plot()
            
        """
        
        # Functions 
        # Function to merge touching polygons
        def merge_touching_polygons(polygons):
            merged_polygons = []
            processed_indices = set()

            for i, (polygon1, properties1) in enumerate(polygons):
                if i not in processed_indices:
                    touching_polygons = [polygon1]

                    for j, (polygon2, properties2) in enumerate(polygons[i+1:], start=i+1):
                        if polygon1.touches(polygon2):
                            touching_polygons.append(polygon2)
                            processed_indices.add(j)

                    merged_polygon = MultiPolygon(touching_polygons).buffer(0)
                    merged_polygons.append((merged_polygon, properties1))

            return merged_polygons

        # Function to merge overlapping polygons
        def merge_overlapping_polygons(polygons):
            merged_polygons = []
            processed_indices = set()
            
            print('Merging poligons...')
            for i, (polygon1, properties1) in enumerate(tqdm(polygons, leave=False)):
                if i not in processed_indices:
                    overlapping_polygons = [polygon1]

                    for j, (polygon2, properties2) in enumerate(polygons[i+1:i+50], start=i+1):
                        if polygon1.overlaps(polygon2):  # Check for overlap instead of touch
                            overlapping_polygons.append(polygon2)
                            processed_indices.add(j)
                            properties1['height*area']+=properties2['height*area']

                    merged_polygon = MultiPolygon(overlapping_polygons).buffer(0)  # No need to apply buffer again
                    merged_polygons.append((merged_polygon, properties1))

            return merged_polygons

        # Function to reduce the buffer size of each polygon
        def reduce_buffer(polygons, original_buffer_size):
            reduced_polygons = []
            for polygon, properties in polygons:
                # Reduce the buffer size to its original value
                original_polygon = polygon.buffer(-original_buffer_size)
                reduced_polygons.append((original_polygon, properties))
            return reduced_polygons

        # Function to calculate area and perimeter for each shape
        def calculate_area_and_perimeter(data):
            areas = []
            perimeters = []
            for feature in data['features']:
                # Extract the geometry of the feature
                geometry = shape(feature['geometry'])
                # Calculate the area of the geometry and append to areas list
                area = geometry.area
                areas.append(area)
                # Calculate the perimeter of the geometry and append to perimeters list
                perimeter = geometry.length
                perimeters.append(perimeter)
            return areas, perimeters

        # Calculate the ratio from haversine
        def meters_to_degrees(lat, lon, meters=1):
            # Radius of the Earth in meters
            earth_radius = 6371000
            # Calculate the change in latitude (in degrees)
            delta_lat = meters / earth_radius * (180 / math.pi)
            # Calculate the change in longitude (in degrees)
            delta_lon = meters / (earth_radius * math.cos(math.radians(lat))) * (180 / math.pi)
            return delta_lat, delta_lon

        # Function to calculate area and perimeter for each shape
        def calculate_area_and_perimeter(geometry):
            # Extract the geometry of the feature
            shape_geometry = shape(geometry)
            # Calculate the area of the geometry
            area = shape_geometry.area
            # Calculate the perimeter of the geometry
            perimeter = shape_geometry.length
            return area, perimeter

        def find_nearest_indices(df, point_coordinates):
            lon, lat = point_coordinates
            # Calculate the difference between point coordinates and grid corner coordinates
            df['abs_diff'] = ((df['XLAT_M']- lat)**2 + (df['XLONG_M'] - lon)**2).abs()
            # Find the nearest corner indices
            nearest_indices = df[['abs_diff']].idxmin()
            distance = df_latlon_m['abs_diff'].loc[nearest_indices[0]]
            return nearest_indices[0], distance


        print('Loading files...')
        # Open the NetCDF file
        if nc_file_path:
            ncfile = nc.Dataset(nc_file_path, "r")
        elif self.geo_em_file[-1]:
            ncfile = self.geo_em_file[-1]
        else:
            print('Need a geo_em file path')

        # Load buildings
        if json_data_path:
            # Load the JSON file
            with open(json_data_path) as f:
                data = json.load(f)
        elif self.combined_rows:
            # Assing from previous variable 
            data = {}
            data['features'] = self.combined_rows.copy()
        else:
            print('Need a json file path for buildings')


        # Extract polygons and their attributes
        #polygons = [(shape(feature['geometry']), feature['properties']) for feature in data['features']]

        # Extract polygons and their attributes buffer, merge and debuffer
        print('Applying buffer and merging poligons...')
        polygons = [(shape(feature['geometry']).buffer(0.00002), feature['properties']) for feature in tqdm(data['features'])]
        
        new_features = []
        for polygon, properties in tqdm(polygons):
            
            polygon_area = polygon.area
            new_properties = {
                'height': properties['height'],  # Keep height as it is
                'area': polygon_area,     # Recalculate area
                'perimeter': polygon.length,  # Recalculate perimeter
                'height*area':properties['height']*polygon_area
            }
            new_feature = {
                'type': 'Feature',
                'properties': new_properties,
                'geometry': polygon.__geo_interface__
            }
            new_features.append(new_feature)
            
        for i in range(4):
            j = i+1
            print(f'Iteration {j}/4...')
            # Extract polygons and their attributes, apply buffer
            polygons = [(shape(feature['geometry']), feature['properties']) for feature in tqdm(new_features, leave=False)]

            # Merge overlapping polygons
            merged_polygons = merge_overlapping_polygons(polygons)

            # Recalculate attributes for merged polygons
            new_features = []
            for merged_polygon, properties in tqdm(merged_polygons):
                
                merged_polygon_area = merged_polygon.area
                new_properties = {
                    'height': properties['height*area']/merged_polygon_area,  # Weighted height
                    'area': merged_polygon_area,     # Recalculate area
                    'perimeter': merged_polygon.length,  # Recalculate perimeter
                    'height*area':properties['height*area']
                }
                new_feature = {
                    'type': 'Feature',
                    'properties': new_properties,
                    'geometry': merged_polygon.__geo_interface__
                }
                new_features.append(new_feature)

            # Update the original JSON data with the merged polygons and their attributes
            new_data = {
                'type': 'FeatureCollection',
                'features': new_features
            }

            # Save the updated JSON data to a new file or overwrite the original file
            if save_temp_files:
                print('Saving temporary file...')
                with open(f'temp_updated_file_iteration_{j}.json', 'w') as f:
                    json.dump(new_data, f)
            else:
                pass


        print('Reducing buffer to original size...')
        # Extract polygons and their attributes
        polygons = [(shape(feature['geometry']), feature['properties']) for feature in new_data['features']]

        # Reduce the buffer size to its original value
        original_buffer_size = 0.00002  # Assuming original buffer size
        reduced_polygons = reduce_buffer(polygons, original_buffer_size)

        # Convert reduced polygons back to GeoJSON format
        updated_features = []
        for polygon, properties in reduced_polygons:
            feature = {
                'type': 'Feature',
                'properties': properties,
                'geometry': polygon.__geo_interface__
            }
            updated_features.append(feature)

        # Create a new FeatureCollection with reduced buffer polygons
        updated_data = {
            'type': 'FeatureCollection',
            'features': updated_features
        }


        # load again
        data = updated_data.copy()

        print('Calculating properties of poligons...')
        # Calculate the ratio from haversine
        lon, lat = feature['geometry']['coordinates'][0][0]  # Assuming the first coordinate pair represents the centroid
        # Get the height of the shape in meters
        height_meters = feature['properties']['height']
        # Convert height from meters to degrees
        delta_lat, delta_lon = meters_to_degrees(lat, lon)

        # Calculate areas and perimeters for each shape and add them as fields
        for feature in data['features']:
            # Calculate area and perimeter
            area, perimeter = calculate_area_and_perimeter(feature['geometry'])
            # Add area and perimeter as fields in the properties of each shape
            feature['properties']['area'] = area/(delta_lat*delta_lon)
            feature['properties']['area_deg'] = area
            feature['properties']['perimeter'] = 2*perimeter/(delta_lat+delta_lon)

        # Save the updated GeoJSON data to a new file
        if save_temp_files:
            with open('temp_updated_file_with_area_perimeter.json', 'w') as f:
                json.dump(data, f)
        else:
            pass


        # Calculation of URB_PARAM fields
        dsxr = self.geo_em_file[-1]

        df_lat_m = dsxr[['XLAT_M']]['XLAT_M'][0].to_dataframe()
        df_lon_m = dsxr[['XLONG_M']]['XLONG_M'][0].to_dataframe()
        df_latlon_m = df_lat_m.join(df_lon_m)
        df_lat_c = dsxr[['XLAT_C']]['XLAT_C'][0].to_dataframe()
        df_lon_c = dsxr[['XLONG_C']]['XLONG_C'][0].to_dataframe()
        df_latlon_c = df_lat_c.join(df_lon_c)

        # check what point is each shape closer to
        print('Assigning poligons to grid...')
        # Function to find the nearest corner indices for a given point
        max_distance = df_latlon_m.diff()['XLONG_M'].max()/1.2

        for i,feature in enumerate(data['features']):
            if feature['geometry']['type'] == 'Polygon':
                point_coordinates = np.array(feature['geometry']['coordinates'][0]).mean(axis=0)
                id_ij, dist_ij = find_nearest_indices(df_latlon_m, point_coordinates)
                id_i, id_j  = id_ij
                if dist_ij < max_distance:
                    data['features'][i]['properties'].update({'id_i': int(id_i)})
                    data['features'][i]['properties'].update({'id_j': int(id_j)})
                else:
                    data['features'][i]['properties'].update({'id_i': -1000})
                    data['features'][i]['properties'].update({'id_j': -1000})

            elif feature['geometry']['type'] == 'MultiPolygon':
                point_coordinates = np.array(feature['geometry']['coordinates'][0][0]).mean(axis=0)
                id_ij, dist_ij = find_nearest_indices(df_latlon_m, point_coordinates)
                id_i, id_j  = id_ij
                if dist_ij < max_distance:
                    data['features'][i]['properties'].update({'id_i': int(id_i)})
                    data['features'][i]['properties'].update({'id_j': int(id_j)})
                else:
                    data['features'][i]['properties'].update({'id_i': -1000})
                    data['features'][i]['properties'].update({'id_j': -1000})


        print('Calculating URB_PARAM fields...')
        df_buildings = pd.json_normalize(data['features'])
        
        #NEW
        self.df_buildings_list.append(df_buildings)

        df_buildings = df_buildings.rename(columns = {'properties.id_i':'south_north','properties.id_j':'west_east'})

        df_buildings['buildingSurface'] = df_buildings['properties.perimeter']*df_buildings['properties.height']+df_buildings['properties.area']

        df_buildingAreaSurface = df_buildings[['south_north','west_east','properties.area','properties.area_deg','properties.height*area','buildingSurface']].groupby(['south_north','west_east']).sum()

        df_buildingAreaSurface['properties.height'] = df_buildingAreaSurface['properties.height*area'].values/df_buildingAreaSurface['properties.area_deg'].values

        #OLD
        '''
        # Define the bin edges and labels
        bin_edges = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 2000]
        bin_labels = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]

        # Create the 'heightDist' column
        df_buildings['heightDist'] = pd.cut(df_buildings['properties.height'], bins=bin_edges, labels=bin_labels)

        df_buildingDist = df_buildings[['south_north','west_east','heightDist','type']].groupby(['south_north','west_east','heightDist']).count()

        df_buildingDist = df_buildingDist/df_buildingDist.groupby(['south_north','west_east']).sum()

        df_buildingDistPivot = df_buildingDist.reset_index().set_index(['south_north', 'west_east']).pivot(columns='heightDist',values='type')
        '''
        
        #NEW
        # Define the bin edges and labels
        bin_edges = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 2000]
        bin_labels = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]

        # Create the 'heightDist' column
        df_buildings['heightDist'] = pd.cut(df_buildings['properties.height'], bins=bin_edges, labels=bin_labels)

        # Calculate the building area
        df_buildings['buildingArea'] = df_buildings['properties.height'] * df_buildings['properties.area']

        # Group by grid cell and height distribution, and sum the building areas
        df_buildingDist = df_buildings.groupby(['south_north', 'west_east', 'heightDist'])['buildingArea'].sum().reset_index()

        # Group by grid cell and normalize the building areas
        df_buildingDist['totalArea'] = df_buildingDist.groupby(['south_north', 'west_east'])['buildingArea'].transform('sum')
        df_buildingDist['buildingDist'] = df_buildingDist['buildingArea'] / df_buildingDist['totalArea']

        # Pivot the table to get the distribution by height bins as columns
        df_buildingDistPivot = df_buildingDist.pivot_table(index=['south_north', 'west_east'], columns='heightDist', values='buildingDist', fill_value=0)


        df_lon_diff_c = df_latlon_c.diff()[['XLONG_C']]/delta_lon
        df_lat_diff_c = df_latlon_c.reset_index().set_index(['west_east_stag','south_north_stag']).sort_index().diff()[['XLAT_C']]/delta_lat
        df_latlon_diff_c = df_lat_diff_c.join(df_lon_diff_c)
        df_latlon_diff_c['area_cell'] = df_latlon_diff_c['XLAT_C']*df_latlon_diff_c['XLONG_C']

        df_grid_area = df_latlon_diff_c[(df_latlon_diff_c.index.get_level_values('west_east_stag') > 0) & (df_latlon_diff_c.index.get_level_values('south_north_stag') > 0)]['area_cell']
        df_grid_area = df_grid_area.reset_index().rename(columns={'west_east_stag':'west_east', 'south_north_stag':'south_north'})
        df_grid_area[['south_north','west_east']] = df_grid_area[['south_north','west_east']]-1
        df_grid_area = df_grid_area.set_index(['south_north','west_east'])

        df_URB_PARAM = df_latlon_m.join(df_grid_area).join(df_buildingAreaSurface).join(df_buildingDistPivot)

        df_URB_PARAM['plan_area_fraction'] = df_URB_PARAM['properties.area']/df_URB_PARAM['area_cell']
        # Create a boolean mask to identify rows where 'plan_area_fraction' is greater than 1
        mask = df_URB_PARAM['plan_area_fraction'] > 1
        # Update the values of 'plan_area_fraction' that are greater than 1 to 1
        df_URB_PARAM.loc[mask, 'plan_area_fraction'] = 1
        df_URB_PARAM['lambdaP'] = df_URB_PARAM['properties.area']/df_URB_PARAM['area_cell']
        df_URB_PARAM = df_URB_PARAM.fillna(0)

        print('Ingesting fields in URB_PARAM...')
        # get shape
        shape_grid = dsxr['URB_PARAM'][0,0].shape
        # Plan area fraction (area of roofs/area of the grid cell)
        dsxr['URB_PARAM'][0,90] = df_URB_PARAM['plan_area_fraction'].values.T.reshape(shape_grid[0],shape_grid[1])
        # Mean building height
        dsxr['URB_PARAM'][0,93] = df_URB_PARAM['properties.height'].values.T.reshape(shape_grid[0],shape_grid[1])
        # Total area of buildings (roof+walls)/area of the grid cell
        dsxr['URB_PARAM'][0,94] = df_URB_PARAM['lambdaP'].values.T.reshape(shape_grid[0],shape_grid[1])
        # If you have a building height distribution, you can put it in the fields (i,j,118-132), every 5m
        dsxr['URB_PARAM'][0,117:] = df_URB_PARAM[bin_labels].values.T.reshape(15,shape_grid[0],shape_grid[1])

        if mask_with_LU_INDEX:
            dsxr['URB_PARAM'] = dsxr['URB_PARAM'].where(dsxr['LU_INDEX']>29,0)
        else:
            pass
        
        # Save file
        if nc_file_path_to_save:
            print(f'Saving new file as {nc_file_path_to_save}')
            dsxr.to_netcdf(nc_file_path_to_save)
        else:
            print('Saving new file as geo_em_modified.nc')
            dsxr.to_netcdf('geo_em_modified.nc')
            
        # Append new file
        self.new_geo_em_file.append(dsxr)
        
        
        
    # Urban Fraction
    def get_urban_fraction_in_aoi(self):

        # Get tiles in area of interest:
        def lat_lon_to_urban_fraction_tile_in_aoi(lat, lon, grid_rows=16, grid_cols=16):
            """
            Convert latitude and longitude to a grid tile index, considering the dataset's specific latitude range.

            Args:
                lat (float): Latitude in degrees.
                lon (float): Longitude in degrees.
                grid_rows (int): Number of rows in the grid.
                grid_cols (int): Number of columns in the grid.

            Returns:
                (int, int): A tuple (row_index, col_index) representing the tile's position.
            """
            # Adjust the latitude range from +84 to -60
            lat_min = -60
            lat_max = 84

            # Normalize latitude and longitude to a 0-1 scale based on the dataset's coverage
            lat_relative = (lat - lat_max) / (lat_min - lat_max)  # Adjusted for specific lat range
            lon_relative = (lon + 180) / 360  # 0 on the left (west), 1 on the right (east)

            # Calculate the tile indices
            row_index = int(lat_relative * grid_rows)
            col_index = int(lon_relative * grid_cols)

            # Ensure indices are within the bounds of the grid
            row_index = min(max(row_index, 0), grid_rows - 1)
            col_index = min(max(col_index, 0), grid_cols - 1)

            return row_index, col_index


        # Get tiles names in area of interest:
        def urban_fraction_tile_name_in_aoi(grid_rows=16, grid_cols=16):

            tile_names = []
            for lon, lat in self.aoi_extent_coordinates[0][0]:

                row_index, col_index = lat_lon_to_urban_fraction_tile_in_aoi(lat, lon, 16, 16)
                tile_name = f"{row_index:02d}_{col_index:02d}_zoom4_urban_fraction_100m_int8"
                #print(f"The tile for latitude {lat} and longitude {lon} at zoom level 4 is: {tile_name}")

                tile_names.append(tile_name)

            return list(np.unique(tile_names))

        def download_and_extract_zip(zip_url, extraction_path):
            # Send a GET request to the URL
            response = requests.get(zip_url)
            # Check if the request was successful
            if response.status_code == 200:
                # Open the ZIP file contained in the response's bytes
                with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
                    # Extract all the contents into the specified directory
                    thezip.extractall(extraction_path)
                print("File successfully downloaded and extracted.")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")

        def download_urban_fraction_tiles():
            import os
            import requests
            import zipfile
            import io

            # Check and create directory
            path2save = "Urban_Fraction_Tiles"
            if os.path.exists(path2save):
                print(f"Tiles will be stored in {path2save}")
            else:
                print(f"Creating directory to store files: {path2save}")
                os.makedirs(path2save)

            # Assuming tile_names and the construction of file_name are defined somewhere in your script
            tile_names = urban_fraction_tile_name_in_aoi() # actual tile names
            for tile_name in tqdm(tile_names):
                file_name = f"{tile_name}.zip"  # Placeholder for actual logic to construct file_name
                # URL of the ZIP file containing the TIFF
                zip_file_url = f"https://github.com/jacobogabeiraspenas/UrbanSurfAce/raw/main/data/urban_fraction/zoom_4/{file_name}"

                # Use the function and pass path2save as the extraction_path
                download_and_extract_zip(zip_file_url, path2save)

            return [f"{path2save}/{tile_name}.tif" for tile_name in tile_names]


        # Download and save file locations
        self.saved_urban_fraction_tiles = download_urban_fraction_tiles()



#class UrbanFraction(InteractiveMap):
    



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
