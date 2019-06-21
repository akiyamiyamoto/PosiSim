# Scripts here creates files for fluka geometry and scoring.

This directory is for creating geometry data and scoring data for Fluka.
These data and script to build them evolves time to time. Past data are 
kept in sperate directories. The direcotry name is used as a version.

## Scripts

- `geobuild.py` : Main script to build geometry.  Geometry parameters are defined here.
- `create_geometry.py` : Used by `geobuild.py` and create geometry data, except target area.
- `create_target.py` : Used by `geobuild.py` and create target area geometry data
- `FLUdata.py` : Utility functions used by above scripts.
- `version.py` : Define a version number attached to the created data

When `geobuild.py` is executed, three data files, for body, region, and assignmat 
of fluka were created.   `geotest.inp` is preared to check the geometry visually using flair.

- `buildcard.py` : Create data card for scoring.

Files created by these scripts should be included properly to your fluka input file.


