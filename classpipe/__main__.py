from argparse import ArgumentParser, Namespace
from colorama import Fore, Back, Style
import subprocess
import os
from time import sleep

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
    parser.add_argument('--ref', help='Input reference DNA files')
    parser.add_argument('--seq1', help='Input aDNA file 1')
    parser.add_argument('--seq2', help='Input aDNA file 2 [Optional]', default=None)

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
    ref = args.ref
    seq1 = args.seq1
    seq2 = args.seq2
    
    # Create output dir if it doesn't exist
    output_dir = args.output
    if args.output == '.':
        output_dir = os.path.join(args.output, 'class_pipe_output')

    # Log files
    report_error_file_name = os.path.join(output_dir, 'report_stderr.txt')
    report_output_file_name = os.path.join(output_dir, 'report_stdout.txt')
    
    command = 'mkdir -p ' + output_dir
    subprocess.run(command, shell=True)
    
    # Clear temp data folder
    data_dir = os.path.join(os.path.dirname(__file__), '.data')
    command = 'rm ' + data_dir + '/* 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name
    subprocess.run(command, shell=True)
    
    # Define input file names
    input_sam_file_path = os.path.join(data_dir, 'DNA_input.sam')
    input_bam_file_path = os.path.join(data_dir, 'DNA_input.bam')        

    # Save BAM and BAI to output
    if args.saveBam:
        bam_dir = os.path.join(output_dir, 'BAM')
        subprocess.run(['mkdir', '-p', bam_dir])
        input_sam_file_path = os.path.join(bam_dir, 'DNA_input.sam')
        input_bam_file_path = os.path.join(bam_dir, 'DNA_input.bam')

    # Check if file DNA inputs are in a valid format 
    if args.seq1.endswith('.fq') or args.seq1.endswith('.fastq') or args.seq1.endswith('.fq.gz') or args.seq1.endswith('.fastq.gz'):
        # Convert reference DNA file (.fa) + aDNA files (.fq) to .sam format
        
        # 1. Create index (bowtie2)  
        # bowtie2-build ref.fa ref_index
        ref_index = os.path.join(data_dir, ref)
        command = 'bowtie2-build ' + ref + ' ' + ref_index + ' 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)

        # 2. Align fastq (bowtie2)
        # bowtie2 -x ref_index -U seq.fastq.gz -S seq.sam
        seq_sam_file_name = os.path.join(data_dir, 'seq.sam')
        
        # Check if single-ended/paired-ended        
        command = 'bowtie2 -x ' + ref_index + ' -U ' + seq1 + ' -S ' + seq_sam_file_name + ' 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name
        if args.seq2:
            command = 'bowtie2 -x ' + ref_index + ' -1 ' + seq1 + ' -2 ' + seq2 + ' -S ' + seq_sam_file_name + ' 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name
        subprocess.run(command, shell=True)
        
        # 3. Pass SAM to BAM (samtools view)
        # samtools view -bS $STUDY-data.sam > $STUDY-data.bam 2>> $REPORTS_DIR/report_stderr.txt
        seq_bam_file_name = os.path.join(data_dir, 'seq.bam')
        command = 'samtools view -b ' + seq_sam_file_name + ' > ' + seq_bam_file_name + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True) 

        # 4. Sort files (samtools sort)
        # samtools sort -n -o $STUDY-sorted-data.bam $STUDY-data-no-human.bam 1>> $REPORTS_DIR/report_stdout.txt 2>> $REPORTS_DIR/report_stderr.txt
        # printRunningMessage('Sorting BAM')
        # seq_bam_sorted_file_name = os.path.join(os.path.dirname(__file__), '.data/seq_sorted.bam')
        # command = 'samtools sort -n -o ' + seq_bam_sorted_file_name + ' ' + seq_bam_filtered_file_name + ' 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name
        # subprocess.run(command, shell=True)
    
        # Transform SAM to BAM
        # command = ''
        # subprocess.run(command, shell=True)
        # subprocess.run(['samtools', 'view', '-b', input_sam_file_path, '-o', input_bam_file_path])
        # subprocess.run(['rm', '-rf', input_sam_file_path])
    
    elif args.seq1.endswith('.bam') or args.seq1.endswith('.sam'):
        # Move .bam/.sam file to .data directory
        if args.seq1.endswith('.bam'):
            seq_bam_file_name = os.path.abspath(args.seq1)
        elif args.seq1.endswith('.sam'):
            seq_sam_file_name = os.path.abspath(args.seq1)
            subprocess.run(['samtools', 'view', '-b', seq_sam_file_name, '-o', seq_bam_file_name])
            subprocess.run(['rm', '-rf', seq_sam_file_name])
    else:
        message = 'Provide a valid format for the input DNA (.fq, .bam, .sam)'
        printErrorMessage(message)

    # Add MD tag
    printRunningMessage('Add MD tag')
    seq_bam_aligned_file_name = os.path.join(data_dir, 'seq_aligned.bam')
    command = 'samtools calmd -b ' + seq_bam_file_name + ' ' + ref + ' >> ' + seq_bam_aligned_file_name
    subprocess.run(command, shell=True)

    # Sort reads
    printRunningMessage('Sort reads')
    seq_bam_aligned_sorted_file_name = os.path.join(data_dir, 'seq_aligned_sorted.bam')
    command = 'samtools sort ' + seq_bam_aligned_file_name + ' -o ' + seq_bam_aligned_sorted_file_name
    subprocess.run(command, shell=True)
    
    # Index reads
    printRunningMessage('Indexing reads')
    seq_bam_index_file_name = os.path.join(data_dir, 'seq_aligned_sorted.bai')
    command = 'samtools index ' + seq_bam_aligned_sorted_file_name + ' ' + seq_bam_index_file_name
    subprocess.run(command, shell=True)
    
    ##############################################
    # PMDTools ###################################
    ##############################################
    if args.PMDtools:
        # Create
        PMDtools_output_dir_path = os.path.join(output_dir, 'PDMtools')

        # Remove PMDtools output dir if it exists
        command = 'rm -rf ' + PMDtools_output_dir_path
        subprocess.run(command, shell=True)
        # Create PMDtools output dir
        command = 'mkdir -p ' + PMDtools_output_dir_path
        subprocess.run(command, shell=True)

        # Create script to plot hist
        output_hist_script_pmdtools_file_name = os.path.join(PMDtools_output_dir_path, 'generate_hist.r')
        output_hist_script_pmdtools_file = open(output_hist_script_pmdtools_file_name, "w+")
        R_source_code = 'pmd_scores <- read.delim("' + PMDtools_output_dir_path + '/PMD_output.txt", header = FALSE, sep = "\t")\nhist_data <- hist(pmd_scores$V4, breaks = 1000, xlab = "PMDscores")\nplot(hist_data, main="Histogram of PMD Scores", xlab = "PMDscores", ylab = "Frequency")'
        output_hist_script_pmdtools_file.write(R_source_code)
        output_hist_script_pmdtools_file.close()

        # Create output file
        output_pmdtools_file_name = os.path.join(PMDtools_output_dir_path, 'PMD_output.txt')
        
        printRunningMessage('PMDtools')

        # Run PMDtools on input bam file
        command = 'samtools view -h ' + seq_bam_aligned_sorted_file_name + ' | python2 ' + os.path.join(os.path.dirname(__file__), 'PMDtools/pmdtools.0.60.py') + ' --printDS >> ' + output_pmdtools_file_name + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)

        # Draw hist
        command = 'Rscript ' + output_hist_script_pmdtools_file_name
        subprocess.run(command, shell=True)
        # Move hist to folder
        command = 'mv Rplots.pdf ' + PMDtools_output_dir_path
        subprocess.run(command, shell=True)
        
        printEndOfToolMessage('PMDtools')

    ##############################################
    # mapDamage ##################################
    ##############################################
    if args.mapDamage:
        # Create output dir
        mapDamage_output_dir_path = os.path.join(output_dir, 'mapDamage')
        # Remove mapDamage output dir if it exists
        command = 'rm -rf ' + mapDamage_output_dir_path + ' 2>> ' + report_error_file_name
        subprocess.run(command, shell=True)
        # Create mapDamage output dir
        command = 'mkdir -p ' + mapDamage_output_dir_path + ' 2>> ' + report_error_file_name
        subprocess.run(command, shell=True)

        printRunningMessage('mapDamage')

        # Run mapDamage on input sam file
        command = 'mapDamage -i ' + seq_bam_aligned_sorted_file_name + ' -r ' + ref + ' -d ' + mapDamage_output_dir_path + ' --merge-reference-sequences --no-stats 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)
        printEndOfToolMessage('mapDamage')

    ##############################################
    # pyDamage ###################################
    ##############################################
    if args.pyDamage:
        # Create output dir
        pyDamage_output_dir_path = os.path.join(output_dir, 'pyDamage')
        # Remove pyDamage output dir if it exists
        command = 'rm -rf ' + pyDamage_output_dir_path + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)
        # Create mapDamage output dir
        command = 'mkdir -p ' + pyDamage_output_dir_path + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)
        
        printRunningMessage('pyDamage')

        # Run pyDamage on input file
        command = 'yes Y | pydamage ' + ' --outdir ' + pyDamage_output_dir_path + ' analyze ' + seq_bam_aligned_sorted_file_name + ' --plot 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name
        subprocess.run(command, shell=True)

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
        command = 'java -jar ' + os.path.join(os.path.dirname(__file__), 'DamageProfiler/DamageProfiler-1.1-java11.jar') + ' -i ' + input_bam_file_path + ' -r ' + ref + ' -o ' + damageProfiler_output_dir_path + ' 1>> ' + report_output_file_name + ' 2>> ' + report_error_file_name 
        subprocess.run(command, shell=True)

    ##############################################
    # Atlas ######################################
    ##############################################
    if args.atlas:
        printRunningMessage('Atlas')
        # subprocess.run([os.path.join(os.path.dirname(__file__), './atlas/atlas'), '--help'])
        atlas_output_dir_path = os.path.join(output_dir, 'atlas')
        command = os.path.join(os.path.dirname(__file__), './atlas/atlas') + ' task=PMD' + ' bam=' + input_bam_file_path + ' fasta=' + args.ref + ' lenght=50' + ' out=' + atlas_output_dir_path
        subprocess.run(command, shell=True)
        # ./atlas task=PMD bam=example.bam fasta=reference.fa length=50
    
    ##############################################
    # metaDamage #################################
    ##############################################
    if args.metaDamage:
        printRunningMessage('MetaDamage')

    # Delete .data files
    command = 'rm ' + data_dir + '/*'
    subprocess.run(command, shell=True)
    # subprocess.run(['rm', '-rf', input_bam_aligned_file_path])
    
    printEndOfPipelineMessage()


if __name__ == '__main__':
    main()