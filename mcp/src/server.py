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

if __name__ == "__main__":
    server = SminaDockingServer()
    server.run()
