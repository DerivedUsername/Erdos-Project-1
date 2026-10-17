from math import gcd

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from erdos_project_1.modular_multiplier import controlled_modular_multiply

N = 15
N_QUBITS = (N - 1).bit_length()
TOTAL_QUBITS = 2 * N_QUBITS + 4

VALID_MULTIPLIERS = [a for a in range(1, N) if gcd(a, N) == 1]


def basis_input(c: int, x: int) -> QuantumCircuit:
    """Prepare control and input registers, with clean ancillas."""
    qc = QuantumCircuit(TOTAL_QUBITS)

    if c:
        qc.x(0)

    for j in range(N_QUBITS):
        if (x >> j) & 1:
            qc.x(1 + j)

    return qc


@pytest.mark.parametrize("a", VALID_MULTIPLIERS)
@pytest.mark.parametrize("c", [0, 1])
@pytest.mark.parametrize("x", range(16))
def test_oracle_basis(a: int, c: int, x: int):
    """Check arithmetic, controls, phases, and all clean ancillas."""
    qc = basis_input(c, x)
    qc.compose(controlled_modular_multiply(a, N), inplace=True)

    actual = Statevector.from_instruction(qc).data

    r = (a * x) % N if c and x < N else x

    expected = np.zeros(2**TOTAL_QUBITS, dtype=complex)
    expected[c + (r << 1)] = 1.0

    assert np.allclose(actual, expected, atol=1e-10, rtol=0), (
        f"Failed: a={a}, c={c}, x={x}, expected={r}"
    )


@pytest.mark.parametrize("a", VALID_MULTIPLIERS)
def test_oracle_inverse(a: int):
    """Check U_(a^-1) U_a = I on all clean-ancilla inputs."""
    inverse_a = pow(a, -1, N)

    oracle = controlled_modular_multiply(a, N)
    inverse_oracle = controlled_modular_multiply(inverse_a, N)

    for c in [0, 1]:
        for x in range(16):
            qc = basis_input(c, x)

            qc.compose(oracle, inplace=True)
            qc.compose(inverse_oracle, inplace=True)

            actual = Statevector.from_instruction(qc).data

            expected = np.zeros(2**TOTAL_QUBITS, dtype=complex)
            expected[c + (x << 1)] = 1.0

            assert np.allclose(actual, expected, atol=1e-10, rtol=0), (
                f"Inverse failed: a={a}, c={c}, x={x}"
            )
