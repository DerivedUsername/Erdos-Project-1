from math import pi

from qiskit import QuantumCircuit
from qiskit.synthesis import synth_qft_full

from erdos_project_1.fourier_adder import phi_add


def append_phi_add(
    qc: QuantumCircuit,
    a: int,
    arithmetic: list[int],
    controls: list[int],
) -> None:
    """Append Fourier addition by a, with zero, one, or two controls."""
    m = len(arithmetic)

    if len(controls) == 0:
        qc.compose(phi_add(a, m), qubits=arithmetic, inplace=True)
        return

    for j, target in enumerate(arithmetic):
        theta = 2 * pi * a / (2 ** (m - j))

        if len(controls) == 1:
            qc.cp(theta, controls[0], target)
        elif len(controls) == 2:
            qc.mcp(theta, controls, target)
        else:
            raise ValueError("At most two controls are supported")


def controlled_modular_add(a: int, N: int) -> QuantumCircuit:
    """
    Construct Beauregard's doubly controlled Fourier modular adder.

    Inputs:
        a: Classical integer, 0 <= a < N.
        N: Modulus, N >= 2.

    Qubit layout:
        q[0], q[1]: controls
        q[2] ... q[m+1]: Fourier arithmetic register
        q[m+2]: clean ancilla

    Assumes the arithmetic register represents 0 <= b < N.
    Returns the work ancilla to |0>.
    """
    if N < 2 or not (0 <= a < N):
        raise ValueError("Require N >= 2 and 0 <= a < N")

    n = (N - 1).bit_length()
    m = n + 1

    qc = QuantumCircuit(m + 3, name=f"modadd_{a}_{N}")

    controls = [0, 1]
    arithmetic = list(range(2, m + 2))
    msb = arithmetic[-1]
    ancilla = m + 2

    qft = synth_qft_full(m, do_swaps=True)
    iqft = qft.inverse()

    # ---- First half: compute the modular sum ----

    # 1. Add a if both control qubits are 1.
    append_phi_add(qc, a, arithmetic, controls)

    # 2. Subtract N.
    append_phi_add(qc, -N, arithmetic, [])

    # 3. Return to computational basis.
    qc.compose(iqft, qubits=arithmetic, inplace=True)

    # 4. Copy the sign bit into the ancilla.
    qc.cx(msb, ancilla)

    # 5. Return to Fourier basis.
    qc.compose(qft, qubits=arithmetic, inplace=True)

    # 6. Add N back if subtraction underflowed.
    append_phi_add(qc, N, arithmetic, [ancilla])

    # ---- Second half: uncompute the ancilla ----

    # 7. Undo the initial conditional addition of a.
    append_phi_add(qc, -a, arithmetic, controls)

    # 8. Return to computational basis.
    qc.compose(iqft, qubits=arithmetic, inplace=True)

    # 9-11. Erase the ancilla using the complemented MSB.
    qc.x(msb)
    qc.cx(msb, ancilla)
    qc.x(msb)

    # 12. Return to Fourier basis.
    qc.compose(qft, qubits=arithmetic, inplace=True)

    # 13. Restore the conditional addition of a.
    append_phi_add(qc, a, arithmetic, controls)

    return qc
