from qiskit import QuantumCircuit
from qiskit.synthesis import synth_qft_full

from erdos_project_1.modular_adder import controlled_modular_add


def controlled_multiply(a: int, N: int) -> QuantumCircuit:
    """
    Figure 6: Controlled modular multiply-accumulate.

    q[0]: external control
    q[1:n+1]: input x, little-endian
    q[n+1:2*n+2]: accumulator b, n+1 qubits
    q[2*n+2]: clean work ancilla

    Requires 0 <= x,b < N.
    """
    if N < 2 or not (0 <= a < N):
        raise ValueError("Invalid multiplier or modulus")

    n = (N - 1).bit_length()
    m = n + 1

    qc = QuantumCircuit(2 * n + 3)

    x = list(range(1, n + 1))
    accumulator = list(range(n + 1, 2 * n + 2))
    work = 2 * n + 2

    qft = synth_qft_full(m, do_swaps=True)

    # Encode the accumulator in the Fourier basis.
    qc.compose(qft, qubits=accumulator, inplace=True)

    for j in range(n):
        constant = (a * 2**j) % N
        adder = controlled_modular_add(constant, N)

        # Controls: external c and input bit x[j].
        qc.compose(
            adder,
            qubits=[0, x[j], *accumulator, work],
            inplace=True,
        )

    # Return accumulator to computational basis.
    qc.compose(qft.inverse(), qubits=accumulator, inplace=True)

    return qc
