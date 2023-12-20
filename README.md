# aDNA-Classification-Pipeline
Pipeline for classification of aDNA (.fq) based on reference DNA (.fq). 

## Description
The aDNA Classification Pipeline (classpipe) is a tool to automate the damage pattern analysis across multiple tools (Currently supporting pyDamage, mapDamage and DamageProfiler), taking care of installing all the necessary dependencies for all the tools. 
Classpipe takes as input a reference fasta file, one or two fastq reads and, optionally, an output directory, and generates the corresponding outputs based on the flags assigned by the user. It is a way to make easier and faster to get aDNA damage pattern analysis data in order to analyse and compare among several tools.
The pipeline also makes easier to use the tools by creating an unique interface that takes the inputs (As mentioned, a reference fasta file and one or two fastq reads) and dealing internally with the different input variations and requisitions, then outputting the results in an organized folder structure.
The tool is hosted in github (https://github.com/djyamunaq/aDNA-Classification-Pipeline.git), where there are instructions for installation and basic usage.

## Downloading:
```
$ git clone https://github.com/djyamunaq/aDNA-Classification-Pipeline.git
```

## Installation:
The file install.sh is responsible for installing necessary dependencies and setup to run the pipeline.
```
$ cd aDNA-Classification-Pipeline
$ ./install.sh
```

## Usage:
The pipeline expects as input a fasta format file (.fa) with the mtDNA reference and one or two fastq reads. It will output in separated folders the results for each tool selected by flags.
After installation, it is possible to run the program with the *classpipe* command in any directory.
```
$ classpipe [-h] [--refDNA REFDNA] [--aDNA1 ADNA1] [--aDNA2 ADNA2] [--PMDtools] [--mapDamage] [--pyDamage] [--damageProfiler]
                 [--atlas] [--metaDamage] [--output OUTPUT]
```
Use flag -h or --help to check on how to use the program.
```
$ classpipe -h
```