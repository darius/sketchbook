-- Like nfa.hs, but with numbered states, so that we can compare them
-- by index, to deduplicate them without looping forever.
-- (It does still loop on many (many (lit 'a')).)
-- Thanks to Libby Horacek for a bunch of help,
-- and Tom Murphy for pointing out Data.Vector.

import Data.List (nub)
import qualified Data.Vector as V

accept = -1  -- A dummy index meaning the accepting state.

matches re cs = accept `elem` foldl step starts cs
  where (starts, states) = re ([accept], [])
        step starts' c = nub $ concat $ map (after c stateVector) starts'
        stateVector = V.fromList states

after c states i = if i == accept then []
                   else let (c', xs) = states V.! i in
                        if c' == c then xs else []

lit c (starts, states) = ([length states], states ++ [(c, starts)])

alt re1 re2 nfa@(starts, _) = (starts1 ++ starts2, states2)
  where (starts1, states1) = re1 nfa
        (starts2, states2) = re2 (starts, states1) 

many re (starts, states) = (resultStarts, loopStates)
  where (loopStarts, loopStates) = re (resultStarts, states)
        resultStarts = starts ++ loopStarts
