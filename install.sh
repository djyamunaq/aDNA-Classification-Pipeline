rm ./src/temp >> /dev/null 2>&1
echo -e "#!/bin/bash\n\n"\$@" &\nwhile kill -0 \$!; do\n\tprintf '.' > /dev/tty\n\tsleep 1\ndone\nprintf '\\n' > /dev/tty" >> src/temp
echo -n "> Updating packages "
sudo ./src/temp apt update >> /dev/null 2>&1
echo -n "> Installing samtools "
sudo ./src/temp sudo apt install samtools >> /dev/null 2>&1
echo -n "> Installing minimap2 "
cd ./src/minimap2 >> /dev/null 2>&1
sudo ../temp make >>  /dev/null 2>&1
cd - >> /dev/null 2>&1
echo -n "> Updating project modules "
sudo ./src/temp git submodule update --init --recursive >> /dev/null 2>&1
echo -n "> Installing classpipe "
sudo ./src/temp pip install -e . >> /dev/null 2>&1
GREEN='\033[0;32m'
echo -e "${GREEN}> Successfully installed package classpipe"
rm ./src/temp

