# Example to use this tool

## To submit fluka jobs,

1. Create data cards for geometry and scoring.
Scripts in `geobuild` directory could be used  for easy preparation of them.

2. Copy files here to your running directory

- `oneyear.inp` : Input file for fluka. Included files should be modified to match you files.
  If appropriate, a symbolic link to `geobuild` in this directory for easy reference to 
  the geometry data.

- Execute `mk_jobdir.sh` to create directories to run many fluka jobs in batch. 

- `source bsub.sh` in job directory will submit job.  

## To summarize fluka jobs.

- Various figures could be produced by a procedure described in `howto.txt` in `scripts` directory.

   
