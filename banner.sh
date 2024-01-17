#!/bin/bash

# Function to display PC-to-PC connection ASCII art
display_pc_connection() {
    echo -e "\033[1;34m"
    echo "     ________          ________"
    echo "    |        |        |        |"
    echo "    |        |        |        |"
    echo "    |        |--------|        |"
    echo "    |________|   ssh  |________|"
    echo -e "\033[0m"

}

# Windows with WSL
if [ "$OSTYPE" = "msys" ]; then
    display_pc_connection
# Linux
else
    display_pc_connection
fi
