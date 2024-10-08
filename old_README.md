# UrbanSurfAce

## Code Overview

UrbanSurfAce can interactive map that allows users to draw shapes on the map and then download and display OpenStreetMap (OSM) building data within the area defined by the drawn shape. The code operates in the following manner:

1. **Map Initialization**: It initializes an interactive map using the `ipyleaflet` library. Users can specify the initial map center and zoom level.

2. **Drawing Rectangles**: The map allows users to draw rectangles using a DrawControl. When a user draws a rectangle on the map, the code captures the coordinates of the drawn rectangle.

3. **Calculating OSM Tile Range**: It calculates the range of OSM tiles that intersect with the drawn rectangle. It computes the tile numbers based on the drawn area.

4. **Downloading OSM Building Data**: The code downloads OSM building data within the specified tile range. It downloads individual tiles that intersect with the drawn area and stores them in a local directory. Users can choose to display these tiles on the map.

5. **Merging Building Data**: After downloading, it merges the OSM building data from the individual tiles into a single GeoJSON file.

6. **Custom Controls**: It provides custom controls on the map. One control allows users to download OSM building data for the drawn area, and another control lets users add the merged building data to the map.

7. **Haversine Factor**: It calculates a haversine factor based on the latitude of the drawn area. This factor is used for distance calculations.

8. **Adding Geo-EM File Extent**: It can add the extent of a NetCDF file to the map.

The result is an interactive map where users can draw shapes, download OSM building data within the drawn area, and visualize this data on the map. It's a tool for exploring and working with building data in a geographic context.

The `CustomControl` and `CustomControl2` classes handle the user interactions with the map, allowing users to trigger specific actions like downloading and displaying building data.

![Alt Text](https://github.com/jacobogabeiraspenas/UrbanSurfAce/blob/main/.various/UrbanSurfAce_example.gif?raw=true)
