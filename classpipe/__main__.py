from argparse import ArgumentParser, Namespace
from colorama import Fore, Back, Style
import subprocess
import os

def printErrorMessage(message):
    print(Fore.RED + Style.BRIGHT + '[ERROR]', end=' ')
    print(message)
    print(Style.RESET_ALL)

def printRunningMessage(toolName):
    print(Fore.BLUE + Style.BRIGHT + '> Running on', toolName)
    print(Style.RESET_ALL)

def printEndOfPipelineMessage():
    print(Fore.GREEN + Style.BRIGHT + '> Pipeline finished')
    print(Style.RESET_ALL)

def printEndOfToolMessage(toolName):
    print(Fore.GREEN + Style.BRIGHT + '> Finished running on', toolName)
    print(Style.RESET_ALL)


def main():
    parser = ArgumentParser()

    # Set input DNA files
    parser.add_argument('--refDNA', help='Input reference DNA files')
    parser.add_argument('--aDNA1', help='Input aDNA file 1')
    parser.add_argument('--aDNA2', help='Input aDNA file  [Optional]', default=None)

    # Set tools from command line 
    parser.add_argument('--PMDtools', action='store_true', help='Run data on PMDTools')
    parser.add_argument('--mapDamage', action='store_true', help='Run data on mapDamage')
    parser.add_argument('--pyDamage', action='store_true', help='Run data on pyDamage')
    parser.add_argument('--damageProfiler', action='store_true', help='Run data on damageProfiler')
    parser.add_argument('--atlas', action='store_true', help='Run data on Atlas')
    parser.add_argument('--metaDamage', action='store_true', help='Run data on metaDamage')
    parser.add_argument('--saveBam', action='store_true', help='Save generated BAM and BAI files to output dir')

    # Set output destionation from command line
    parser.add_argument('--output', help='Set output destination [Default: .]', default='.')
    
    # Get arguments from command line
    args: Namespace = parser.parse_args()

    # Create output dir if it doesn't exist
    output_dir = args.output
    if args.output == '.':
        output_dir = os.path.join(args.output, 'class_pipe_output')

    bam_dir = os.path.join(os.path.dirname(__file__), '.data')
    input_sam_file_path = os.path.join(bam_dir, 'DNA_input.sam')
    input_bam_file_path = os.path.join(bam_dir, 'DNA_input.bam')        

    # Save BAM and BAI to output
    if args.saveBam:
        bam_dir = os.path.join(output_dir, 'BAM')
        subprocess.run(['rm', '-rf', bam_dir])
        subprocess.run(['mkdir', bam_dir])
        input_sam_file_path = os.path.join(bam_dir, 'DNA_input.sam')
        input_bam_file_path = os.path.join(bam_dir, 'DNA_input.bam')


    # Check if file DNA inputs are in a valid format 
    if args.aDNA1.endswith('.fq') or args.aDNA1.endswith('.fastq') or args.aDNA1.endswith('.fq.gz') or args.aDNA1.endswith('.fastq.gz'):
        # Convert reference DNA file (.fa) + aDNA files (.fq) to .sam format
        if args.aDNA2:
            subprocess.run(['minimap2', '-t', '8', '-a', '-x', 'sr', args.refDNA, args.aDNA1, args.aDNA2, '-o', input_sam_file_path])
        else:
            subprocess.run(['minimap2', '-t', '8', '-a', '-x', 'sr', args.refDNA, args.aDNA1, '-o', input_sam_file_path])
        subprocess.run(['samtools', 'view', '-b', input_sam_file_path, '-o', input_bam_file_path])
        subprocess.run(['rm', '-rf', input_sam_file_path])
    elif args.aDNA1.endswith('.bam') or args.aDNA1.endswith('.sam'):
        # Move .bam/.sam file to .data directory
        if args.aDNA1.endswith('.bam'):
            input_bam_file_path = os.path.abspath(args.aDNA1)
        elif args.aDNA1.endswith('.sam'):
            input_sam_file_path = os.path.abspath(args.aDNA1)
            subprocess.run(['samtools', 'view', '-b', input_sam_file_path, '-o', input_bam_file_path])
            subprocess.run(['rm', '-rf', input_sam_file_path])
    else:
        message = 'Provide a valid format for the input DNA (.fq, .bam, .sam)'
        printErrorMessage(message)

    # Add MD tag
    input_bam_aligned_file_path = os.path.join(bam_dir, 'DNA_input_aligned.bam')
    input_bam_aligned_file = open(input_bam_aligned_file_path, '+w')
    subprocess.run(['samtools', 'calmd', '-b', input_bam_file_path, args.refDNA], stdout=input_bam_aligned_file)
    input_bam_aligned_file.close()

    # Sort reads
    input_bam_aligned_sorted_file_path = os.path.join(bam_dir, 'DNA_input_aligned_sorted.bam')
    subprocess.run(['samtools', 'sort', input_bam_aligned_file_path, '-o', input_bam_aligned_sorted_file_path])
    
    # Index reads
    input_bam_index_file_path = os.path.join(bam_dir, 'DNA_input_aligned_sorted.bai')
    subprocess.run(['samtools', 'index', input_bam_aligned_sorted_file_path, input_bam_index_file_path])
    
    ##############################################
    # PMDTools ###################################
    ##############################################
    if args.PMDtools:
        # Create
        PMDtools_output_dir_path = os.path.join(output_dir, 'PDMtools')

        # Remove PMDtools output dir if it exists
        subprocess.run(['rm', '-rf', PMDtools_output_dir_path])
        # Create PMDtools output dir
        subprocess.run(['mkdir', PMDtools_output_dir_path])

        # Create script to plot hist
        output_hist_script_pmdtools_file_path = os.path.join(PMDtools_output_dir_path, 'generate_hist.r')
        output_hist_script_pmdtools_file = open(output_hist_script_pmdtools_file_path, "w+")
        output_hist_script_pmdtools_file.write('pmd_scores <- read.delim("output.txt", header = FALSE, sep = "\t")\nhist_data <- hist(pmd_scores$V4, breaks = 1000, xlab = "PMDscores")\nplot(hist_data, main="Histogram of PMD Scores", xlab = "PMDscores", ylab = "Frequency")')
        output_hist_script_pmdtools_file.close()

        # Create output file
        output_pmdtools_file_path = os.path.join(PMDtools_output_dir_path, 'output.txt')
        # Open output file
        output_pmdtools_file = open(output_pmdtools_file_path, "w+") 
        
        printRunningMessage('PMDtools')

        # Run PMDtools on input bam file
        sp = subprocess.run(['samtools', 'view', '-h', input_bam_aligned_sorted_file_path], check=True, capture_output=True)
        subprocess.run(['python2', os.path.join(os.path.dirname(__file__), 'PMDtools/pmdtools.0.60.py'), '--printDS'], input=sp.stdout, stdout=output_pmdtools_file)

        output_pmdtools_file.close()

        printEndOfToolMessage('PMDtools')


    ##############################################
    # mapDamage ##################################
    ##############################################
    if args.mapDamage:
        # Create output dir
        mapDamage_output_dir_path = os.path.join(output_dir, 'mapDamage')
        # Remove mapDamage output dir if it exists
        subprocess.run(['rm', '-rf', mapDamage_output_dir_path])
        # Create mapDamage output dir
        subprocess.run(['mkdir', mapDamage_output_dir_path])

        printRunningMessage('mapDamage')

        # Run mapDamage on input sam file
        subprocess.run(['mapDamage', '-i', input_bam_aligned_sorted_file_path, '-r', args.refDNA, '-d', mapDamage_output_dir_path, '--merge-reference-sequences', '--no-stats'])

        printEndOfToolMessage('mapDamage')

    ##############################################
    # pyDamage ###################################
    ##############################################
    if args.pyDamage:
        # Create output dir
        pyDamage_output_dir_path = os.path.join(output_dir, 'pyDamage')
        # Remove pyDamage output dir if it exists
        subprocess.run(['rm', '-rf', pyDamage_output_dir_path])

        printRunningMessage('pyDamage')

        # Run pyDamage on input file
        subprocess.run(['pydamage', '--outdir', pyDamage_output_dir_path, 'analyze', input_bam_aligned_sorted_file_path, '--plot'])

    ##############################################
    # damageProfiler ##############################
    ##############################################
    if args.damageProfiler:
        # Create output dir
        damageProfiler_output_dir_path = os.path.join(output_dir, 'DamageProfiler')
        # Remove pyDamage output dir if it exists
        subprocess.run(['rm', '-rf', damageProfiler_output_dir_path])

        printRunningMessage('DamageProfiler')

        # Run DamageProfiler on input file
        subprocess.run(['java', '-jar', os.path.join(os.path.dirname(__file__), 'DamageProfiler/DamageProfiler-1.1-java11.jar'), '-i', input_bam_file_path, '-r', args.refDNA, '-o', damageProfiler_output_dir_path])


    ##############################################
    # Atlas ######################################
    ##############################################
    if args.atlas:
        printRunningMessage('Atlas')
        # subprocess.run([os.path.join(os.path.dirname(__file__), './atlas/atlas'), '--help'])
        atlas_output_dir_path = os.path.join(output_dir, 'atlas')
        command = os.path.join(os.path.dirname(__file__), './atlas/atlas') + ' task=PMD' + ' bam=' + input_bam_file_path + ' fasta=' + args.refDNA + ' lenght=50' + ' out=' + atlas_output_dir_path
        subprocess.run(command, shell=True)
        # ./atlas task=PMD bam=example.bam fasta=reference.fa length=50
    
    ##############################################
    # metaDamage #################################
    ##############################################
    if args.metaDamage:
        printRunningMessage('MetaDamage')

    # Delete unused files
    # subprocess.run(['rm', '-rf', input_bam_file_path])
    # subprocess.run(['rm', '-rf', input_bam_aligned_file_path])
    
    printEndOfPipelineMessage()


if __name__ == '__main__':
    main()