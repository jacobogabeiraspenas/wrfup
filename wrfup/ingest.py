# wrfup/ingest.py
import logging

def ingest_fields(info, calculated_data, ds):
    """
    Ingest the calculated data into the geo_em file.
    
    Args:
        info (Info): The configuration object containing paths and settings.
        calculated_data (np.ndarray): The data that has been calculated and needs to be ingested.
        ds (xarray.Dataset): The already opened geo_em dataset.
    """
    logging.info(f"Ingesting {info.field} into {info.geo_em_file}...")

    # Ingest the calculated data into the appropriate field in the dataset
    ds[info.field][:] = calculated_data
    print('calculated_data = ', calculated_data)
    print('max and min = ', calculated_data.max(), calculated_data.min())
    print('Ingo geoem : ', info.geo_em_file)
    # Write the changes to the file
    ds.to_netcdf(info.geo_em_file)
