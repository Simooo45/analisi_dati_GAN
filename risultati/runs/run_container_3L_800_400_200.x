#!/bin/bash

#SBATCH --cpus-per-task=32
#SBATCH --mem-per-cpu=15G
#SBATCH --job-name=32CPU_RUN

cd /scratch/nucleare/simone.elia

export DATADIR=/scratch/nucleare/simone.elia/datas/original_data
mkdir /scratch/nucleare/simone.elia/outputs/outputs/run3L_800_400_200_R3
export WORKINGDIR=/scratch/nucleare/simone.elia/outputs/run3L_800_400_200_R3
export CODEDIR=/scratch/nucleare/simone.elia/code/BoloGAN

cd containers
srun apptainer run -B $WORKINGDIR -B $DATADIR -B $CODEDIR ./new_container.sif train pions
