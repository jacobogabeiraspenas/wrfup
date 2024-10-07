# info.py in wrfup
import os
from typing import NamedTuple

class Info(NamedTuple):
    """
    Immutable class that stores configuration details such as file paths and options.
    This class will be used to pass necessary information between different modules.
    """
    geo_em_file: str         # Path to the geo_em.d0X.nc file
    temp_dir: str            # Directory for temporary files
    field: str               # Field to ingest (FRC_URB2D or URB_PARAM)

    @classmethod
    def from_argparse(cls, args) -> 'Info':
        """
        Create an Info instance from the argparse Namespace.
        This method extracts the necessary fields from argparse arguments and
        constructs the Info object.
        """
        return cls(
            geo_em_file=args.geo_em_file,
            temp_dir=args.temp_dir,
            field=args.field
        )

