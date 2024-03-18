from osgeo import gdal

# List of TIFF files to merge
tiff_files = [
    '07_02_zoom4_urban_fraction_100m.tif',
    '07_03_zoom4_urban_fraction_100m.tif',
    '08_02_zoom4_urban_fraction_100m.tif',
    '08_03_zoom4_urban_fraction_100m.tif'
]

# Output file name
output_file = '07merged_zoom4_urban_fraction_100m.tif'

# Specify your nodata value here. Use the same nodata value as in your input TIFFs.
nodata_value = 0  # Adjust this value as per your data's nodata value

# Create a GDAL virtual file system that holds the list of files to be merged
vrt_options = gdal.BuildVRTOptions(resampleAlg='nearest', addAlpha=False, srcNodata=nodata_value, VRTNodata=nodata_value)
vrt_ds = gdal.BuildVRT('', tiff_files, options=vrt_options)  # Use an empty string for in-memory VRT

# Use gdal_translate to convert the VRT to the actual merged TIFF, ensuring nodata is handled
translate_options = gdal.TranslateOptions(options=["COMPRESS=LZW"], noData=nodata_value)
gdal.Translate(output_file, vrt_ds, options=translate_options)

# Clean up
vrt_ds = None

print(f'Merged file created: {output_file}')

