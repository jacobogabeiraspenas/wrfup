# main.py in wrfup
import argparse
import logging
from wrfup.info import Info
from wrfup.download import download_fields
from wrfup.calculation import calculate_fields
from wrfup.ingest import ingest_fields
from wrfup.utils import clean_up, check_geo_em_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wrfup.log"),
        logging.StreamHandler()
    ]
)

def main(argv=None):
    """
    Main entry point for wrfup package.
    Parses command-line arguments and coordinates downloading fields,
    performing calculations, and ingesting fields into the WRF geo_em file.
    """

    parser = argparse.ArgumentParser(
        description="Ingest urban data (FRC_URB2D, URB_PARAM) into geo_em.d0X.nc file."
    )

    # Required arguments
    parser.add_argument('geo_em_file', type=str, help="Path to the WRF geo_em.d0X.nc file.")
    parser.add_argument('field', type=str, choices=['FRC_URB2D', 'URB_PARAM'],
                        help="Field to ingest into the geo_em file.")

    # Optional arguments
    parser.add_argument('--temp_dir', type=str, default='./temp',
                        help="Directory for temporary files (default: ./temp).")

    args = parser.parse_args(argv)

    # Create an Info object to store paths and configuration
    info = Info.from_argparse(args)

    # Step 1: Check the geo_em file for required fields
    logging.info("Checking the geo_em file for required fields...")
    if not check_geo_em_file(info.geo_em_file, info.field):
        logging.error(f"Required field {info.field} is missing from the geo_em file. Exiting...")
        return 1

    # Step 2: Download necessary fields
    logging.info("Downloading fields...")
    download_fields(info)

    # Step 3: Perform calculations to prepare data for ingestion
    logging.info("Calculating fields...")
    calculated_data = calculate_fields(info)

    # Step 4: Ingest fields into the geo_em file
    logging.info(f"Ingesting {args.field} into the geo_em file...")
    ingest_fields(info, calculated_data)

    # Step 5: Clean up temporary files
    logging.info("Cleaning up temporary files...")
    clean_up(info.temp_dir)

    logging.info("Process completed successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

