from argparse import ArgumentParser, Namespace
from colorama import Fore, Back, Style
import subprocess
import os

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

    # Set output destionation from command line
    parser.add_argument('--output', help='Set output destination [Default: .]', default='.')
    
    # Get arguments from command line
    args: Namespace = parser.parse_args()

    input_sam_file_path = os.path.join(os.path.dirname(__file__),'.data/DNA_input_sam_format.sam')
    input_bam_file_path = os.path.join(os.path.dirname(__file__),'.data/DNA_input_sam_format.bam')

    # Convert reference DNA file (.fa) + aDNA files (.fq) to .sam format
    if args.aDNA2:
        subprocess.run(['minimap2', '-t', '8', '-a', '-x', 'sr', args.refDNA, args.aDNA1, args.aDNA2, '-o', input_sam_file_path])
    else:
        subprocess.run(['minimap2', '-t', '8', '-a', '-x', 'sr', args.refDNA, args.aDNA1, '-o', input_sam_file_path])
    
    # Sort sam file and convert to bam format
    subprocess.run(['samtools', 'sort', input_sam_file_path, '-o', input_sam_file_path])
    subprocess.run(['samtools', 'view', input_sam_file_path, '-o', input_bam_file_path])

    # Create output dir if it doesn't exist
    output_dir = os.path.join(args.output, 'output')
    # Create output
    subprocess.run(['mkdir', output_dir])

    ##############################################
    # PMDTools ###################################
    ##############################################
    if args.PMDtools:
        # Create
        PMDtools_output_dir_path = os.path.join(output_dir, 'PDMTools')

        # Remove PMDtools output dir if it exists
        subprocess.run(['rm', '-rf', PMDtools_output_dir_path])
        # Create PMDtools output dir
        subprocess.run(['mkdir', PMDtools_output_dir_path])

        # Open input file
        input_bam_file = open(input_bam_file_path, "r") 
        
        # Create output file
        output_pmdtools_file_path = os.path.join(PMDtools_output_dir_path, 'output.txt')
        # Open output file
        output_pmdtools_file = open(output_pmdtools_file_path, "w") 
        
        printRunningMessage('PMDtools')

        # Run PMDtools on input sam file
        subprocess.run(['python2', os.path.join(os.path.dirname(__file__), 'PMDtools/pmdtools.0.60.py'), '--platypus', '--requirebaseq', '30'], stdin=input_bam_file, stdout=output_pmdtools_file)
        
        # Close files
        input_bam_file.close()
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

        # Open input file
        input_bam_file = open(input_bam_file_path, "r") 
        
        printRunningMessage('mapDamage')

        # Run mapDamage on input sam file
        subprocess.run(['mapDamage', '-i', input_bam_file_path, '-r', args.refDNA, '--folder', mapDamage_output_dir_path])

        # Close files
        input_bam_file.close()

        printEndOfToolMessage('mapDamage')

    ##############################################
    # mapDamage ##################################
    ##############################################
    if args.pyDamage:
        # Create output dir
        pyDamage_output_dir_path = os.path.join(output_dir, 'pyDamage')
        # Remove pyDamage output dir if it exists
        subprocess.run(['rm', '-rf', pyDamage_output_dir_path])

        # Run pyDamage on input file
        subprocess.run(['pydamage', '--outdir', pyDamage_output_dir_path, 'analyze', input_bam_file_path])

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
        
    ##############################################
    # metaDamage #################################
    ##############################################
    if args.metaDamage:
        printRunningMessage('MetaDamage')

    printEndOfPipelineMessage()



if __name__ == '__main__':
    main()