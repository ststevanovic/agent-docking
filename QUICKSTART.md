# Quick Start Guide - Molecular Docking MCP Tool

## What Was Implemented

This implementation adds comprehensive MCP (Model Context Protocol) tools for molecular docking with a user-friendly Gradio interface.

### New Features

1. **PDB Structure Fetching** (`utils.py: fetch_pdb`)
   - Fetches protein structures from RCSB PDB database
   - Validates PDB IDs
   - Returns PDB file content

2. **SMILES to PDBQT Conversion** (`utils.py: smiles_to_pdbqt`)
   - Converts SMILES strings to PDBQT format
   - Uses OpenBabel for conversion
   - Adds hydrogens and generates 3D coordinates

3. **MCP Server Tools** (`server.py`)
   - `fetch_pdb`: Fetch PDB structures via MCP
   - `smiles_to_pdbqt`: Convert SMILES via MCP
   - `dock_ligand`: Perform docking (existing, enhanced)

4. **Gradio UI Interface** (`ui.py`)
   - Tab 1: Fetch PDB structures by ID
   - Tab 2: Convert SMILES to PDBQT
   - Tab 3: Run molecular docking
   - Auto-fill coordinates from fetched structures
   - Interactive web interface

5. **Utility Functions** (`utils.py`)
   - `fetch_pdb()`: Fetch from RCSB
   - `smiles_to_pdbqt()`: SMILES conversion
   - `calculate_pdb_center()`: Calculate geometric center

### Files Created/Modified

```
mcp/
├── README.md                    # Comprehensive documentation
├── setup_env.sh                 # Environment setup script
├── requirements.txt             # Updated with requests dependency
└── src/
    ├── server.py                # Enhanced MCP server with new tools
    ├── utils.py                 # Utility functions (NEW)
    ├── ui.py                    # Gradio UI interface (NEW)
    ├── example.py               # Example usage scripts (NEW)
    └── test_utils.py            # Unit tests (NEW)
```

## Environment Setup

The implementation is on the `prod-testing` branch.

### Prerequisites

- Conda (Miniconda or Anaconda)
- Python 3.10+

### Installation Steps

```bash
# 1. Clone and switch to prod-testing branch
git checkout prod-testing

# 2. Navigate to mcp directory
cd mcp

# 3. Run setup script
chmod +x setup_env.sh
./setup_env.sh

# 4. Activate environment
conda activate docking-mcp
```

### Manual Installation

If the setup script doesn't work:

```bash
# Create environment
conda create -n docking-mcp python=3.10 -y
conda activate docking-mcp

# Install bioconda packages
conda install -c conda-forge -c bioconda smina openbabel -y

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### 1. Gradio UI Interface (Recommended for Testing)

```bash
cd src
python ui.py
```

Visit `http://localhost:7860` in your browser.

**Workflow:**
1. Tab 1: Enter PDB ID (e.g., `1HSG`) → Fetch → See coordinates
2. Tab 2: Enter SMILES (e.g., `CC(=O)OC1=CC=CC=C1C(=O)O`) → Convert
3. Tab 3: Adjust coordinates → Run Docking

### 2. MCP Server

```bash
cd src
python server.py
```

Use with MCP client to call:
- `fetch_pdb(pdb_id="1HSG")`
- `smiles_to_pdbqt(smiles="CC(=O)OC1=CC=CC=C1C(=O)O")`
- `dock_ligand(...)`

### 3. Command Line Examples

```bash
cd src
python example.py
```

This runs a complete workflow demonstration.

## Testing

### Unit Tests

```bash
cd src
pytest test_utils.py -v
```

Note: PDB fetching tests require internet access.

### Manual Testing

Test individual components:

```python
from utils import calculate_pdb_center

mock_pdb = """
ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  CA  ALA A   2      10.000   0.000   0.000  1.00  0.00           C
"""

center = calculate_pdb_center(mock_pdb)
print(center)  # {'x': 5.0, 'y': 0.0, 'z': 0.0}
```

## Example Use Cases

### Use Case 1: Drug Discovery Screening

```
1. Fetch target protein (e.g., 1HSG - HIV Protease)
2. Convert drug SMILES to PDBQT
3. Run docking to predict binding affinity
4. Analyze scores to rank compounds
```

### Use Case 2: Academic Research

```
1. Fetch multiple protein structures
2. Test various ligands via SMILES
3. Compare docking scores
4. Identify promising candidates
```

## Common PDB IDs for Testing

- **1HSG**: HIV-1 Protease (with inhibitor)
- **1UBQ**: Ubiquitin (small, fast)
- **3PBL**: Penicillin-binding protein
- **2ZFF**: EGFR kinase domain

## Common SMILES for Testing

- **Aspirin**: `CC(=O)OC1=CC=CC=C1C(=O)O`
- **Caffeine**: `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`
- **Ibuprofen**: `CC(C)CC1=CC=C(C=C1)C(C)C(=O)O`

## Architecture

```
User Interface (Gradio)
         ↓
    UI Module (ui.py)
         ↓
    Utilities (utils.py) ←→ MCP Server (server.py)
         ↓                          ↓
   [OpenBabel]                [Smina Docking]
         ↓                          ↓
   External Data                 Results
   (RCSB PDB)
```

## Troubleshooting

### Issue: "smina not found"
**Solution**: Install via conda:
```bash
conda install -c bioconda smina
```

### Issue: "obabel not found"
**Solution**: Install OpenBabel:
```bash
conda install -c conda-forge openbabel
```

### Issue: "Cannot fetch PDB"
**Solutions**:
- Check internet connection
- Verify PDB ID is valid (4 characters)
- Try accessing https://files.rcsb.org/download/[PDB_ID].pdb directly

### Issue: "Gradio not starting"
**Solution**: Ensure gradio is installed:
```bash
pip install gradio>=3.50.0
```

## Next Steps

1. Set up the conda environment using `setup_env.sh`
2. Test the UI with `python src/ui.py`
3. Try example workflow with `python src/example.py`
4. Explore MCP integration with the server

## Support

For issues or questions:
1. Check the main README.md in `/mcp/`
2. Review code examples in `src/example.py`
3. Run tests with `pytest src/test_utils.py`

## Branch Information

- **Branch**: `prod-testing`
- **Purpose**: Production testing environment
- **Status**: Ready for testing and deployment
