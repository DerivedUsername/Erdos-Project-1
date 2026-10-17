# A Controlled Modular Multiplication Oracle for Shor's Algorithm

**Erdős Institute — Quantum Computing Bootcamp, Mini-project 1, Project 6**

This project constructs and tests a reversible **controlled modular multiplication oracle** using Qiskit. For a classical modulus `N` and multiplier `a` with `gcd(a, N) = 1`, the target operation is

\[
|c\rangle |y\rangle |0\rangle_w \longmapsto
|c\rangle |g_{a,N}(c,y)\rangle |0\rangle_w,
\]

where

\[
g_{a,N}(c,y) =
\begin{cases}
ay\bmod N, & c=1\text{ and }y<N,\\
y, & \text{otherwise}.
\end{cases}
\]

The circuit preserves the external control and returns **every work qubit to zero**. The required supported case is **`N = 15` for all eight coprime multipliers**: `1, 2, 4, 7, 8, 11, 13, 14`.

## Method

The implementation follows the Fourier-arithmetic approach of Beauregard, assembled in four stages:

1. **Fourier adder:** Implement addition by a classical constant using single-qubit phase rotations in the Fourier basis.
2. **Doubly controlled modular adder:** Use subtraction of `N`, an underflow flag, modular correction, and reversible uncomputation.
3. **Controlled modular multiply-accumulate:** Build multiplication as a sequence of modular additions controlled by the external control and each input bit.
4. **Clean in-place oracle:** Compute the product, swap registers conditionally, and uncompute the accumulator using the inverse of the multiply-accumulate circuit for `a⁻¹ mod N`.

For `N = 15`, an additional validity flag ensures the unused four-bit state `y = 15` is left unchanged.

The notebook provides the mathematical derivation, example circuits, correctness demonstrations, resource measurements, and a discussion of superpositions and ancilla cleanup.

## Repository structure

```text
Erdos-Project-1/
├── notebooks/
│   └── 01_shor_oracle.ipynb
├── src/
│   └── erdos_project_1/
│       ├── __init__.py
│       ├── fourier_adder.py
│       ├── modular_adder.py
│       ├── controlled_multiplier.py
│       ├── modular_multiplier.py
│       └── classical_reference.py
├── tests/
│   ├── test_fourier_adder.py
│   ├── test_modular_adder.py
│   ├── test_controlled_multiplier.py
│   └── test_modular_multiplier.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

Install [`uv`](https://docs.astral.sh/uv/) and use a Python version compatible with the project's `pyproject.toml`. From the repository root:

```bash
uv sync --locked
```

In VS Code, select the Python interpreter and Jupyter kernel from this project's `.venv` environment. Open `notebooks/01_shor_oracle.ipynb`, restart the kernel, and run all cells in order.

The environment is managed through `pyproject.toml` and `uv.lock`; do not install dependencies into a different Python environment when working with the notebook.

## Usage

The function returns a Qiskit circuit, rather than an ordinary integer. This example prepares the input `y = 3`, applies multiplication by `a = 7` modulo `15`, and checks **both** control branches (`c = 0` leaves the input unchanged; `c = 1` produces `7 * 3 mod 15 = 6`). All work qubits start and end in `|0⟩`.

```python
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from erdos_project_1.modular_multiplier import controlled_modular_multiply

a, N, y = 7, 15, 3
oracle = controlled_modular_multiply(a=a, N=N)
print(oracle.num_qubits)  # 12

for control in (0, 1):
    qc = QuantumCircuit(oracle.num_qubits)

    # q[0] is the control; X changes |0> to |1> when enabled.
    if control == 1:
        qc.x(0)

    # q[1:5] stores y in little-endian bit order.
    for j in range(4):
        if (y >> j) & 1:
            qc.x(j + 1)

    qc.compose(oracle, inplace=True)

    # This circuit has a deterministic computational-basis output.
    state = Statevector.from_instruction(qc)
    index = max(range(len(state.data)), key=lambda i: abs(state.data[i]) ** 2)
    output_y = (index >> 1) & 0b1111
    work = index >> 5

    expected = (a * y) % N if control else y
    assert output_y == expected
    assert work == 0
    print(f"Control={control}: {y} -> {output_y}, work={work}")
