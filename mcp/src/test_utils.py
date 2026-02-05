"""
Tests for molecular docking utilities.
"""
import pytest
from utils import fetch_pdb, smiles_to_pdbqt, calculate_pdb_center


def test_fetch_pdb_valid():
    """Test fetching a valid PDB structure."""
    # Fetch a small PDB structure (1UBQ - ubiquitin, 76 residues)
    pdb_content = fetch_pdb("1UBQ")
    
    assert pdb_content is not None
    assert len(pdb_content) > 100
    assert "ATOM" in pdb_content
    assert "1UBQ" in pdb_content.upper() or "HEADER" in pdb_content


def test_fetch_pdb_invalid():
    """Test fetching an invalid PDB ID."""
    with pytest.raises(ValueError):
        fetch_pdb("INVALID123")  # Too long
    
    with pytest.raises((ValueError, RuntimeError)):
        fetch_pdb("XXXX")  # Non-existent


def test_calculate_pdb_center():
    """Test calculating center coordinates from PDB."""
    # Simple PDB with known coordinates
    sample_pdb = """
ATOM      1  CA  ALA A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  CA  ALA A   2      10.000   0.000   0.000  1.00  0.00           C
ATOM      3  CA  ALA A   3       0.000  10.000   0.000  1.00  0.00           C
ATOM      4  CA  ALA A   4       0.000   0.000  10.000  1.00  0.00           C
END
"""
    center = calculate_pdb_center(sample_pdb)
    
    # Center should be approximately (2.5, 2.5, 2.5)
    assert 'x' in center and 'y' in center and 'z' in center
    assert abs(center['x'] - 2.5) < 0.1
    assert abs(center['y'] - 2.5) < 0.1
    assert abs(center['z'] - 2.5) < 0.1


def test_smiles_to_pdbqt_valid():
    """Test converting a valid SMILES string to PDBQT."""
    # Simple molecule: methane
    smiles = "C"
    pdbqt_content = smiles_to_pdbqt(smiles, "methane")
    
    assert pdbqt_content is not None
    assert len(pdbqt_content) > 0
    assert "ATOM" in pdbqt_content or "HETATM" in pdbqt_content


def test_smiles_to_pdbqt_complex():
    """Test converting a complex SMILES string (aspirin)."""
    smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    pdbqt_content = smiles_to_pdbqt(smiles, "aspirin")
    
    assert pdbqt_content is not None
    assert len(pdbqt_content) > 100  # Should have multiple atoms
    assert "ATOM" in pdbqt_content or "HETATM" in pdbqt_content


def test_smiles_to_pdbqt_empty():
    """Test that empty SMILES raises an error."""
    with pytest.raises(ValueError):
        smiles_to_pdbqt("", "empty")
    
    with pytest.raises(ValueError):
        smiles_to_pdbqt("   ", "whitespace")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
