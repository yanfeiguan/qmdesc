"""
This module defines the PathwayRankingHandler for use in Torchserve.
"""

import torch
from qmdesc.featurization import mol2graph, get_atom_fdim, get_bond_fdim
from rdkit import Chem


class ReactivityDescriptorHandler():

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model_pt_path = "QM_137k.pt"

        from qmdesc.model import MoleculeModel

        # Load model and args
        state = torch.load(model_pt_path, lambda storage, loc: storage)
        args, loaded_state_dict = state['args'], state['state_dict']
        atom_fdim = get_atom_fdim()
        bond_fdim = get_bond_fdim() + atom_fdim

        self.model = MoleculeModel(args, atom_fdim, bond_fdim)
        self.model.load_state_dict(loaded_state_dict)
        self.model.to(self.device)
        self.model.eval()

        self.initalized = True
        print('Model file {0} loaded successfully.'.format(model_pt_path))

    def preprocess(self, smiles):
        mol_graph = mol2graph(smiles)
        f_atoms, f_bonds, a2b, b2a, b2revb, a_scope, b_scope, b2br, bond_types = mol_graph.get_components()
        f_atoms, f_bonds, a2b, b2a, b2revb, b2br, bond_types = \
            f_atoms.to(self.device), f_bonds.to(self.device), a2b.to(self.device), b2a.to(self.device), \
            b2revb.to(self.device), b2br.to(self.device), bond_types.to(self.device)

        return f_atoms, f_bonds, a2b, b2a, b2revb, a_scope, b_scope, b2br, bond_types

    def inference(self, data):
        descs = self.model(data)

        return descs

    def postprocess(self, inference_output):

        smiles = inference_output['smiles']
        descs = inference_output['descs']

        descs = [x.data.cpu().numpy() for x in descs]

        partial_charge, partial_neu, partial_elec, NMR, bond_order, bond_distance = descs

        results = {'smiles': smiles, 'partial_charge': partial_charge, 'fukui_neu': partial_neu,
                    'fukui_elec': partial_elec, 'NMR': NMR, 'bond_order': bond_order, 'bond_length': bond_distance}
        return results

    def predict(self, smiles, sdf=None):

        outputs = self.inference(self.preprocess([smiles]))
        postprocess_inputs = {'smiles': smiles, 'descs': outputs}
        results = self.postprocess(postprocess_inputs)

        if sdf is not None:

            if not sdf.endswith('.sdf'):
                print('must provide a sdf name end up with \'.sdf\'')

            writer = Chem.SDWriter(sdf)
            m = Chem.MolFromSmiles(smiles)
            m = Chem.AddHs(m)

            for p in results:
                p_upper = p.upper()
                if p == 'smiles':
                    m.SetProp(p_upper, results[p])
                else:
                    m.SetProp(p_upper, ','.join(str(x) for x in results[p].flatten()))

            name = sdf.strip('.sdf')
            m.SetProp('_Name', name)

            writer.write(m)

        return results

if __name__ == '__main__':

    handler = ReactivityDescriptorHandler()
    result = handler.predict('C', 'test.sdf')
    print(result)

