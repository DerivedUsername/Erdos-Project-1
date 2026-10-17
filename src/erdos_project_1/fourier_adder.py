from math import pi

from qiskit import QuantumCircuit


def phi_add(a: int, num_qubits: int) -> QuantumCircuit:
    """
    Construct Fourier-space addition of a classical integer.

    Acts on a Fourier-encoded register of num_qubits qubits.

    |phi(b)> -> |phi((a + b) mod 2**num_qubits)>

    Register convention: q[0] is the least significant bit.
    """
    qc = QuantumCircuit(num_qubits)
    for j in range(num_qubits):
        theta = 2 * pi * a / (2 ** (num_qubits - j))
        qc.p(theta, j)
    return qc
