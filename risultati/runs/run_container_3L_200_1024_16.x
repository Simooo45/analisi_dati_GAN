#!/bin/sh

#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=15G
#SBATCH --job-name=2_DISC_EXPERIMENT
#SBATCH --time 24:00:00

cd /scratch/nucleare/simone.elia/runs

export XML_CONFIG=binning_3L_200_1024_16.xml
export WORKINGDIR=/scratch/nucleare/simone.elia/outputs/run3L_200_1024_16_R3
mkdir $WORKINGDIR

export DATADIR=/scratch/nucleare/simone.elia/datas/data
export CODEDIR=/scratch/nucleare/simone.elia/code/BoloGAN

srun apptainer run -B $WORKINGDIR -B $DATADIR -B $CODEDIR /scratch/nucleare/simone.elia/containers/new_container.sif train pions
