import numpy as np
import pytest
from qiskit.quantum_info import Operator

from erdos_project_1.fourier_adder import phi_add


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("a", [-3, 0, 1, 2, 7])
def test_phi_add(n: int, a: int):
    """Verify Fourier addition against classical modular addition."""
    m = n + 1
    M = 2**m

    # Construct the QFT matrix independently
    x = np.arange(M)
    F = np.exp(2j * np.pi * np.outer(x, x) / M) / np.sqrt(M)

    # Construct classical modular addition as a permutation matrix
    T = np.zeros((M, M), dtype=complex)

    for b in range(M):
        T[(a + b) % M, b] = 1

    # Mathematical reference: A_a = F T_a F^{-1}
    expected = F @ T @ F.conj().T

    # Actual circuit matrix
    actual = Operator(phi_add(a, m)).data

    # Compare complete unitaries, including phases
    assert np.allclose(actual, expected, atol=1e-10, rtol=0)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("a", [-3, 0, 1, 2, 7])
def test_inverse_phi_add(n: int, a: int):
    """Verify that subtraction by a undoes addition by a."""
    m = n + 1
    M = 2**m

    adder = Operator(phi_add(a, m)).data
    inverse = Operator(phi_add(-a, m)).data

    # A_{-a} A_a = I
    identity = np.eye(M, dtype=complex)

    assert np.allclose(inverse @ adder, identity, atol=1e-10, rtol=0)
