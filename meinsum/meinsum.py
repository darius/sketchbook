# Reimplement einsum to check my understanding. Efficiency not a goal.
# (in Python3)
# https://numpy.org/doc/stable/reference/generated/numpy.einsum.html
# Features skipped:
#  - only takes the einsum required arguments, none of the extra keyword arguments
#  - "->xyz" in spec_string is not optional (i.e. explicit mode only)
#  - "..." in spec_string is not supported

# An 'array' variable is a numpy ndarray.
# spec_string looks like e.g. "mn,np->mp".
# ref means a string of subscripts, e.g "np".

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
    all_ref = ''.join(in_set)

    if len(in_refs) != len(arrays):
        raise ValueError("Mismatch between spec_string and number of arguments",
                         spec_string, len(arrays))
    dims = find_dimensions(in_refs, arrays)
    out_shape = at(dims, out_ref)

    acc = np.zeros(out_shape) # Result accumulator
    # For every value of every subscript:
    for indices in itertools.product(*[range(dims[subscript])
                                       for subscript in all_ref]):
        # Assign each subscript its index value:
        setting = dict(zip(all_ref, indices))
        # At these indices, sum into the output the product of the inputs:
        acc[at(setting, out_ref)] += np.prod([arr[at(setting, ref)]
                                              for arr, ref in zip(arrays, in_refs)])
    return acc if out_shape else acc[()]

def at(setting, ref):
    "Return a tuple indexing into an n-d array, as specified by ref."
    return tuple(setting[subscript] for subscript in ref)

def check_ref(ref):
    for ch in ref:
        if not (ch.isalpha() and ch.isascii()):
            raise ValueError("Subscript is not a letter", ch)

def find_dimensions(refs, arrays):
    """Given refs like e.g. ['mn', 'np'] and corresponding ndarrays,
    return a dict from (again e.g.) 'm', 'n', and 'p' to the
    corresponding array dimensions. Complain if the array shapes don't
    match the refs."""
    dims = {}
    for ref, array in zip(refs, arrays):
        if len(ref) != len(array.shape):
            raise ValueError("Rank mismatch", ref, array.shape)
        for subscript, dim in zip(ref, array.shape):
            if dims.get(subscript, dim) != dim:
                raise ValueError("Dimension mismatch", subscript, dims[subscript], dim)
            dims[subscript] = dim
    return dims


# Smoke test originally by ChatGPT

def test_einsum():

    def check_einsum(spec_string, *arrays):
        assert np.allclose(einsum(spec_string, *arrays),
                           np.einsum(spec_string, *arrays))

    # Example data to use in the tests.
    a = np.arange(25).reshape((5, 5))
    b = np.ones((5, 5))
    vec1 = np.array([1, 2, 3])
    vec2 = np.array([4, 5])
    vec5 = np.arange(5)
    c = np.arange(60.).reshape(3,4,5)
    d = np.arange(24.).reshape(4,3,2)
    e = np.ones((10, 3, 3))
    f = np.ones((10, 3, 3))

    # The tests. In the comments, M for matrix, v for vector.
    # Mostly from https://obilaniu6266h16.wordpress.com/2016/02/04/einstein-summation-in-numpy/

    check_einsum('i->', vec1)                # 1-d sum
    check_einsum('ij->', a)                  # 2-d sum
    check_einsum('ijk->', c)                 # 3-d sum

    check_einsum('i,i->', vec1, vec1)        # v dot v
    check_einsum('i,i->i', vec1, vec1)       # v elementwise* v
    check_einsum('i,j->ij', vec1, vec2)      # v outer* v

    check_einsum('i,ij->j', vec5, a)         # vM
    check_einsum('ij,j->i', a, vec5)         # Mv
    check_einsum('i,ij,j->', vec5, a, vec5)  # vMv (quadratic form)

    check_einsum('ij->ji', a)                # M transpose
    check_einsum('ii->i', a)                 # M diagonal
    check_einsum('ii->', a)                  # M trace
    check_einsum('ij,ij->', a, a)            # M dot M (|M|^2)

    check_einsum('ij,jk->ik', a, b)          # MM (matrix *)
    check_einsum('Bij,Bjk->Bik', e, f)       # batch MM
    check_einsum('ijk,jil->kl', c, d)        # tensor contraction

test_einsum()
