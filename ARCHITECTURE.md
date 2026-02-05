# Molecular Docking MCP Tool - Architecture & Workflow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interfaces                              │
├─────────────────────────────────────────────────────────────────┤
│  Gradio UI (ui.py)        │        MCP Client                   │
│  - Tab 1: Fetch PDB       │        - AI Agents                  │
│  - Tab 2: SMILES→PDBQT    │        - API Calls                  │
│  - Tab 3: Run Docking     │        - Automation                 │
└─────────────┬───────────────────────────┬───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Core Utilities (utils.py)                       │
├─────────────────────────────────────────────────────────────────┤
│  • fetch_pdb()           - Fetch from RCSB PDB                  │
│  • smiles_to_pdbqt()     - Convert SMILES using OpenBabel       │
│  • calculate_pdb_center() - Calculate geometric center          │
└─────────────┬────────────────────────────┬─────────────────────┘
              │                            │
              ▼                            ▼
┌────────────────────────┐    ┌──────────────────────────────────┐
│  MCP Server (server.py)│    │  External Tools & Services       │
├────────────────────────┤    ├──────────────────────────────────┤
│  MCP Tools:            │    │  • RCSB PDB Database             │
│  • fetch_pdb           │    │  • OpenBabel (obabel)            │
│  • smiles_to_pdbqt     │    │  • Smina Docking Engine          │
│  • dock_ligand         │    │                                  │
└────────────────────────┘    └──────────────────────────────────┘
```

## Workflow Diagrams

### Workflow 1: Complete Docking Pipeline (via UI)

```
┌──────────────┐
│ Start UI     │
│ python ui.py │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Tab 1: Fetch PDB Structure                  │
├─────────────────────────────────────────────┤
│ 1. Enter PDB ID (e.g., "1HSG")              │
│ 2. Click "Fetch PDB"                        │
│ 3. → fetch_pdb("1HSG")                      │
│ 4. → Download from files.rcsb.org           │
│ 5. ✓ Display PDB content                    │
│ 6. ✓ Calculate center (X, Y, Z)             │
│ 7. → Auto-fill to Tab 3                     │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Tab 2: Convert SMILES to PDBQT              │
├─────────────────────────────────────────────┤
│ 1. Enter SMILES (e.g., aspirin)             │
│ 2. Click "Convert to PDBQT"                 │
│ 3. → smiles_to_pdbqt(smiles)                │
│ 4. → OpenBabel: SMILES → PDB (3D)           │
│ 5. → OpenBabel: PDB → PDBQT                 │
│ 6. ✓ Display PDBQT content                  │
│ 7. → Auto-fill to Tab 3                     │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│ Tab 3: Run Docking                          │
├─────────────────────────────────────────────┤
│ 1. Verify receptor PDB                      │
│ 2. Verify ligand PDBQT                      │
│ 3. Check/adjust coordinates (X,Y,Z)         │
│ 4. Set box size (default: 20×20×20 Å)       │
│ 5. Set exhaustiveness (1-32, default: 8)    │
│ 6. Click "Run Docking"                      │
│ 7. → smina docking engine                   │
│ 8. ✓ Display docking scores                 │
│ 9. ✓ Display best pose PDBQT                │
└──────┬──────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│ Results:     │
│ • Scores     │
│ • Structures │
└──────────────┘
```

### Workflow 2: MCP Tool Integration

```
┌──────────────────┐
│ AI Agent / Client│
└────────┬─────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ MCP Server (server.py)                  │
├─────────────────────────────────────────┤
│                                         │
│  Tool 1: fetch_pdb                      │
│  ├─ Input: {"pdb_id": "1HSG"}          │
│  └─ Output: {pdb_content, center}      │
│                                         │
│  Tool 2: smiles_to_pdbqt                │
│  ├─ Input: {"smiles": "CC(=O)O..."}    │
│  └─ Output: {pdbqt_content}            │
│                                         │
│  Tool 3: dock_ligand                    │
│  ├─ Input: {receptor, ligand,          │
│  │          center_x/y/z, size_x/y/z}  │
│  └─ Output: {docked_ligand, scores}    │
│                                         │
└─────────────────────────────────────────┘
```

## Data Flow

### fetch_pdb Data Flow

```
PDB ID (e.g., "1HSG")
    ↓
[Validate: 4 chars, uppercase]
    ↓
