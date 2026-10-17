from math import gcd

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from erdos_project_1.controlled_multiplier import controlled_multiply

N = 15
N_QUBITS = (N - 1).bit_length()
TOTAL_QUBITS = 2 * N_QUBITS + 3

VALID_MULTIPLIERS = [a for a in range(1, N) if gcd(a, N) == 1]


@pytest.mark.parametrize("a", VALID_MULTIPLIERS)
@pytest.mark.parametrize("c", [0, 1])
def test_controlled_multiply(a: int, c: int):
    oracle = controlled_multiply(a, N)

    for x in range(N):
        for b in range(N):
            qc = QuantumCircuit(TOTAL_QUBITS)

            # Initialize control
            if c:
                qc.x(0)

            # Initialize x register
            for j in range(N_QUBITS):
                if (x >> j) & 1:
                    qc.x(1 + j)

            # Initialize accumulator
            for j in range(N_QUBITS):
                if (b >> j) & 1:
                    qc.x(N_QUBITS + 1 + j)

            qc.compose(oracle, inplace=True)

            actual = Statevector.from_instruction(qc).data

            r = (b + c * a * x) % N

            expected_index = c + (x << 1) + (r << (N_QUBITS + 1))

            expected = np.zeros(2**TOTAL_QUBITS, dtype=complex)
            expected[expected_index] = 1.0

            assert np.allclose(actual, expected, atol=1e-10, rtol=0), (
                f"Failed: a={a}, c={c}, x={x}, b={b}, expected accumulator={r}"
            )
