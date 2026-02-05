"""
Example usage of the molecular docking MCP tools.
This script demonstrates the complete workflow from fetching PDB to docking.
"""
from utils import fetch_pdb, smiles_to_pdbqt, calculate_pdb_center
import subprocess
import tempfile
from pathlib import Path


def example_complete_workflow():
    """Demonstrate the complete docking workflow."""
    print("=" * 60)
    print("Molecular Docking MCP Tool - Example Workflow")
    print("=" * 60)
    print()
    
    # Step 1: Fetch PDB structure
    print("Step 1: Fetching PDB structure (1HSG - HIV Protease)...")
    pdb_id = "1HSG"
    try:
        pdb_content = fetch_pdb(pdb_id)
        print(f"✓ Successfully fetched PDB {pdb_id}")
        print(f"  PDB content length: {len(pdb_content)} characters")
    except Exception as e:
        print(f"✗ Error fetching PDB: {e}")
        return
    
    print()
    
    # Step 2: Calculate center coordinates
    print("Step 2: Calculating center coordinates...")
    try:
        center = calculate_pdb_center(pdb_content)
        print(f"✓ Center coordinates:")
        print(f"  X: {center['x']:.2f} Å")
        print(f"  Y: {center['y']:.2f} Å")
        print(f"  Z: {center['z']:.2f} Å")
    except Exception as e:
        print(f"✗ Error calculating center: {e}")
        return
    
    print()
    
    # Step 3: Convert SMILES to PDBQT
    print("Step 3: Converting SMILES to PDBQT (Aspirin)...")
    smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    ligand_name = "aspirin"
    try:
        pdbqt_content = smiles_to_pdbqt(smiles, ligand_name)
        print(f"✓ Successfully converted {ligand_name} to PDBQT")
        print(f"  PDBQT content length: {len(pdbqt_content)} characters")
    except Exception as e:
        print(f"✗ Error converting SMILES: {e}")
        return
    
    print()
    
    # Step 4: Run docking (optional - requires smina)
    print("Step 4: Running molecular docking...")
    try:
        # Check if smina is available
        result = subprocess.run(['which', 'smina'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠ Smina not found - skipping docking step")
            print("  Install with: conda install -c bioconda smina")
            return
        
        smina_path = result.stdout.strip()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write files
            receptor_path = Path(tmpdir) / "receptor.pdb"
            ligand_path = Path(tmpdir) / "ligand.pdbqt"
            output_path = Path(tmpdir) / "output.pdbqt"
            log_path = Path(tmpdir) / "log.txt"
            
            receptor_path.write_text(pdb_content)
            ligand_path.write_text(pdbqt_content)
            
            # Run smina
            cmd = [
                smina_path,
                '--receptor', str(receptor_path),
                '--ligand', str(ligand_path),
                '--center_x', str(center['x']),
                '--center_y', str(center['y']),
                '--center_z', str(center['z']),
                '--size_x', '20.0',
                '--size_y', '20.0',
                '--size_z', '20.0',
                '--exhaustiveness', '8',
                '--out', str(output_path),
                '--log', str(log_path)
            ]
            
            print(f"  Running docking at center ({center['x']:.1f}, {center['y']:.1f}, {center['z']:.1f})...")
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                print(f"✗ Docking failed: {process.stderr}")
                return
            
            # Parse results
            log_content = log_path.read_text()
            scores = []
            for line in log_content.split('\n'):
                if 'Affinity:' in line:
                    try:
                        score = float(line.split()[1])
                        scores.append(score)
                    except (IndexError, ValueError):
                        continue
            
            if scores:
                print(f"✓ Docking completed successfully!")
                print(f"  Best score: {scores[0]:.2f} kcal/mol")
                print(f"  Number of poses: {len(scores)}")
                print(f"  All scores: {[f'{s:.2f}' for s in scores]}")
            else:
                print("✓ Docking completed (no scores parsed)")
    
    except Exception as e:
        print(f"✗ Error during docking: {e}")
    
    print()
    print("=" * 60)
    print("Example workflow completed!")
    print("=" * 60)


def example_multiple_ligands():
    """Example of testing multiple ligands."""
    print("\nExample: Testing Multiple Ligands")
    print("-" * 60)
    
    ligands = {
        "aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "ibuprofen": "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O"
    }
    
    for name, smiles in ligands.items():
        print(f"\nConverting {name}...")
        try:
            pdbqt = smiles_to_pdbqt(smiles, name)
            print(f"✓ {name}: {len(pdbqt)} characters")
        except Exception as e:
            print(f"✗ {name}: {e}")


if __name__ == "__main__":
    # Run complete workflow
    example_complete_workflow()
    
    # Run multiple ligands example
    example_multiple_ligands()
    
    print("\n" + "=" * 60)
    print("To use the interactive UI, run: python ui.py")
    print("=" * 60)
