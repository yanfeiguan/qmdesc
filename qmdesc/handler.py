"""
This module defines the PathwayRankingHandler for use in Torchserve.
"""
from typing import Dict

import pkg_resources
import torch
from qmdesc.featurization import mol2graph, get_atom_fdim, get_bond_fdim
from rdkit import Chem

class ReactivityDescriptorHandler():
    '''Wrap the trained atom-bond qm descriptors predicting model

    Predict QM descriptors for a given SMILES string of organic compound containing C, H, O, N, P, S, F, Cl, Br, I, B

    Example:
            >>> from qmdesc import ReactivityDescriptorHandler
            >>> handler = ReactivityDescriptorHandler()
            >>> results = handler.predict('CCCC')
    '''

    def __init__(self):
        """
        ReactivityDescriptorHandler constructor.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model_pt_path = "QM_137k.pt"

        from qmdesc.model import MoleculeModel

        # Load model and args
        stream = pkg_resources.resource_stream(__name__, model_pt_path)
        state = torch.load(stream, lambda storage, loc: storage)
        args, loaded_state_dict = state['args'], state['state_dict']
        atom_fdim = get_atom_fdim()
        bond_fdim = get_bond_fdim() + atom_fdim

        self.model = MoleculeModel(args, atom_fdim, bond_fdim)
        self.model.load_state_dict(loaded_state_dict)
        self.model.to(self.device)
        self.model.eval()

        self.initalized = True

    def _preprocess(self, smiles: str):
        """
        Preprocess SMILES

        :param smiles: SMILES string
        :return: molecular graph
        """
        mol_graph = mol2graph(smiles)
        f_atoms, f_bonds, a2b, b2a, b2revb, a_scope, b_scope, b2br, bond_types = mol_graph.get_components()
        f_atoms, f_bonds, a2b, b2a, b2revb, b2br, bond_types = \
            f_atoms.to(self.device), f_bonds.to(self.device), a2b.to(self.device), b2a.to(self.device), \
            b2revb.to(self.device), b2br.to(self.device), bond_types.to(self.device)

        return f_atoms, f_bonds, a2b, b2a, b2revb, a_scope, b_scope, b2br, bond_types

    def _inference(self, data):
        """
        model prediction

        :param data: molecular graph
        :return: The output of the model
        """
        descs = self.model(data)

        return descs

    def _postprocess(self, inference_output) -> Dict:
        """
        Postprocess results

        :param inference_output: The output of the model
        :return: Results
        """

        smiles = inference_output['smiles']
        descs = inference_output['descs']

        descs = [x.data.cpu().numpy() for x in descs]

        partial_charge, partial_neu, partial_elec, NMR, bond_order, bond_distance = descs

        results = {'smiles': smiles, 'partial_charge': partial_charge.flatten(), 'fukui_neu': partial_neu.flatten(),
                   'fukui_elec': partial_elec.flatten(), 'NMR': NMR.flatten(), 'bond_order': bond_order.flatten(),
                   'bond_length': bond_distance.flatten()}
        return results

    def predict(self,
                smiles: str,
                sdf: str = None) -> Dict:
        """
        Wrap the preprocess, inference, and postprocess

        :param smiles: Input SMILES string
        :param sdf: Output .sdf file
        :return: A dictionary containing the prediction result
        """

        outputs = self._inference(self._preprocess([smiles]))
        postprocess_inputs = {'smiles': smiles, 'descs': outputs}
        results = self._postprocess(postprocess_inputs)

        if sdf is not None:
            if not sdf.endswith('.sdf'):
                print('must provide a sdf name end up with \'.sdf\'')
                return results

            writer = Chem.SDWriter(sdf)
            m = Chem.MolFromSmiles(smiles)
            m = Chem.AddHs(m)

            for p in results:
                p_upper = p.upper()
                if p == 'smiles':
                    m.SetProp(p_upper, results[p])
                else:
                    m.SetProp(p_upper, ','.join(str(x) for x in results[p]))

            name = sdf.strip('.sdf')
            m.SetProp('_Name', name)

            writer.write(m)

        return results

def qmdesc() -> None:
    """
    This is the entry point for the command line command :code:'qmdesc'

    Example:
       $ qmdesc CCCC --sdf CCCC.sdf
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('smiles', type=str,
                        help='Input smiles string')
    parser.add_argument('--sdf', default='qmdesc.sdf', type=str,
                        help='output sdf saving the qm descriptors')
    args = parser.parse_args()

    predictor = ReactivityDescriptorHandler()
    results = predictor.predict(args.smiles, sdf=args.sdf)


