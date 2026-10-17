import numpy as np
import pytest

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from erdos_project_1.modular_multiplier import controlled_modular_multiply


@pytest.mark.parametrize("a", [1, 2, 4, 7, 8, 11, 13, 14])
def test_controlled_modular_multiply(a):
    N = 15
    oracle = controlled_modular_multiply(a, N)

    for c in (0, 1):
        for x in range(16):
            qc = QuantumCircuit(oracle.num_qubits)

            if c:
                qc.x(0)

            for j in range(4):
                if (x >> j) & 1:
                    qc.x(j + 1)

            qc.compose(oracle, inplace=True)

            state = Statevector.from_instruction(qc)

            expected_x = (a * x) % N if c and x < N else x
            expected_index = c + 2 * expected_x

            expected = np.zeros(2**oracle.num_qubits, dtype=complex)
            expected[expected_index] = 1

            assert np.allclose(state.data, expected, atol=1e-9)