# Reimplement einsum to check my understanding. Efficiency not a goal.
# (in Python3)

# An 'array' variable is a numpy ndarray.
# spec_string looks like e.g. "mn,np->mp".
# ref means a string of index letters, e.g "np".

import itertools
import numpy as np

def einsum(spec_string, *arrays):
    instr, out_ref = spec_string.split('->')
    in_refs = instr.split(',')
    if in_refs == ['']:
        raise ValueError("Must specify at least one operand")

    for ref in in_refs:
        check_ref(ref)
    check_ref(out_ref)
    in_set = set(''.join(in_refs))
    out_set = set(out_ref)
    if len(out_set) != len(out_ref):
        raise ValueError("Repeated index in output", out_ref)
    if not out_set.issubset(in_set):
        raise ValueError("Output unconnected to input", out_set.difference(in_set))
    all_subscripts = ''.join(in_set)

    if len(arrays) != len(in_refs):
        raise ValueError("Mismatch between spec_string and number of arguments",
                        spec_string, len(arrays))
    dims = find_dimensions(in_refs, arrays)
    out_shape = at(dims, out_ref)

    acc = np.zeros(out_shape) # Result accumulator
    for indices in itertools.product(*[range(dims[subscript])
                                       for subscript in all_subscripts]):
        # Assign each subscript its index value:
        setting = dict(zip(all_subscripts, indices))
        # At these indices, sum into the output the product of the inputs:
        acc[at(setting, out_ref)] += np.prod([arr[at(setting, ref)]
                                              for arr, ref in zip(arrays, in_refs)])
    return acc if out_shape else acc[()]

def at(setting, ref):
    "Return a tuple indexing into an n-d array, as specified by ref."
    return tuple(setting[letter] for letter in ref)

def check_ref(ref):
    for ch in ref:
        if not (ch.isalpha() and ch.isascii()):
            raise ValueError("Subscript is not a letter", ch)

def find_dimensions(refs, arrays):
    """Given refs like e.g. ['mn', 'np'] and corresponding ndarrays,
    map 'm', 'n', and 'p' to the corresponding array dimensions. Complain
    if the array shapes don't match the refs."""
    dims = {}
    for subscripts, array in zip(refs, arrays):
        if len(subscripts) != len(array.shape):
            raise ValueError("Rank mismatch", subscripts, array.shape)
        for letter, dim in zip(subscripts, array.shape):
            if letter not in dims:
                dims[letter] = dim
            elif dims[letter] != dim:
                raise ValueError("Dimension mismatch", letter, dims[letter], dim)
    return dims


# Smoke test from ChatGPT (tweaked)
import pytest

def test_einsum():
    # Define some arrays to use in the tests.
    a = np.arange(25).reshape((5, 5))
    b = np.ones((5, 5))

    # Case 1: trace of a matrix
    assert np.allclose(einsum('ii->', a),
                       np.einsum('ii', a))

    # Case 2: matrix multiplication
    assert np.allclose(einsum('ij,jk->ik', a, b),
                       np.einsum('ij,jk', a, b))

    # Case 3: outer product
    vec1 = np.array([1, 2, 3])
    vec2 = np.array([4, 5])
    assert np.allclose(einsum('i,j->ij', vec1, vec2),
                       np.einsum('i,j', vec1, vec2))

    # Case 4: tensor dot product
    c = np.arange(60.).reshape(3,4,5)
    d = np.arange(24.).reshape(4,3,2)
    assert np.allclose(einsum('ijk,jil->kl', c, d),
                       np.einsum('ijk,jil->kl', c, d))

    # Case 5: batch matrix multiplication
    e = np.ones((10, 3, 3))
    f = np.ones((10, 3, 3))
    assert np.allclose(einsum('ijk,ikl->ijl', e, f),
                       np.einsum('ijk,ikl->ijl', e, f))

test_einsum()
