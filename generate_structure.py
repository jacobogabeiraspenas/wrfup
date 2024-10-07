import os

# Define the directory structure
package_name = "wrfup"
structure = {
    package_name: [  # Main package directory
        "__init__.py",
        "main.py",
        "info.py",
        "download.py",
        "calculation.py",
        "ingest.py",
        "utils.py"
    ],
    "tests": [  # Tests directory
        "test_info.py",
        "test_download.py",
        "test_calculation.py",
        "test_ingest.py",
        "test_utils.py"
    ],
    "scripts": [  # Scripts directory
        "example_run.py"
    ],
    "temp": [],  # Temporary directory, no initial files
    ".": [  # Root files
        "README.md",
        "requirements.txt",
        "setup.py",
        "LICENSE"
    ]
}

# Create directories and files
def create_structure():
    for directory, files in structure.items():
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created.")
        
        # Create files inside the directory
        for file in files:
            file_path = os.path.join(directory, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    if file == "__init__.py":
                        f.write(f"# {directory} module initialization\n")
                    elif file == "README.md":
                        f.write(f"# {package_name} Package\n\nThis is the README for the {package_name} package.")
                    elif file == "requirements.txt":
                        f.write("netCDF4\npandas\n# Add other dependencies here\n")
                    elif file == "setup.py":
                        f.write(f"""
from setuptools import setup, find_packages

setup(
    name="{package_name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'netCDF4',
        'pandas',
        # Add more dependencies here
    ],
    # Other metadata...
)
""")
                    else:
                        f.write(f"# {file} in {directory}\n")
                print(f"File '{file}' created in '{directory}'.")

if __name__ == "__main__":
    create_structure()
    print("\nDirectory structure and files have been created (if they didn't already exist).")

