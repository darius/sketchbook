-- Like nfa.py
-- Uses an algebraic datatype instead of functions for the states,
-- since we can't compare functions in Haskell.
-- E.g.: (lit 'a' . many (lit 'b' `alt` lit 'c') . lit 'd') `matches` "abbcd"
-- Thanks to Mike Vanier for some Haskelly tips.

import Data.List (nub)

matches re = any accepts . foldl step [re Accept]

data State = Accept | Expect Char State | Fork State State
  deriving (Eq, Ord)

accepts Accept       = True
accepts (Expect _ _) = False
accepts (Fork s1 s2) = accepts s1 || accepts s2

step states c = nub $ concat $ map (after c) states

after _ Accept            = []
after c (Expect c' state) = if c' == c then [state] else []
after c (Fork s1 s2)      = after c s1 ++ after c s2

lit = Expect
alt re1 re2 state = re1 state `Fork` re2 state
many re state = loop where loop = state `Fork` re loop
