"""
Advanced 3D visualization service using RDKit and Three.js.
"""
import logging
import json
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
import networkx as nx
from scipy.spatial import distance

logger = logging.getLogger(__name__)

class MolecularVisualizer:
    def __init__(self):
        """Initialize the visualizer."""
        self.atom_colors = {
            'C': 0x808080,  # Gray
            'H': 0xFFFFFF,  # White
            'O': 0xFF0000,  # Red
            'N': 0x0000FF,  # Blue
            'S': 0xFFFF00,  # Yellow
            'P': 0xFFA500,  # Orange
            'F': 0x00FF00,  # Green
            'Cl': 0x00FF00,  # Green
            'Br': 0x800000,  # Dark Red
            'I': 0x800080   # Purple
        }
        
        self.atom_radii = {
            'C': 0.4,
            'H': 0.2,
            'O': 0.35,
            'N': 0.35,
            'S': 0.4,
            'P': 0.4,
            'F': 0.3,
            'Cl': 0.4,
            'Br': 0.45,
            'I': 0.5
        }

    def generate_3d_molecule(self, smiles):
        """
        Generate 3D structure from SMILES using RDKit.
        
        Args:
            smiles (str): SMILES representation of molecule
            
        Returns:
            dict: 3D molecular data for Three.js
        """
        try:
            # Create molecule from SMILES
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise ValueError("Invalid SMILES string")
            
            # Add hydrogens and generate 3D coordinates
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            
            # Get atom positions and properties
            conf = mol.GetConformer()
            atoms = []
            bonds = []
            
            # Process atoms
            for atom in mol.GetAtoms():
                pos = conf.GetAtomPosition(atom.GetIdx())
                element = atom.GetSymbol()
                atoms.append({
                    'element': element,
                    'position': [float(pos.x), float(pos.y), float(pos.z)],
                    'color': self.atom_colors.get(element, 0x808080),
                    'radius': self.atom_radii.get(element, 0.4)
                })
            
            # Process bonds
            for bond in mol.GetBonds():
                bonds.append({
                    'atom1': bond.GetBeginAtomIdx(),
                    'atom2': bond.GetEndAtomIdx(),
                    'order': bond.GetBondTypeAsDouble()
                })
            
            return {
                'atoms': atoms,
                'bonds': bonds,
                'center': self._calculate_center(atoms),
                'bounding_box': self._calculate_bounding_box(atoms)
            }
            
        except Exception as e:
            logger.error(f"Error generating 3D molecule: {str(e)}")
            raise

    def generate_nanoparticle(self, size_nm, surface_charge, coating):
        """
        Generate 3D nanoparticle representation.
        
        Args:
            size_nm (float): Nanoparticle size in nanometers
            surface_charge (float): Surface charge in mV
            coating (str): Coating material
            
        Returns:
            dict: Nanoparticle data for Three.js
        """
        try:
            # Scale size for visualization
            scale_factor = 0.1  # Adjust for better visualization
            radius = size_nm * scale_factor
            
            # Generate surface points
            points = self._generate_sphere_points(radius, 100)
            
            # Add surface properties
            surface_properties = {
                'charge': surface_charge,
                'coating': coating,
                'texture': self._get_coating_texture(coating)
            }
            
            return {
                'points': points,
                'radius': radius,
                'surface_properties': surface_properties,
                'center': [0, 0, 0]
            }
            
        except Exception as e:
            logger.error(f"Error generating nanoparticle: {str(e)}")
            raise

    def calculate_interactions(self, molecule_data, nanoparticle_data):
        """
        Calculate interaction points between molecule and nanoparticle.
        
        Args:
            molecule_data (dict): 3D molecular data
            nanoparticle_data (dict): Nanoparticle data
            
        Returns:
            dict: Interaction data
        """
        try:
            molecule_points = np.array([atom['position'] for atom in molecule_data['atoms']])
            nanoparticle_points = np.array(nanoparticle_data['points'])
            
            # Calculate distances
            distances = distance.cdist(molecule_points, nanoparticle_points)
            
            # Find interaction points
            interaction_threshold = nanoparticle_data['radius'] * 1.2
            interaction_points = []
            
            for i, atom_distances in enumerate(distances):
                min_dist = np.min(atom_distances)
                if min_dist < interaction_threshold:
                    closest_point = np.argmin(atom_distances)
                    interaction_points.append({
                        'atom_index': i,
                        'nanoparticle_point': closest_point,
                        'distance': float(min_dist)
                    })
            
            return {
                'points': interaction_points,
                'count': len(interaction_points),
                'average_distance': float(np.mean([p['distance'] for p in interaction_points]))
            }
            
        except Exception as e:
            logger.error(f"Error calculating interactions: {str(e)}")
            raise

    def _calculate_center(self, atoms):
        """Calculate molecule center."""
        positions = np.array([atom['position'] for atom in atoms])
        return list(np.mean(positions, axis=0))

    def _calculate_bounding_box(self, atoms):
        """Calculate molecule bounding box."""
        positions = np.array([atom['position'] for atom in atoms])
        return {
            'min': list(np.min(positions, axis=0)),
            'max': list(np.max(positions, axis=0))
        }

    def _generate_sphere_points(self, radius, num_points):
        """Generate points on a sphere surface."""
        points = []
        for i in range(num_points):
            phi = np.arccos(-1 + 2 * i / num_points)
            theta = np.sqrt(num_points * np.pi) * phi
            
            x = radius * np.cos(theta) * np.sin(phi)
            y = radius * np.sin(theta) * np.sin(phi)
            z = radius * np.cos(phi)
            
            points.append([float(x), float(y), float(z)])
        return points

    def _get_coating_texture(self, coating):
        """Get texture properties for coating material."""
        textures = {
            'PEG': {'roughness': 0.2, 'metalness': 0.1},
            'Chitosan': {'roughness': 0.4, 'metalness': 0.2},
            'PLA': {'roughness': 0.3, 'metalness': 0.1},
            'Lipid': {'roughness': 0.1, 'metalness': 0.3}
        }
        return textures.get(coating, {'roughness': 0.3, 'metalness': 0.2})

# Create global instance
molecular_visualizer = MolecularVisualizer() 