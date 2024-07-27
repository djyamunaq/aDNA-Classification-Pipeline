#!/bin/bash

# Stop script if any command fail
set -e

# Force sudo activation
sudo ls >> /dev/null 2>&1

# Remove temporary loading animation file if it exists
if [ -f "classpipe/temp" ] ; then
    sudo rm "classpipe/temp" >> /dev/null
fi

# Create temporary loading animation file
echo -e "#!/bin/bash\n\n"\$@" &\nwhile kill -0 \$!; do\n\tprintf '.' > /dev/tty\n\tsleep 1\ndone\nprintf '\\n' > /dev/tty" >> classpipe/temp
# Make script executable
chmod +x classpipe/temp

# Update packages
echo -n "> Updating packages "
sudo ./classpipe/temp apt update >> /dev/null 2>&1

# Install python 2
echo -n "> Install Python 2 "
sudo ./classpipe/temp apt install python2 >> /dev/null 2>&1

# Install samtools
echo -n "> Installing samtools "
sudo ./classpipe/temp sudo apt install samtools >> /dev/null 2>&1

# Install minimap2
echo -n "> Installing minimap2 "
# Repo version
    # cd ./classpipe/minimap2 >> /dev/null 2>&1
    # sudo ../temp make >>  /dev/null 2>&1
    # cd - >> /dev/null 2>&1
sudo ./classpipe/temp apt install minimap2 >> /dev/null 2>&1

# Install samtools
echo -n "> Installing pyDamage "
sudo ./classpipe/temp pip install pydamage >> /dev/null 2>&1

# Install atlas
echo -n "> Installing atlas "
# sudo ./classpipe/temp make ./classpipe/atlas/ >> /dev/null 2>&1
sudo ./classpipe/temp make ./classpipe/atlas/

# Install mapDamage
echo -n "> Installing mapDamage "
sudo ./classpipe/temp apt install mapdamage >> /dev/null 2>&1

# Update git submodules
echo -n "> Updating project modules "
sudo ./classpipe/temp git submodule update --init --recursive >> /dev/null 2>&1

# Pip install classpipe package
echo "> Installing classpipe"
if pip install -e .; then
    GREEN='\033[0;32m'
    echo -e "${GREEN}> Successfully installed package classpipe"
else
    RED='\033[0;31m'
    echo -e "${RED}> Failed installing package classpipe"
fi

# Reset terminal colors
WHITE="\033[0;37m"
echo -ne "${WHITE}"

# Remove temporary loading animation file
rm ./classpipe/temp

