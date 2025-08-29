# Installation & Usage

Follow the official installation guide:  
[Copernicus Marine Toolbox Installation](https://help.marine.copernicus.eu/en/articles/7970514-copernicus-marine-toolbox-installation)

## 1. Environment Setup
- Create a new conda/mamba environment using the provided `env.yml` file  
  **or**  
- Install the `copernicusmarine` package into your existing environment (e.g. `pip install copernicusmarine`, `conda install -c conda-forge copernicusmarine` ).
    - Sometimes it installs an older version, to test run `pip show copernicusmarine`, it should be version: 2.2.2 (written on August 28th, 2025).
    - If so, run pip/conda update copernicusmarine.

## 2. Login
Open a terminal inside the environment where the package is installed and run:

`copernicusmarine login`

You will be prompted for your credentials:

`Copernicus Marine username`:

## 3. run the notebook satellite_static_plots.py to generate static plots of the most recent satellite data
