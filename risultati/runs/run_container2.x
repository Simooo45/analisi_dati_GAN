#!/bin/sh

#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=5G
#SBATCH --job-name=DISC_EXPERIMENT
#SBATCH --time 20:00:00


cd /scratch/nucleare/simone.elia/runs

export XML_CONFIG=binning_1L_128.xml
export WORKINGDIR=/scratch/nucleare/simone.elia/outputs/run1L_128
mkdir $WORKINGDIR

export DATADIR=/scratch/nucleare/simone.elia/datas/data
export CODEDIR=/scratch/nucleare/simone.elia/code/BoloGAN

srun apptainer run -B $WORKINGDIR -B $DATADIR -B $CODEDIR /scratch/nucleare/simone.elia/containers/new_container.sif train pions