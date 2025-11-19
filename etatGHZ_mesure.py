# %%
from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
for j in range(12):
    G.add_node(j, pos=(j % 4, -(j // 4)))

for j in range(0, 3):
    G.add_edge(j, j + 1)
    G.add_edge(j + 4, j + 5)
    G.add_edge(j + 8, j + 9)
G.add_edge(0, 4)
G.add_edge(4, 8)

# nx.draw(G,nx.get_node_attributes(G,'pos'),with_labels=True)
# nx.write_latex(G, "latex_graph.tex", pos=nx.get_node_attributes(G,'pos'), as_document=True)


def thetaGate(theta):
    qc = QuantumCircuit(1, 0, name="thetaGate")
    qc.rz(theta, 0)
    qc.h(0)
    return qc


# Get a fake backend from the fake provider
backend = GenericBackendV2(num_qubits=12, noise_info=False)

# Préparation de l'état initial
circuit = QuantumCircuit(12, 12)
for j in range(12):
    circuit.h(j)
for j, k in G.edges():
    # print(j,  " ", k)
    circuit.cz(j, k)
# # État cluster préparé

# ### Modifier sous cette ligne
# TODO, juste apliquer direct les angles de mesure
"""
Ligne 1
"""
# Qubit 0
# Mesure le qubit 0 dans la base theta = 0
circuit.compose(thetaGate(0), [0], inplace=True)
circuit.measure(0, 0)

# Qubit 1
circuit.compose(thetaGate(0), [1], inplace=True)
circuit.measure(1, 1)

# Qubit 2
circuit.compose(thetaGate(0), [2], inplace=True)
circuit.measure(2, 2)

# Qubit 3
### Correction dans l'ordre inverse
circuit.x(3).c_if(circuit.clbits[2], 1)
circuit.z(3).c_if(circuit.clbits[1], 1)
circuit.x(3).c_if(circuit.clbits[0], 1)

"""
Ligne 2
"""
# Qubit 4
circuit.compose(thetaGate(np.pi / 2), [4], inplace=True)
circuit.measure(4, 4)

# Qubit 5
### Faire la rz avant pour qu'elle soit du bon côté du H.
circuit.rz(-np.pi, 5).c_if(circuit.clbits[4], 1)
circuit.compose(thetaGate(np.pi / 2), [5], inplace=True)
circuit.measure(5, 5)

# Qubit 6
circuit.rz(-np.pi, 6).c_if(circuit.clbits[5], 1)
circuit.compose(thetaGate(np.pi / 2), [6], inplace=True)
circuit.measure(6, 6)

# Qubit 7
circuit.x(7).c_if(circuit.clbits[6], 1)
circuit.z(7).c_if(circuit.clbits[5], 1)
circuit.x(7).c_if(circuit.clbits[4], 1)

"""
Ligne 3
"""
# Qubit 8
# Mesure le qubit 0 dans la base theta = 0
circuit.compose(thetaGate(0), [8], inplace=True)
circuit.measure(8, 8)

# Qubit 9
circuit.compose(thetaGate(0), [9], inplace=True)
circuit.measure(9, 9)

# Qubit 10
circuit.compose(thetaGate(0), [10], inplace=True)
circuit.measure(10, 10)

# Qubit 11
circuit.x(11).c_if(circuit.clbits[10], 1)
circuit.z(11).c_if(circuit.clbits[9], 1)
circuit.x(11).c_if(circuit.clbits[8], 1)


print(circuit)
# TODO
### Modifier au dessus de cette ligne

# Transpile le circuit pour le backend
transpiled_circuit = transpile(circuit, backend, optimization_level=0)


# Observables pour l'état GHZ
observables_labels = ["XIIIXIIIXIII", "ZIIIIIIIZIII", "ZIIIZIIIIIII"]
observables = [SparsePauliOp(label) for label in observables_labels]
mapped_observables = [
    observable.apply_layout(transpiled_circuit.layout) for observable in observables
]

# Construit l'instance de l'estimateur et simule le circuit
estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 500
job = estimator.run([(transpiled_circuit, mapped_observables)])
pub_result = job.result()[0]

# %%
# Montre le résultat
values = pub_result.data.evs
plt.plot(observables_labels, values, "-o")
plt.xlabel("Observables")
plt.ylabel("Valeurs")
plt.show()
