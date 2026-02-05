from typing import Dict, Any, Optional
from model_context_protocol import (
    MCPServer,
    Request,
    Response,
    register_function,
    ServerConfig,
)
import tempfile
import os
import subprocess
from pathlib import Path
from utils import fetch_pdb, smiles_to_pdbqt, calculate_pdb_center

class SminaDockingServer(MCPServer):
    def __init__(self, config: Optional[ServerConfig] = None):
        super().__init__(config)
        self.smina_path = self._find_smina()

    def _find_smina(self) -> str:
        """Find smina executable in conda environment."""
        try:
            result = subprocess.run(['which', 'smina'], 
                                 capture_output=True, 
                                 text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            raise FileNotFoundError("smina executable not found")
        except Exception as e:
            raise RuntimeError(f"Failed to locate smina: {str(e)}")

    @register_function("dock_ligand")
    async def dock_ligand(self, request: Request) -> Response:
        """
        Dock a ligand to a receptor using smina.
        
        Args:
            request.inputs:
                receptor_pdb: str - Content of the receptor PDB file
                ligand_pdbqt: str - Content of the ligand in PDBQT format
                center_x: float - X coordinate of the binding site
                center_y: float - Y coordinate of the binding site
                center_z: float - Z coordinate of the binding site
                size_x: float - Size of the search space in X dimension
                size_y: float - Size of the search space in Y dimension
                size_z: float - Size of the search space in Z dimension
                exhaustiveness: int - (optional) Exhaustiveness of the search (default: 8)
        
        Returns:
            dict containing:
                docked_ligand: str - PDBQT string of the best docked pose
                score: float - Docking score of the best pose
                all_scores: list - List of scores for all poses
        """
        inputs = request.inputs

        # Validate required inputs
        required_fields = ['receptor_pdb', 'ligand_pdbqt', 
                         'center_x', 'center_y', 'center_z',
                         'size_x', 'size_y', 'size_z']
        for field in required_fields:
            if field not in inputs:
                return Response(
                    error=f"Missing required input: {field}"
                )

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write input files
                receptor_path = Path(tmpdir) / "receptor.pdb"
                ligand_path = Path(tmpdir) / "ligand.pdbqt"
                output_path = Path(tmpdir) / "output.pdbqt"

                receptor_path.write_text(inputs['receptor_pdb'])
                ligand_path.write_text(inputs['ligand_pdbqt'])

                # Prepare smina command
                cmd = [
                    self.smina_path,
                    '--receptor', str(receptor_path),
                    '--ligand', str(ligand_path),
                    '--center_x', str(inputs['center_x']),
                    '--center_y', str(inputs['center_y']),
                    '--center_z', str(inputs['center_z']),
                    '--size_x', str(inputs['size_x']),
                    '--size_y', str(inputs['size_y']),
                    '--size_z', str(inputs['size_z']),
                    '--exhaustiveness', str(inputs.get('exhaustiveness', 8)),
                    '--out', str(output_path),
                    '--log', str(Path(tmpdir) / "log.txt")
                ]

                # Run docking
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )

                if process.returncode != 0:
                    return Response(
                        error=f"Docking failed: {process.stderr}"
                    )

                # Read results
                docked_ligand = output_path.read_text()
                log_content = (Path(tmpdir) / "log.txt").read_text()
                
                # Parse scores from log
                scores = []
                for line in log_content.split('\n'):
                    if line.startswith('Affinity:'):
                        scores.append(float(line.split()[1]))

                return Response(
                    outputs={
                        'docked_ligand': docked_ligand,
                        'score': scores[0] if scores else None,
                        'all_scores': scores
                    }
                )

        except Exception as e:
            return Response(
                error=f"Error during docking: {str(e)}"
            )

    @register_function("fetch_pdb")
    async def fetch_pdb_structure(self, request: Request) -> Response:
        """
        Fetch a PDB structure from the RCSB PDB database.
        
        Args:
            request.inputs:
                pdb_id: str - 4-character PDB identifier (e.g., '1HSG')
        
        Returns:
            dict containing:
                pdb_content: str - Content of the PDB file
                pdb_id: str - The PDB ID that was fetched
                center: dict - Geometric center coordinates (x, y, z)
        """
        inputs = request.inputs
        
        if 'pdb_id' not in inputs:
            return Response(
                error="Missing required input: pdb_id"
            )
        
        try:
            pdb_content = fetch_pdb(inputs['pdb_id'])
            center = calculate_pdb_center(pdb_content)
            
            return Response(
                outputs={
                    'pdb_content': pdb_content,
                    'pdb_id': inputs['pdb_id'].upper(),
                    'center': center
                }
            )
        except Exception as e:
            return Response(
                error=f"Error fetching PDB: {str(e)}"
            )

    @register_function("smiles_to_pdbqt")
    async def convert_smiles_to_pdbqt(self, request: Request) -> Response:
        """
        Convert a SMILES string to PDBQT format using OpenBabel.
        
        Args:
            request.inputs:
                smiles: str - SMILES string representation of the molecule
                ligand_name: str - (optional) Name for the ligand (default: "ligand")
        
        Returns:
            dict containing:
                pdbqt_content: str - Content of the PDBQT file
                smiles: str - The input SMILES string
                ligand_name: str - Name of the ligand
        """
        inputs = request.inputs
        
        if 'smiles' not in inputs:
            return Response(
                error="Missing required input: smiles"
            )
        
        try:
            ligand_name = inputs.get('ligand_name', 'ligand')
            pdbqt_content = smiles_to_pdbqt(inputs['smiles'], ligand_name)
            
            return Response(
                outputs={
                    'pdbqt_content': pdbqt_content,
                    'smiles': inputs['smiles'],
                    'ligand_name': ligand_name
                }
            )
        except Exception as e:
            return Response(
                error=f"Error converting SMILES to PDBQT: {str(e)}"
            )

if __name__ == "__main__":
    server = SminaDockingServer()
    server.run()
