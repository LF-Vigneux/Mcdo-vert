# %%
from qiskit import QuantumCircuit
from qiskit import QuantumRegister
import matplotlib.pyplot as plt

# %%
qr = QuantumRegister(3, name='|0>')
qc_i = QuantumCircuit(qr)

qc_i.h(1)
qc_i.cx(1, 0)
qc_i.cx(1, 2)

fig = qc_i.draw(output='mpl')
fig.savefig("circuit_init.pdf", bbox_inches='tight')

plt.clf()
# %%
qr = QuantumRegister(3, name="|0>")
qc_2 = QuantumCircuit(qr)

qc_2.h(1)
qc_2.h(0)
qc_2.cz(1,0)
qc_2.h(0)
qc_2.h(2)
qc_2.cz(1,2)
qc_2.h(2)

fig = qc_2.draw(output='mpl')
fig.savefig("circuit_2.pdf", bbox_inches='tight')

plt.clf()

# %%

qr = QuantumRegister(3, name="|+>")
qc_2 = QuantumCircuit(qr)



qc_2.cz(1,0)
qc_2.h(0)

qc_2.cz(1,2)
qc_2.h(2)

fig = qc_2.draw(output='mpl')
fig.savefig("circuit_2_+.pdf", bbox_inches='tight')

plt.clf()


# %%
