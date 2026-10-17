import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.synthesis import synth_qft_full

from erdos_project_1.modular_adder import controlled_modular_add


@pytest.mark.parametrize("a", range(15))
@pytest.mark.parametrize(
    "c1,c2",
    [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ],
)
def test_controlled_modular_add(a: int, c1: int, c2: int):
    N = 15
    n = (N - 1).bit_length()
    m = n + 1

    arithmetic = list(range(2, m + 2))
    qft = synth_qft_full(m, do_swaps=True)
    oracle = controlled_modular_add(a, N)

    for b in range(N):
        qc = QuantumCircuit(m + 3)

        if c1:
            qc.x(0)
        if c2:
            qc.x(1)

        for j in range(n):
            if (b >> j) & 1:
                qc.x(arithmetic[j])

        qc.compose(qft, qubits=arithmetic, inplace=True)
        qc.compose(oracle, inplace=True)
        qc.compose(qft.inverse(), qubits=arithmetic, inplace=True)

        actual = Statevector.from_instruction(qc).data

        r = (a + b) % N if c1 and c2 else b
        expected_index = c1 + (c2 << 1) + (r << 2)

        expected = np.zeros(2 ** (m + 3), dtype=complex)
        expected[expected_index] = 1.0

        assert np.allclose(actual, expected, atol=1e-10, rtol=0), (
            f"Failed for a={a}, b={b}, c1={c1}, c2={c2}"
        )
