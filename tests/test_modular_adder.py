import numpy as np
import pytest

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.synthesis import synth_qft_full

from erdos_project_1.modular_adder import controlled_modular_add


@pytest.mark.parametrize("a", range(15))
def test_modular_adder(a):
    N = 15
    m = 5

    modular_adder = controlled_modular_add(a, N)
    qft = synth_qft_full(m, do_swaps=True)
    arithmetic = list(range(2, m + 2))

    for c1 in (0, 1):
        for c2 in (0, 1):
            for b in range(N):
                qc = QuantumCircuit(m + 3)

                if c1:
                    qc.x(0)
                if c2:
                    qc.x(1)

                for j in range(m):
                    if (b >> j) & 1:
                        qc.x(2 + j)

                qc.compose(qft, qubits=arithmetic, inplace=True)
                qc.compose(modular_adder, inplace=True)
                qc.compose(
                    qft.inverse(),
                    qubits=arithmetic,
                    inplace=True,
                )

                state = Statevector.from_instruction(qc)

                expected_b = (a + b) % N if c1 and c2 else b

                expected_index = c1 + 2 * c2 + 4 * expected_b

                expected = np.zeros(2 ** (m + 3), dtype=complex)
                expected[expected_index] = 1

                assert np.allclose(state.data, expected, atol=1e-9)