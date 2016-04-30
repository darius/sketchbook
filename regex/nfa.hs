-- Like nfa.py
-- E.g.: (lit 'a' . many (lit 'b' `alt` lit 'c') . lit 'd') `matches` "abbcd"
-- Thanks to Mike Vanier for some Haskelly tips.

import Data.List (nub)

data State = Accept | Expect Char [State]
  deriving Eq

matches re = any (Accept ==) . foldl step (re [Accept])
step states c = nub $ concat $ map (after c) states

after _ Accept             = []
after c (Expect c' states) = if c' == c then states else []

lit c states = [Expect c states]
alt re1 re2 states = re1 states ++ re2 states
many re states = loop where loop = states ++ re loop
