#!/bin/bash

# Colors for better printing
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASE_DIR="${SCRIPT_DIR}"

echo -e "${RED}WARNING: This operation is NOT revertable.${NC}"
echo -e "${YELLOW}It will delete all '__pycache__' folders and 'django migrations' folders.${NC}"
echo -e "${BLUE}Are you sure you want to proceed? (yes/no): ${NC}"
read -r CONFIRMATION

if [[ ! "$CONFIRMATION" =~ ^[Yy][Ee][Ss]$ ]]; then
    echo -e "${GREEN}Operation cancelled. No files were deleted.${NC}"
    exit 0
fi

echo -e "${BLUE}--- Cleaning up ... ${BASE_DIR} ---${NC}"

echo -e "\n${YELLOW}>>> Deleting __pycache__ folders...${NC}"
find "${BASE_DIR}" -depth -name "__pycache__" -type d -print0 | while IFS= read -r -d $'\0' dir; do
    echo -e "${RED}  Deleting: ${dir}${NC}"
    rm -rf "${dir}"
done
echo -e "${GREEN}<<< __pycache__ deletion complete!${NC}"


echo -e "\n${YELLOW}>>> Deleting Django database migration folders...${NC}"

find "${BASE_DIR}" -name "migrations" -type d -not -path "${BASE_DIR}/migrations" -print0 | while IFS= read -r -d $'\0' migrations_dir; do
    if [ -f "${migrations_dir}/__init__.py" ]; then
        echo -e "${RED}  Deleting: ${migrations_dir}${NC}"
        rm -rf "${migrations_dir}"
    else
        echo -e "${BLUE}  Skipping non-Django migrations folder: ${migrations_dir} (no __init__.py found)${NC}"
    fi
done
echo -e "${GREEN}<<< Django migration folders deletion complete!${NC}"