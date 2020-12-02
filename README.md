# qmdesc

[![GitHub license](https://img.shields.io/github/license/yanfeiguan/qmdesc)](https://github.com/yanfeiguan/qmdesc/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/qmdesc/badge/?version=latest)](https://qmdesc.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/qmdesc.svg)](https://badge.fury.io/py/qmdesc)


A trained multitask constraint message passing neural networks 
for QM atomic/bond property predictions as described in the paper 
[Regio-Selectivity Prediction with a Machine-Learned Reaction Representation and On-the-Fly Quantum Mechanical Descriptors](https://doi.org/10.26434/chemrxiv.12907316.v1).

QM descriptors under B3LYP/def2svp level of theory that can be predicted with this model:
1. Hirshfeld partial charge
2. Neucleuphilic Fukui indices
3. Electrophilic Fukui indices
4. NMR shielding constants
5. Bond lengths
6. Bond orders

**Documentation:** Documentation of qmdesc is available at https://qmdesc.readthedocs.io/en/latest/index.html.

## Requirements

* RDKit

### Installation
For all installations, we recommend using conda to get the necessary rdkit dependency:
```console
conda install -c rdkit rdkit
pip install qmdesc
```

Or from envrioment.yml 
```console
conda create --name qmdesc --file environment.yml
```
