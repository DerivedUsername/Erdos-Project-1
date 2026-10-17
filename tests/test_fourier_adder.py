import numpy as np
from qiskit.quantum_info import Operator

from erdos_project_1.fourier_adder import phi_add


def test_phi_add():
    m = 3
    a = 2
    dimension = 2**m

    # Independent Fourier matrix
    x = np.arange(dimension)
    F = np.exp(2j * np.pi * np.outer(x, x) / dimension)
    F /= np.sqrt(dimension)

    # Classical modular addition permutation matrix
    T = np.zeros((dimension, dimension), dtype=complex)

    for b in range(dimension):
        T[(b + a) % dimension, b] = 1

    # Expected Fourier-basis addition
    expected = F @ T @ F.conj().T

    actual = Operator(phi_add(a, m)).data

    assert np.allclose(actual, expected, atol=1e-10)