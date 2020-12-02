.. qmdesc documentation master file, created by
   sphinx-quickstart on Tue Dec  1 10:29:07 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

qmdesc
======
`qmdesc <https://github.com/yanfeiguan/qmdesc>`_ is a package for QM atomic/bond descriptors prediction

At its core, qmdesc contains a derived `ChemProp <https://github.com/chemprop/chemprop>`_ model that was trained on QM descriptors including
hirshfeld partial charges, nucleophilicity/electrophilicity Fukui indcides, NMR shielding constants, bond lengths, and bond indices calculated under B3LYP/def2svp level of theory.
This work was first presented in `Regio-Selectivity Prediction with a Machine-Learned Reaction Representation and On-the-Fly Quantum Mechanical Descriptors <https://doi.org/10.26434/chemrxiv.12907316.v1>`_.

qmdesc can be used through either `python module <https://qmdesc.readthedocs.io/en/latest/qmdesc.html#qmdesc.handler.ReactivityDescriptorHandler>`_ or
`command line <https://qmdesc.readthedocs.io/en/latest/qmdesc.html#qmdesc.handler.qmdesc>`_

Prerequisite: `RDKit <https://anaconda.org/rdkit/rdkit>`_


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
