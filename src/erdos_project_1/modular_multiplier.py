from math import gcd
from qiskit import QuantumCircuit

from erdos_project_1.controlled_multiplier import controlled_multiply


def controlled_modular_multiply(a: int, N: int) -> QuantumCircuit:
    """
    Controlled modular multiplication in-place.

    Specialized to N=15, including the identity action on x=15.

    q[0]: external control
    q[1:5]: input x
    q[5:10]: accumulator (5 qubits)
    q[10]: modular-adder work ancilla
    q[11]: effective-control flag

    All work qubits return to zero.
    """
    if N != 15:
        raise ValueError("This implementation currently supports N=15")

    if not (1 <= a < N) or gcd(a, N) != 1:
        raise ValueError("a must be a unit modulo N")

    n = (N - 1).bit_length()

    qc = QuantumCircuit(2 * n + 4)

    x = list(range(1, n + 1))
    accumulator = list(range(n + 1, 2 * n + 2))
    work = 2 * n + 2
    flag = 2 * n + 3

    # Effective control = c AND (x != 15).
    qc.cx(0, flag)
    qc.mcx([0, *x], flag)

    # Step 1: compute ax into accumulator.
    mult_a = controlled_multiply(a, N)

    qc.compose(
        mult_a,
        qubits=[flag, *x, *accumulator, work],
        inplace=True,
    )

    # Step 2: swap x with the low n accumulator qubits.
    for j in range(n):
        qc.cswap(flag, x[j], accumulator[j])

    # Step 3: erase the old x using multiplication by a^-1.
    inverse_a = pow(a, -1, N)
    mult_inverse = controlled_multiply(inverse_a, N)

    qc.compose(
        mult_inverse.inverse(),
        qubits=[flag, *x, *accumulator, work],
        inplace=True,
    )

    # Erase the validity flag.
    # Valid residues remain valid under multiplication by a unit.
    qc.mcx([0, *x], flag)
    qc.cx(0, flag)

    return qc