https://files.rcsb.org/download/1HSG.pdb
    ↓
[HTTP GET Request]
    ↓
PDB File Content (text)
    ↓
[Parse ATOM/HETATM lines]
    ↓
Calculate Center: {x, y, z}
    ↓
Return: {pdb_content, pdb_id, center}
```

### smiles_to_pdbqt Data Flow

```
SMILES String (e.g., "CC(=O)OC1=CC=CC=C1C(=O)O")
    ↓
[Write to temp .smi file]
    ↓
obabel input.smi -O output.pdb --gen3d -h
    ↓
PDB with 3D coordinates + hydrogens
    ↓
obabel input.pdb -O output.pdbqt -xh
    ↓
PDBQT format (ready for docking)
    ↓
Return: {pdbqt_content}
```

### dock_ligand Data Flow

```
Inputs: receptor.pdb + ligand.pdbqt + parameters
    ↓
[Write temp files]
    ↓
smina --receptor receptor.pdb \
      --ligand ligand.pdbqt \
      --center_x X --center_y Y --center_z Z \
      --size_x SX --size_y SY --size_z SZ \
      --exhaustiveness E \
      --out output.pdbqt
    ↓
Docking calculation (Monte Carlo + local optimization)
    ↓
Multiple poses with affinity scores
    ↓
[Parse log file for scores]
    ↓
Return: {docked_ligand, score, all_scores}
```

## File Structure

```
agent-docking/
├── README.md                  # Main project README
├── QUICKSTART.md             # Quick start guide
├── LICENSE                   # License file
├── .gitignore               # Git ignore rules
└── mcp/                     # MCP tool directory
    ├── README.md            # Detailed MCP documentation
    ├── requirements.txt     # Python dependencies
    ├── setup_env.sh         # Environment setup script
    └── src/                 # Source code
        ├── server.py        # MCP server with 3 tools
        ├── utils.py         # Core utility functions
        ├── ui.py            # Gradio web interface
        ├── example.py       # Usage examples
        ├── test_utils.py    # Unit tests
        ├── test_client.py   # MCP client test
        └── initialize_rag.py # RAG initialization
```

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Programming language
- **Model Context Protocol SDK**: MCP integration
- **Gradio**: Web UI framework
- **Requests**: HTTP client for PDB fetching

### Bioinformatics Tools
- **Smina**: Molecular docking engine (fork of AutoDock Vina)
- **OpenBabel**: Chemical file format conversion
- **RCSB PDB**: Protein structure database

### Optional
- **LangChain**: RAG support
- **MongoDB Atlas**: Vector storage
- **OpenAI**: Embeddings

## Key Features

### 1. User-Friendly Interface
- No command-line knowledge required
- Visual feedback at each step
- Auto-fill between tabs
- Real-time status updates

### 2. MCP Integration
- AI agent accessible
- Programmatic control
- Batch processing support
- API-style usage

### 3. Robust Error Handling
- Input validation
- Detailed error messages
- Graceful fallbacks
- Status reporting

### 4. Flexible Configuration
- Adjustable search space
- Variable exhaustiveness
- Custom ligand names
- Multiple output formats

## Example Use Cases

### Research
1. Virtual screening of drug candidates
2. Protein-ligand binding prediction
3. Structure-based drug design
4. Academic teaching

### Industry
1. Lead compound optimization
2. Drug repurposing studies
3. Target validation
4. High-throughput screening

## Performance Considerations

### PDB Fetching
- Speed: ~1-2 seconds per structure
- Depends on: Internet speed, server load
- Caching: Not implemented (future enhancement)

### SMILES Conversion
- Speed: ~1-5 seconds per molecule
- Depends on: Molecule complexity
- Bottleneck: 3D coordinate generation

### Molecular Docking
- Speed: 30 seconds to 5 minutes
- Depends on: Exhaustiveness, search space
- Parallelization: Automatic (Smina default)

## Security & Privacy

- No data stored permanently
- Temporary files auto-deleted
- No external API keys required (except RAG features)
- Local execution (no cloud dependencies)

## Future Enhancements

Potential improvements:
- [ ] Local PDB caching
- [ ] Batch processing UI
- [ ] Visualization of docking results (3D)
- [ ] Results database/history
- [ ] Multiple conformer generation
- [ ] Ensemble docking support
- [ ] Integration with more docking engines
- [ ] Docker containerization
