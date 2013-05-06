-- Like nfa.py
-- Uses an algebraic datatype instead of functions for the states,
-- since we can't compare functions in Haskell.
-- Example:
--   match (lit 'a' . many (lit 'b' `alt` lit 'c') . lit 'd') "abbcd"

import Data.Set (elems, empty, singleton, union, unions)

match re = any accepts . elems . foldl step (singleton $ re Accept)
  where step states c = unions $ map (after c) (elems states)

data State = Accept | Expect Char State | Fork State State
   deriving (Eq, Ord)

accepts Accept       = True
accepts (Expect _ _) = False
accepts (Fork s1 s2) = accepts s1 || accepts s2

after c Accept            = empty
after c (Expect c' state) = if c' == c then singleton state else empty
after c (Fork s1 s2)      = after c s1 `union` after c s2

lit = Expect
alt re1 re2 state = re1 state `Fork` re2 state
many re state = loop where loop = state `Fork` re loop
