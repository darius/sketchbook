-- Like nfavector2.hs, but, instead of [Int] for state-sets, uses bit ops on Integer.

import Data.Bits
import qualified Data.Vector as V

matches re cs = 0 /= (1 .&. endBits)
  where endBits = foldl step startBits cs
        (starts, states) = re ([0::Int], [('#', [])])  -- ('#' is arbitrary)
        startBits = asBitset starts
        stateVector = V.fromList [(c, asBitset succs) | (c, succs) <- states]
        step stateBits c = foldr (.|.) 0 $ map after $ enumerateOnBits stateBits
          where after i = let (c', xs) = stateVector V.! i in
                          if c' == c then xs else 0

asBitset = sum . map bit

enumerateOnBits :: Integer -> [Int]
enumerateOnBits = enumFrom 0
  where enumFrom _ 0 = []
        enumFrom i n = if 0 == (n .&. 1) then rest else i:rest
                       where rest = enumFrom (i+1) (n `shiftR` 1)

lit c (starts, states) = ([length states], states ++ [(c, starts)])

alt re1 re2 nfa@(starts, _) = (starts1 ++ starts2, states2)
  where (starts1, states1) = re1 nfa
        (starts2, states2) = re2 (starts, states1) 

many re (starts, states) = (resultStarts, loopStates)
  where (loopStarts, loopStates) = re (resultStarts, states)
        resultStarts = starts ++ loopStarts
