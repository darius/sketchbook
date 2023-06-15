# Reimplement einsum to check my understanding. Efficiency not a goal.
# (in Python3)

# An 'array' variable is a numpy ndarray.
# spec_string looks like e.g. "mn,np->mp".

import itertools
import numpy as np

def einsum(spec_string, *arrays):
    instr, out = spec_string.split('->')
    ins = instr.split(',')
    if ins == ['']:
        raise Exception("Must specify at least one operand")

    if len(arrays) != len(ins):
        raise Exception("Mismatch between spec_string and number of input arrays",
                        spec_string, len(arrays))
    for index_string in ins:
        check_index_string(index_string)
    check_index_string(out)
    in_set = set(''.join(ins))
    out_set = set(out)
    if len(out_set) != len(out):
        raise Exception("Repeated index in output", out)
    if not out_set.issubset(in_set):
        raise Exception("Output unconnected to input", out_set.difference(in_set))
    letters = ''.join(in_set)

    dims = find_dimensions(ins, arrays)
    out_shape = at(dims, out)

    acc = np.zeros(out_shape) # Result accumulator
    for indices in itertools.product(*[range(dims[letter]) for letter in letters]):
        # Assign each letter its index value:
        setting = dict(zip(letters, indices))
        # At these indices, sum into the output the product of the inputs:
        acc[at(setting, out)] += np.prod([arr[at(setting, arr_letters)]
                                          for arr, arr_letters in zip(arrays, ins)])
    return acc if out_shape else acc[()]

def at(setting, index_string):
    "Return a tuple indexing into an n-d array, as specified by index_string."
    return tuple(setting[letter] for letter in index_string)

def check_index_string(index_string):
    for ch in index_string:
        if not (ch.isalpha() and ch.isascii()):
            raise Exception("Index is not a letter", ch)

def find_dimensions(ins, arrays):
    """Given index strings like e.g. ['mn', 'np'] and corresponding ndarrays,
    map 'm', 'n', and 'p' to the corresponding array dimensions. Complain
    if the arrays don't match the patterns."""
    dims = {}
    for letters, array in zip(ins, arrays):
        shape = array.shape
        if len(letters) != len(shape):
            raise Exception("Rank mismatch", letters, shape)
        for letter, size in zip(letters, shape):
            if letter not in dims:
                dims[letter] = size
            elif dims[letter] != size:
                raise Exception("Dimension mismatch", letter, dims[letter], size)
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
