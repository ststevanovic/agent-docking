# Molecular Docking MCP Tool

An MCP (Model Context Protocol) tool for molecular docking operations with an integrated Gradio UI interface.

## Features

- **PDB Structure Fetching**: Fetch protein structures directly from RCSB PDB database
- **SMILES to PDBQT Conversion**: Convert SMILES strings to PDBQT format using OpenBabel
- **Molecular Docking**: Perform molecular docking using Smina
- **Interactive UI**: User-friendly Gradio interface for all operations
- **MCP Integration**: Accessible as MCP tools for AI agents

## Installation

### Prerequisites

- [Conda](https://docs.conda.io/en/latest/miniconda.html) (Miniconda or Anaconda)
- Python 3.10 or higher

### Quick Setup

```bash
cd mcp
chmod +x setup_env.sh
./setup_env.sh
```

### Manual Setup

1. Create and activate conda environment:
```bash
conda create -n docking-mcp python=3.10
conda activate docking-mcp
```

2. Install bioconda packages:
```bash
conda install -c conda-forge -c bioconda smina openbabel
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Gradio UI Interface

Start the interactive web interface:

```bash
conda activate docking-mcp
cd src
python ui.py
```

The interface will be available at `http://localhost:7860`

#### UI Workflow:

1. **Tab 1 - Fetch PDB Structure**:
   - Enter a 4-character PDB ID (e.g., `1HSG` for HIV protease)
   - Click "Fetch PDB"
   - View the structure and calculated center coordinates
   - Content automatically transfers to the docking tab

2. **Tab 2 - Convert SMILES to PDBQT**:
   - Enter a SMILES string (e.g., `CC(=O)OC1=CC=CC=C1C(=O)O` for aspirin)
   - Provide a ligand name (optional)
   - Click "Convert to PDBQT"
   - Content automatically transfers to the docking tab

3. **Tab 3 - Run Docking**:
   - Verify receptor (PDB) and ligand (PDBQT) content
   - Adjust docking box center coordinates (X, Y, Z)
   - Set docking box size (default: 20x20x20 Å)
   - Adjust exhaustiveness (1-32, default: 8)
   - Click "Run Docking"
   - View results and docking scores

### MCP Server

Start the MCP server:

```bash
conda activate docking-mcp
cd src
python server.py
```

#### Available MCP Tools:

1. **fetch_pdb**
   - Fetch PDB structure from RCSB database
   - Input: `pdb_id` (string)
   - Output: `pdb_content`, `pdb_id`, `center` coordinates

2. **smiles_to_pdbqt**
   - Convert SMILES to PDBQT format
   - Input: `smiles` (string), `ligand_name` (optional string)
   - Output: `pdbqt_content`, `smiles`, `ligand_name`

3. **dock_ligand**
   - Perform molecular docking
   - Inputs: `receptor_pdb`, `ligand_pdbqt`, `center_x/y/z`, `size_x/y/z`, `exhaustiveness`
   - Output: `docked_ligand`, `score`, `all_scores`

## Examples

### Example 1: Docking Aspirin to HIV Protease

```python
# Using the UI:
# 1. Fetch PDB: 1HSG
# 2. Convert SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
# 3. Use auto-filled coordinates and run docking
```

### Example 2: Using MCP Tools

```python
from model_context_protocol import MCPClient

client = MCPClient()

# Fetch PDB
pdb_response = await client.call("fetch_pdb", {"pdb_id": "1HSG"})

# Convert SMILES
ligand_response = await client.call("smiles_to_pdbqt", {
    "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "ligand_name": "aspirin"
})

# Run docking
dock_response = await client.call("dock_ligand", {
    "receptor_pdb": pdb_response.outputs['pdb_content'],
    "ligand_pdbqt": ligand_response.outputs['pdbqt_content'],
    "center_x": pdb_response.outputs['center']['x'],
    "center_y": pdb_response.outputs['center']['y'],
    "center_z": pdb_response.outputs['center']['z'],
    "size_x": 20.0,
    "size_y": 20.0,
    "size_z": 20.0,
    "exhaustiveness": 8
})

print(f"Docking score: {dock_response.outputs['score']} kcal/mol")
```

## Common PDB IDs for Testing

- `1HSG`: HIV-1 protease
- `3PBL`: Penicillin-binding protein
- `1UYD`: Lysozyme
- `2ZFF`: Epidermal growth factor receptor
- `4HHB`: Hemoglobin

## Common SMILES Strings for Testing

- Aspirin: `CC(=O)OC1=CC=CC=C1C(=O)O`
- Caffeine: `CN1C=NC2=C1C(=O)N(C(=O)N2C)C`
- Ibuprofen: `CC(C)CC1=CC=C(C=C1)C(C)C(=O)O`
- Paracetamol: `CC(=O)NC1=CC=C(C=C1)O`

## Troubleshooting

### Smina not found
- Ensure conda environment is activated: `conda activate docking-mcp`
- Reinstall smina: `conda install -c bioconda smina`

### OpenBabel conversion fails
- Check OpenBabel installation: `obabel --version`
- Reinstall: `conda install -c conda-forge openbabel`

### PDB fetch fails
- Check internet connection
- Verify PDB ID is correct (4 characters)
- Try accessing directly: `https://files.rcsb.org/download/[PDB_ID].pdb`

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Linting

```bash
flake8 src/
```

## License

See LICENSE file in the repository root.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.
