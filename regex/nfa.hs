-- Like nfa.py
-- Uses an algebraic datatype instead of functions for the states,
-- since we can't compare functions in Haskell.

import Data.Set (elems, empty, singleton, union, unions)

data State = Accept | Expect Char State | Fork State State
   deriving (Eq, Ord)

isAccepting Accept       = True
isAccepting (Expect _ _) = False
isAccepting (Fork s1 s2) = isAccepting s1 || isAccepting s2

after c Accept            = empty
after c (Expect c' state) = if c' == c then singleton state else empty
after c (Fork s1 s2)      = after c s1 `union` after c s2

epsilon state = state
alt re1 re2 state = re1 state `Fork` re2 state
many re state = loop where loop = state `Fork` re loop
lit = Expect

match re = any isAccepting . elems . foldl step (singleton $ re Accept)
  where step states c = unions $ map (after c) (elems states)
