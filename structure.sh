wrfup/                     # Root directory of your package
│
├── wrfup/                 # Main package directory (previously py4bem/)
│   ├── __init__.py        # Initialize the package
│   ├── main.py            # Entry point (contains main() function)
│   ├── info.py            # Info class to manage arguments and settings
│   ├── download.py        # Handles downloading fields
│   ├── calculation.py     # Module for calculating fields like FRC_URB2D
│   ├── ingest.py          # Handles ingesting calculated fields into the geo_em file
│   ├── utils.py           # Utility functions (e.g., check_geo_em_file, clean_up)
│
├── tests/                 # Unit tests for your package
│   ├── test_info.py       # Tests for the Info class
│   ├── test_download.py   # Tests for downloading functionality
│   ├── test_calculation.py# Tests for calculation functions
│   ├── test_ingest.py     # Tests for ingesting fields
│   ├── test_utils.py      # Tests for utility functions
│
├── scripts/               # Optional helper scripts (for demos or examples)
│   └── example_run.py     # Example script for running wrfup
│
├── temp/                  # Temporary directory (for temporary files)
│   └── (temporary files)  # Stores temporary files during processing
│
├── README.md              # Documentation and instructions for the package
├── requirements.txt       # List of dependencies (e.g., netCDF4, pandas)
├── setup.py               # Setup script for installing wrfup
├── pyproject.toml         # Optional project configuration (if using)
└── LICENSE                # License for your package

