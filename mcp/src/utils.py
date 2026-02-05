"""Utility functions for molecular docking operations."""
import requests
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


def fetch_pdb(pdb_id: str) -> str:
    """
    Fetch PDB file from RCSB PDB database.
    
    Args:
        pdb_id: 4-character PDB identifier (e.g., '1HSG')
    
    Returns:
        str: Content of the PDB file
        
    Raises:
        ValueError: If PDB ID is invalid
        RuntimeError: If fetching fails
    """
    # Validate PDB ID format
    pdb_id = pdb_id.strip().upper()
    if len(pdb_id) != 4:
        raise ValueError(f"Invalid PDB ID: {pdb_id}. Must be 4 characters.")
    
    # Fetch from RCSB PDB
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if "not found" in response.text.lower() or len(response.text) < 100:
            raise ValueError(f"PDB ID {pdb_id} not found in RCSB database")
            
        return response.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch PDB {pdb_id}: {str(e)}")


def smiles_to_pdbqt(smiles: str, output_name: str = "ligand") -> str:
    """
    Convert SMILES string to PDBQT format using OpenBabel.
    
    Args:
        smiles: SMILES string representation of the molecule
        output_name: Name for the output molecule (default: "ligand")
    
    Returns:
        str: Content of the PDBQT file
        
    Raises:
        RuntimeError: If conversion fails
    """
    if not smiles or not smiles.strip():
        raise ValueError("SMILES string cannot be empty")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create paths
            smi_path = Path(tmpdir) / f"{output_name}.smi"
            pdb_path = Path(tmpdir) / f"{output_name}.pdb"
            pdbqt_path = Path(tmpdir) / f"{output_name}.pdbqt"
            
            # Write SMILES to file
            smi_path.write_text(smiles.strip())
            
            # Step 1: Convert SMILES to PDB with 3D coordinates using OpenBabel
            cmd_to_pdb = [
                'obabel',
                str(smi_path),
                '-O', str(pdb_path),
                '--gen3d',  # Generate 3D coordinates
                '-h'  # Add hydrogens
            ]
            
            result = subprocess.run(
                cmd_to_pdb,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"OpenBabel SMILES to PDB conversion failed: {result.stderr}")
            
            if not pdb_path.exists() or pdb_path.stat().st_size == 0:
                raise RuntimeError("OpenBabel produced empty PDB file")
            
            # Step 2: Convert PDB to PDBQT using OpenBabel
            cmd_to_pdbqt = [
                'obabel',
                str(pdb_path),
                '-O', str(pdbqt_path),
                '-xh'  # Add hydrogens and partial charges
            ]
            
            result = subprocess.run(
                cmd_to_pdbqt,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"OpenBabel PDB to PDBQT conversion failed: {result.stderr}")
            
            if not pdbqt_path.exists() or pdbqt_path.stat().st_size == 0:
                raise RuntimeError("OpenBabel produced empty PDBQT file")
            
            # Read and return PDBQT content
            pdbqt_content = pdbqt_path.read_text()
            return pdbqt_content
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"OpenBabel execution failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error during SMILES to PDBQT conversion: {str(e)}")


def calculate_pdb_center(pdb_content: str) -> Dict[str, float]:
    """
    Calculate the geometric center of a PDB structure.
    
    Args:
        pdb_content: Content of the PDB file
    
    Returns:
        dict: Dictionary with 'x', 'y', 'z' coordinates
    """
    x_coords = []
    y_coords = []
    z_coords = []
    
    for line in pdb_content.split('\n'):
        if line.startswith('ATOM') or line.startswith('HETATM'):
            try:
                # PDB format: columns 31-38 (x), 39-46 (y), 47-54 (z)
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                x_coords.append(x)
                y_coords.append(y)
                z_coords.append(z)
            except (ValueError, IndexError):
                continue
    
    if not x_coords:
        raise ValueError("No valid coordinates found in PDB file")
    
    return {
        'x': sum(x_coords) / len(x_coords),
        'y': sum(y_coords) / len(y_coords),
        'z': sum(z_coords) / len(z_coords)
    }
