# Agentic Docking Assistant – MCP Tool

A comprehensive Model Context Protocol (MCP) tool for molecular docking operations with an integrated Gradio UI interface.

## Features

- **PDB Structure Fetching**: Automatically fetch protein structures from RCSB PDB database
- **SMILES to PDBQT Conversion**: Convert molecular SMILES strings to PDBQT format using OpenBabel
- **Molecular Docking**: Perform protein-ligand docking using Smina
- **Interactive UI**: User-friendly Gradio web interface for all operations
- **MCP Integration**: Full MCP tool support for AI agent integration

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup and usage instructions.

### Installation

```bash
cd mcp
chmod +x setup_env.sh
./setup_env.sh
conda activate docking-mcp
```

### Run the UI

```bash
cd mcp/src
python ui.py
```

Visit `http://localhost:7860` to access the interface.

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide and troubleshooting
- [mcp/README.md](mcp/README.md) - Comprehensive documentation with examples

## Branch Information

- **prod-testing**: Production testing branch with latest features
- All development work is on this branch

## License

See [LICENSE](LICENSE) file for details.

