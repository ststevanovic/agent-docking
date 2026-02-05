#!/bin/bash
# Setup script for Molecular Docking MCP Tool Environment

echo "========================================="
echo "Molecular Docking MCP Tool Setup"
echo "========================================="
echo ""

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Miniconda or Anaconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Step 1: Creating conda environment 'docking-mcp'..."
conda create -n docking-mcp python=3.10 -y

echo ""
echo "Step 2: Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate docking-mcp

echo ""
echo "Step 3: Installing bioconda packages (smina, openbabel)..."
conda install -c conda-forge -c bioconda smina openbabel -y

echo ""
echo "Step 4: Installing Python dependencies..."
cd "$(dirname "$0")"
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To activate the environment, run:"
echo "  conda activate docking-mcp"
echo ""
echo "To start the Gradio UI, run:"
echo "  python src/ui.py"
echo ""
echo "To start the MCP server, run:"
echo "  python src/server.py"
echo ""
