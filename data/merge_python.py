from osgeo import gdal

# List of TIFF files to merge
tiff_files = [
    '00_00_zoom4_urban_fraction_100m.tif',
    '00_01_zoom4_urban_fraction_100m.tif',
    '01_00_zoom4_urban_fraction_100m.tif',
    '01_01_zoom4_urban_fraction_100m.tif'
]

# Output file name
output_file = 'merged_zoom4_urban_fraction_100m.tif'

# Create a GDAL virtual file system that holds the list of files to be merged
vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False, VRTNodata=0)
vrt_ds = gdal.BuildVRT('', tiff_files, options=vrt_options)  # Use an empty string for in-memory VRT

# Use gdal_translate to convert the VRT to the actual merged TIFF
gdal.Translate(output_file, vrt_ds, options="-co COMPRESS=LZW")

# Clean up
vrt_ds = None

print(f'Merged file created: {output_file}')

