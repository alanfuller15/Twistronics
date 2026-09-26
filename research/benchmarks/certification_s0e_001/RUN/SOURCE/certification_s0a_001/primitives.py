"""Small, auditable Arb primitives. Exact symmetric inputs are a precondition.

Bounds are serialized as dyadic endpoints. Floats are used only for timings.
This module contains no Twistronics Hamiltonian or physical parameter imports.
"""
from math import factorial
from flint import arb, arb_mat


def dyadic(x):
    m, e = x.man_exp()
    return {"mantissa": str(m), "exponent": int(e)}


def enclosure(x):
    if not x.is_finite():
        raise ArithmeticError("nonfinite bound")
    return {"lower": dyadic(x.lower()), "upper": dyadic(x.upper())}


def frobenius(a):
    # abs_upper makes this valid for a rectangular interval enclosure too.
    return sum((a[i, j].abs_upper() ** 2
                for i in range(a.nrows()) for j in range(a.ncols())), arb(0)).sqrt()


def identity(n):
    return arb_mat([[int(i == j) for j in range(n)] for i in range(n)])


def inertia_ldl(a):
    """Unpivoted interval LDL. Ambiguous pivots stop, without changing shifts.

The supplied balls must enclose one exact real symmetric matrix (or a
family of such matrices). Only the lower triangle is evaluated. Induction
on exact Schur complements establishes the enclosure of each signed pivot.
"""
    n = a.nrows()
    if a.ncols() != n:
        raise ValueError("square matrix required")
    l, d, pivots = [], [], []
    negative = 0
    for i in range(n):
        row = []
        for j in range(i):
            s = a[i, j]
            for k in range(j):
                s = s - row[k] * d[k] * l[j][k]
            row.append(s / d[j])
        p = a[i, i]
        for k in range(i):
            p = p - row[k] * row[k] * d[k]
        if not p.is_finite():
            raise ArithmeticError("nonfinite LDL pivot")
        pivots.append(enclosure(p))
        if p.contains(0):
            return {"status": "INCONCLUSIVE", "reason": "ZERO_CONTAINING_PIVOT",
                    "pivot_index": i, "pivots": pivots}
        negative += int(p < 0)
        d.append(p)
        row.append(arb(1))
        l.append(row)
    return {"status": "PASS", "negative": negative, "positive": n - negative,
            "zero": 0, "pivots": pivots}


def householder(n):
    u = [1 + i % 7 for i in range(n)]
    s = sum(x*x for x in u)
    q = arb_mat([[arb(int(i == j)) - arb(2*u[i]*u[j])/s
                  for j in range(n)] for i in range(n)])
    return u, s, q


def synthetic_symmetric(n):
    u, s, q = householder(n)
    m = (n - 2) // 2
    d = [-3-i for i in range(m)] + [0, 0] + [3+i for i in range(m)]
    weighted = sum(ui*ui*di for ui, di in zip(u, d))
    # Exact algebra for Q diag(d) Q^T, evaluated with outward rounding.
    h = arb_mat([[arb(d[i] if i == j else 0)
                  - arb(2*u[i]*u[j]*(d[i]+d[j]))/s
                  + arb(4*u[i]*u[j]*weighted)/(s*s)
                  for j in range(n)] for i in range(n)])
    v = arb_mat([[q[i, j]*(arb(1)+arb(1+j % 3)/1024)
                  for j in range(n)] for i in range(n)])
    return h, v, d


def midpoint_matrix(a):
    c = arb_mat([[a[i, j].mid() for j in range(a.ncols())]
                 for i in range(a.nrows())])
    r = frobenius(a - c)
    return c, r


def transport_constant(n, omega, steps, degree):
    """Known skew problem with full n-by-2 state, but structured O(n) steps.

For exact skew A, ||exp(hA)-sum_{k=0}^m(hA)^k/k!||_2
    <= (h||A||_2)^(m+1)/(m+1)!.
Orthogonal exact propagation carries the previous error with factor one.
Each rounded polynomial endpoint is recentered; its entire radius is added.
"""
    _, _, q = householder(n)
    f0 = arb_mat([[q[i, j] for j in range(2)] for i in range(n)])
    center, error = midpoint_matrix(f0)
    initial_error = error
    z = arb(omega) / steps
    tail = z ** (degree+1) / factorial(degree+1)
    # Polynomial in J is c I+s J; J^2=-I on each coordinate pair.
    c, s = arb(0), arb(0)
    for k in range(degree+1):
        term = z**k / factorial(k)
        if k % 2:
            s += (-1)**((k-1)//2)*term
        else:
            c += (-1)**(k//2)*term
    max_rounding = arb(0)
    truncation = arb(0)
    rounding = arb(0)
    for _ in range(steps):
        local = tail*frobenius(center)
        y = arb_mat([[c*center[i, j] + (-s*center[i+1, j] if i % 2 == 0
                                        else s*center[i-1, j])
                      for j in range(2)] for i in range(n)])
        center, radius = midpoint_matrix(y)
        error += local + radius
        truncation += local
        rounding += radius
        max_rounding = arb(max(max_rounding.upper(), radius.upper()))
    ct, st = arb(omega).cos(), arb(omega).sin()
    reference = arb_mat([[ct*f0[i, j] + (-st*f0[i+1, j] if i % 2 == 0
                                        else st*f0[i-1, j])
                          for j in range(2)] for i in range(n)])
    discrepancy = frobenius(center - reference)
    # For an uncertain constant rate omega +/- 1/1000, the extra Duhamel
    # error bound is sqrt(2)/1000 on [0,1]. This is not silently discarded.
    parameter_debit = arb(2).sqrt()/1000
    return {"bound": error, "reference_discrepancy_bound": discrepancy,
            "initial_rounding_bound": initial_error, "truncation_sum_bound": truncation,
            "rounding_sum_bound": rounding, "max_step_rounding_bound": max_rounding,
            "local_operator_remainder_bound": tail,
            "uncertain_rate_extra_bound": parameter_debit,
            "uncertain_rate_total_bound": error+parameter_debit}
