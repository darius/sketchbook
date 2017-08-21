-- Like nfa.hs, but with numbered states, so that we can compare them
-- by index, to deduplicate them without looping forever.
-- (It does still loop on many (many (lit 'a')).)
-- Thanks to Libby Horacek for a bunch of help,
-- and Tom Murphy for pointing out Data.Vector.

import Data.List (nub)
import qualified Data.Vector as V

matches re cs = 0 `elem` foldl step starts cs
  where (starts, states) = re ([0], [('#', [])])  -- ('#' is arbitrary)
        step starts' c = nub $ concat $ map (after c) starts'
        after c i = let (c', xs) = stateVector V.! i in
                    if c' == c then xs else []
        stateVector = V.fromList states

lit c (starts, states) = ([length states], states ++ [(c, starts)])

alt re1 re2 nfa@(starts, _) = (starts1 ++ starts2, states2)
  where (starts1, states1) = re1 nfa
        (starts2, states2) = re2 (starts, states1) 

many re (starts, states) = (resultStarts, loopStates)
  where (loopStarts, loopStates) = re (resultStarts, states)
        resultStarts = starts ++ loopStarts
