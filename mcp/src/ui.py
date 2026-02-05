"""
Gradio UI for Molecular Docking with MCP integration.
"""
import gradio as gr
import asyncio
from utils import fetch_pdb, smiles_to_pdbqt, calculate_pdb_center
import subprocess
import tempfile
from pathlib import Path


def fetch_pdb_ui(pdb_id: str):
    """Fetch PDB structure and calculate center."""
    try:
        pdb_content = fetch_pdb(pdb_id)
        center = calculate_pdb_center(pdb_content)
        
        return (
            pdb_content,
            f"Successfully fetched PDB: {pdb_id.upper()}",
            center['x'],
            center['y'],
            center['z']
        )
    except Exception as e:
        return "", f"Error: {str(e)}", 0.0, 0.0, 0.0


def convert_smiles_ui(smiles: str, ligand_name: str = "ligand"):
    """Convert SMILES to PDBQT format."""
    try:
        pdbqt_content = smiles_to_pdbqt(smiles, ligand_name)
        return pdbqt_content, f"Successfully converted SMILES to PDBQT for {ligand_name}"
    except Exception as e:
        return "", f"Error: {str(e)}"


def run_docking(
    receptor_pdb: str,
    ligand_pdbqt: str,
    center_x: float,
    center_y: float,
    center_z: float,
    size_x: float,
    size_y: float,
    size_z: float,
    exhaustiveness: int
):
    """Run molecular docking with smina."""
    try:
        # Find smina executable
        result = subprocess.run(['which', 'smina'], capture_output=True, text=True)
        if result.returncode != 0:
            return "", "Error: smina executable not found. Please install via conda."
        
        smina_path = result.stdout.strip()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write input files
            receptor_path = Path(tmpdir) / "receptor.pdb"
            ligand_path = Path(tmpdir) / "ligand.pdbqt"
            output_path = Path(tmpdir) / "output.pdbqt"
            log_path = Path(tmpdir) / "log.txt"

            receptor_path.write_text(receptor_pdb)
            ligand_path.write_text(ligand_pdbqt)

            # Prepare smina command
            cmd = [
                smina_path,
                '--receptor', str(receptor_path),
                '--ligand', str(ligand_path),
                '--center_x', str(center_x),
                '--center_y', str(center_y),
                '--center_z', str(center_z),
                '--size_x', str(size_x),
                '--size_y', str(size_y),
                '--size_z', str(size_z),
                '--exhaustiveness', str(exhaustiveness),
                '--out', str(output_path),
                '--log', str(log_path)
            ]

            # Run docking
            process = subprocess.run(cmd, capture_output=True, text=True)

            if process.returncode != 0:
                return "", f"Docking failed: {process.stderr}"

            # Read results
            docked_ligand = output_path.read_text()
            log_content = log_path.read_text()
            
            # Parse scores from log
            scores = []
            for line in log_content.split('\n'):
                if 'Affinity:' in line:
                    try:
                        score = float(line.split()[1])
                        scores.append(score)
                    except (IndexError, ValueError):
                        continue

            result_text = f"Docking completed successfully!\n\n"
            if scores:
                result_text += f"Best Score: {scores[0]} kcal/mol\n"
                result_text += f"All Scores: {scores}\n\n"
            result_text += f"Output structure:\n{docked_ligand[:500]}..."

            return docked_ligand, result_text

    except Exception as e:
        return "", f"Error during docking: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Molecular Docking Interface") as demo:
    gr.Markdown("# Molecular Docking MCP Tool Interface")
    gr.Markdown("Fetch PDB structures, convert SMILES to PDBQT, and perform molecular docking.")
    
    with gr.Tab("1. Fetch PDB Structure"):
        gr.Markdown("### Fetch a protein structure from RCSB PDB")
        with gr.Row():
            pdb_id_input = gr.Textbox(
                label="PDB ID",
                placeholder="Enter 4-character PDB ID (e.g., 1HSG)",
                value="1HSG"
            )
            fetch_btn = gr.Button("Fetch PDB", variant="primary")
        
        fetch_status = gr.Textbox(label="Status", interactive=False)
        pdb_content_output = gr.Textbox(
            label="PDB Content",
            lines=10,
            interactive=False
        )
        
        gr.Markdown("### Calculated Center Coordinates")
        with gr.Row():
            center_x_output = gr.Number(label="Center X", interactive=False)
            center_y_output = gr.Number(label="Center Y", interactive=False)
            center_z_output = gr.Number(label="Center Z", interactive=False)
    
    with gr.Tab("2. Convert SMILES to PDBQT"):
        gr.Markdown("### Convert a SMILES string to PDBQT format")
        smiles_input = gr.Textbox(
            label="SMILES String",
            placeholder="Enter SMILES (e.g., CC(=O)OC1=CC=CC=C1C(=O)O for aspirin)",
            value="CC(=O)OC1=CC=CC=C1C(=O)O"
        )
        ligand_name_input = gr.Textbox(
            label="Ligand Name",
            value="ligand",
            placeholder="ligand"
        )
        convert_btn = gr.Button("Convert to PDBQT", variant="primary")
        
        convert_status = gr.Textbox(label="Status", interactive=False)
        pdbqt_content_output = gr.Textbox(
            label="PDBQT Content",
            lines=10,
            interactive=False
        )
    
    with gr.Tab("3. Run Docking"):
        gr.Markdown("### Configure and run molecular docking")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### Receptor (PDB)")
                receptor_input = gr.Textbox(
                    label="Receptor PDB Content",
                    lines=8,
                    placeholder="Paste PDB content or fetch from Tab 1"
                )
            
            with gr.Column():
                gr.Markdown("#### Ligand (PDBQT)")
                ligand_input = gr.Textbox(
                    label="Ligand PDBQT Content",
                    lines=8,
                    placeholder="Paste PDBQT content or convert from Tab 2"
                )
        
        gr.Markdown("#### Docking Box Configuration")
        with gr.Row():
            dock_center_x = gr.Number(label="Center X", value=0.0)
            dock_center_y = gr.Number(label="Center Y", value=0.0)
            dock_center_z = gr.Number(label="Center Z", value=0.0)
        
        with gr.Row():
            dock_size_x = gr.Number(label="Size X (Å)", value=20.0)
            dock_size_y = gr.Number(label="Size Y (Å)", value=20.0)
            dock_size_z = gr.Number(label="Size Z (Å)", value=20.0)
        
        exhaustiveness_input = gr.Slider(
            minimum=1,
            maximum=32,
            value=8,
            step=1,
            label="Exhaustiveness (higher = more thorough but slower)"
        )
        
        dock_btn = gr.Button("Run Docking", variant="primary")
        
        docking_status = gr.Textbox(label="Docking Results", lines=10, interactive=False)
        docked_output = gr.Textbox(
            label="Docked Structure (PDBQT)",
            lines=10,
            interactive=False
        )
    
    # Connect buttons to functions
    fetch_btn.click(
        fn=fetch_pdb_ui,
        inputs=[pdb_id_input],
        outputs=[pdb_content_output, fetch_status, center_x_output, center_y_output, center_z_output]
    )
    
    convert_btn.click(
        fn=convert_smiles_ui,
        inputs=[smiles_input, ligand_name_input],
        outputs=[pdbqt_content_output, convert_status]
    )
    
    dock_btn.click(
        fn=run_docking,
        inputs=[
            receptor_input,
            ligand_input,
            dock_center_x,
            dock_center_y,
            dock_center_z,
            dock_size_x,
            dock_size_y,
            dock_size_z,
            exhaustiveness_input
        ],
        outputs=[docked_output, docking_status]
    )
    
    # Add auto-fill functionality
    pdb_content_output.change(
        fn=lambda x: x,
        inputs=[pdb_content_output],
        outputs=[receptor_input]
    )
    
    pdbqt_content_output.change(
        fn=lambda x: x,
        inputs=[pdbqt_content_output],
        outputs=[ligand_input]
    )
    
    center_x_output.change(
        fn=lambda x: x,
        inputs=[center_x_output],
        outputs=[dock_center_x]
    )
    
    center_y_output.change(
        fn=lambda x: x,
        inputs=[center_y_output],
        outputs=[dock_center_y]
    )
    
    center_z_output.change(
        fn=lambda x: x,
        inputs=[center_z_output],
        outputs=[dock_center_z]
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
