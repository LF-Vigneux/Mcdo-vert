# %%
from qiskit import QuantumCircuit
from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp,Statevector
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit_ibm_runtime import EstimatorV2 as Estimator
import numpy as np

import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
for j in range(12):
    G.add_node(j,pos=(j%4,-(j//4)))

for j in range(0,3):
    G.add_edge(j, j+1)
    G.add_edge(j+4, j+5)
    G.add_edge(j+8, j+9)
G.add_edge(0,4)
G.add_edge(4,8)

# nx.draw(G,nx.get_node_attributes(G,'pos'),with_labels=True)
# nx.write_latex(G, "latex_graph.tex", pos=nx.get_node_attributes(G,'pos'), as_document=True)
 
def thetaGate(theta):
    qc = QuantumCircuit(1,0, name='thetaGate')
    qc.rz(theta,0)
    qc.h(0)
    return qc

# Get a fake backend from the fake provider
backend = GenericBackendV2(num_qubits=12,noise_info=False)
 
# Préparation de l'état initial
circuit = QuantumCircuit(12,12)
for j in range(12):
    circuit.h(j)
for j,k in G.edges():
    # print(j,  " ", k)
    circuit.cz(j,k)
# # État cluster préparé

# ### Modifier sous cette ligne 
# Mesure le qubit 0 dans la base theta = 0 
circuit.compose(thetaGate(0),[0],inplace=True)
circuit.measure(0,0)

# Mesure le qubit 1 dans la base theta1 = 0.1
theta1 = 0.1
circuit.rz(-2*theta1,1).c_if(circuit.clbits[0],1)
circuit.compose(thetaGate(theta1),[1],inplace=True)
circuit.measure(1,1)

print(circuit)
### Modifier au dessus de cette ligne

# Transpile le circuit pour le backend
transpiled_circuit = transpile(circuit, backend,optimization_level=0)


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
