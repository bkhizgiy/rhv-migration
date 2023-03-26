#!/bin/bash

GREEN='\033[0;32m'
PUR='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${GREEN}-------Starting setting up the env for migration-------${NC}"
python create_secret.py
echo -e "${GREEN}1.-------Secret created-------${NC}"
python create_provider.py
echo -e "${GREEN}2.-------Provider created-------${NC}"
python python create_storage_mapping.py
echo -e "${GREEN}3.-------Storage mapping created-------${NC}"
python create_network_maping.py
echo -e "${GREEN}4.-------Network mapping created-------${NC}"
python create_plans.py
echo -e "${GREEN}5.-------Plans created-------${NC}"

echo -e "${PUR}Do you like to start the migration? [Y/n]${NC}"
read -r -e answer

if [[ "$answer" =~ [Yy] ]]; then
    python init_migration.py
    echo -e "${GREEN}6.-------migration started-------"
else
    echo "Oh well, see you next time!"
fi


