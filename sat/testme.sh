#!/bin/bash

try_it () {
    local mod=$1
    local param=$2
    local solver=$3
    echo $mod $param $solver 1>&2
    echo $mod $param $solver
    time python $mod.py $param $solver
}

try_it nqueens 4 ttsat
try_it nqueens 4 prunettsat
try_it nqueens 4 unitsat

for size in 4 14; do
    for solver in indexedsat watch1sat impwatch1sat watch1unitsat; do
        try_it nqueens $size $solver
    done
done

# way too slow: watch1sat
# also slow at ~30 sec: impwatch1sat
for solver in indexedsat watch1unitsat; do
    try_it sudoku easy $solver
done
