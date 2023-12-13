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
    print(Fore.GREEN + Style.BRIGHT + '> Ended running on', toolName)
    print(Style.RESET_ALL)


def main():
    parser = ArgumentParser()

    # Set input DNA files
    parser.add_argument('--refDNA', help='Input reference DNA files')
    parser.add_argument('--aDNA1', help='Input aDNA file 1')
    parser.add_argument('--aDNA2', help='Input aDNA file 2')

    # Set tools from command line 
    parser.add_argument('--pmdTools', help='Run data on PMDTools')
    parser.add_argument('--mapDamage', help='Run data on mapDamage')
    parser.add_argument('--pyDamage', help='Run data on pyDamage')
    parser.add_argument('--damageProfile', help='Run data on damageProfile')
    parser.add_argument('--atlas', help='Run data on Atlas')
    parser.add_argument('--metaDamage', help='Run data on metaDamage')

    # Set output destionation from command line
    parser.add_argument('--output', help='Set output destination [Default: ./output]', default='output')
    
    # Get arguments from command line
    args: Namespace = parser.parse_args()

    # Convert reference DNA file (.fa) + aDNA files (.fq) to .sam format
    subprocess.run(['ls'])
    subprocess.run([os.path.join(os.path.dirname(__file__),'./minimap2/minimap2'), '-t', '8', '-a', '-x', 'sr', args.refDNA, args.aDNA1, args.aDNA2, '-o', os.path.join(os.path.dirname(__file__),'.data/sam/DNA_input_sam_format.sam')])

    ##############################################
    # PMDTools ###################################
    ##############################################
    if args.pmdTools:
        printRunningMessage('PMDtools')
        subprocess.run(['samtools', 'view', '', os.path.join(os.path.dirname(__file__),'./PMDtools/'), os.path.join(os.path.dirname(__file__), './.data/')])
        printEndOfToolMessage('PMDtools')

    ##############################################
    # mapDamage ##################################
    ##############################################
    if args.mapDamage:
        printRunningMessage('MapDamage')

    ##############################################
    # mapDamage ##################################
    ##############################################
    if args.pyDamage:
        printRunningMessage('PyDamage')

    ##############################################
    # damageProfile ##############################
    ##############################################
    if args.damageProfile:
        printRunningMessage('DamageProfile')

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

    return

    # Run gargammel simulation
    subprocess.run([os.path.join(os.path.dirname(__file__),'./gargammel/gargammel.pl'), os.path.join(os.path.dirname(__file__), './.data/')])
    
    # Remove output dir if it exists
    subprocess.run(['rm', '-rf', args.output])
    # Create output
    subprocess.run(['mkdir', args.output])
    # Move files to output dir
    subprocess.run(['cp', os.path.join(os.path.dirname(__file__), './.data/simadna_s1.fq.gz'), os.path.join(args.output, 'simadna_s1.fq.gz')])
    subprocess.run(['cp', os.path.join(os.path.dirname(__file__), './.data/simadna_s2.fq.gz'), os.path.join(args.output, 'simadna_s2.fq.gz')])
    # Decompress files and delete previous compressed files
    subprocess.run(['gzip', '-d', '-q', '-f', os.path.join(args.output, 'simadna_s1.fq.gz')])
    subprocess.run(['gzip', '-d', '-q', '-f', os.path.join(args.output, 'simadna_s2.fq.gz')])


if __name__ == '__main__':
    main()