from model_context_protocol import MCPClient

async def test_docking():
    client = MCPClient()
    
    # Example usage with a receptor and ligand
    response = await client.call(
        "dock_ligand",
        {
            "receptor_pdb": "... PDB content ...",
            "ligand_pdbqt": "... PDBQT content ...",
            "center_x": 0.0,
            "center_y": 0.0,
            "center_z": 0.0,
            "size_x": 20.0,
            "size_y": 20.0,
            "size_z": 20.0,
            "exhaustiveness": 8
        }
    )
    
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Docking score: {response.outputs['score']}")
        print(f"All scores: {response.outputs['all_scores']}")
        print("Docked ligand structure:")
        print(response.outputs['docked_ligand'][:200] + "...")