```

Expected output:

```text
12
Control=0: 3 -> 3, work=0
Control=1: 3 -> 6, work=0
```

This is an ideal **statevector simulation**, not execution on quantum hardware. The notebook and tests separately verify coherent superpositions and relative phases, which cannot be established from computational-basis examples alone.

### Register layout for `N = 15`

Qiskit uses little-endian qubit numbering.

| Qubit indices | Role | Size |
| --- | --- | ---: |
| `q[0]` | External control `c` | 1 |
| `q[1]`–`q[4]` | Input/output `y`, least-significant bit first | 4 |
| `q[5]`–`q[9]` | Arithmetic accumulator, including extra most-significant bit | 5 |
| `q[10]` | Modular-adder work ancilla | 1 |
| `q[11]` | Validity flag for `y = 15` | 1 |

**Total:** 12 qubits, including **7 clean work qubits**. Initialize all work qubits to `|0⟩`. The routine rejects multipliers that are not coprime to `N`; the final in-place implementation is currently specialized to `N = 15`.

The intermediate `controlled_multiply(a, N)` is a **multiply-accumulate** operation, not the same as the final in-place oracle.

## Verification

Tests compare exact complex statevectors or unitary matrices with independent arithmetic references, using an absolute tolerance of `1e-10`. They check arithmetic outputs, control preservation, input boundaries, phases, and work-register cleanup.

- Fourier adder: compare against `F T_a F⁻¹` and test the inverse.
- Modular adder: test valid register inputs and control combinations.
- Multiply-accumulate: check output values, unchanged input/control, and clean work qubits.
- Final oracle: check every `y = 0,…,15`, both control values, and all eight valid multipliers, including `a = 1`, `y = 0`, and `y = 15`.
- Inverse composition: check the final oracle followed by the one for `a⁻¹ mod 15` on clean-work inputs.
- Superpositions: the notebook includes a `|+⟩`-control example, comparing the entire complex output state to detect relative phases and residual workspace entanglement.

Run the full suite:

```bash
uv run pytest
```

Before submission, also run:

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
```

These commands are the **validation procedure**, not a claim that the latest run has passed; confirm their terminal results and rerun the notebook from a clean kernel.

## Measured circuit resources (`N = 15`)

All eight valid multipliers had identical counts under the measured circuit construction and compilation settings:

| Circuit representation | Gates | Depth |
| --- | ---: | ---: |
| Original Qiskit circuit | 852 | 528 |
| `decompose(reps=10)` | 4,520 | 2,887 |
| Transpiled to `rz`, `sx`, `x`, `cx` | 4,695 | 2,926 |

The final transpilation used `optimization_level=0`, with no hardware connectivity constraints. Its gate distribution was **2,613 `rz`**, **218 `sx`**, **20 `x`**, and **1,844 `cx`**. In the original representation, the circuit had **120 doubly controlled phase gates** and **two five-controlled X gates** for validity-flag computation and uncomputation; additional singly controlled operations are documented in the notebook.

These counts describe a particular decomposition, **not** a hardware-optimized implementation or an estimate of wall-clock simulation time.

## Scope and limitations

- The **final in-place oracle** is implemented for `N = 15`; extension to arbitrary moduli is not claimed.
- The implementation uses Qiskit's built-in QFT and inverse QFT as permitted by the assignment. Fourier arithmetic and modular multiplication are composed in project code, rather than using built-in modular multiplication or permutation synthesis.
- No measurement, reset, or classical bit is used inside the oracle.
- Resource counts depend on the selected gate basis and transpilation settings; physical connectivity and noise are not modeled.
- This project constructs the modular multiplication **oracle**, not a complete implementation of Shor's order-finding algorithm.

## Attribution

The construction is based on:

- Stéphane Beauregard, *Circuit for Shor's Algorithm Using 2n+3 Qubits*, [arXiv:quant-ph/0205095](https://arxiv.org/abs/quant-ph/0205095), especially the Fourier-adder, modular-adder, multiply-accumulate, and clean multiplication constructions (Figures 3, 5, 6, and 7).
- Qiskit is used for quantum circuit representation, allowed QFT/inverse-QFT construction, statevector verification, circuit diagrams, and gate-basis transpilation.
- NumPy is used for independent numerical references and comparisons; pytest for automated tests; Ruff for linting/formatting; uv for reproducible dependency management; pandas for resource tables in the notebook.
