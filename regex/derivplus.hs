-- Thompson said he derived his method from Brzozowski
-- derivatives. Here's an idea how one might start down tha road. To
-- keep things easier while I figure this out, let's avoid epsilon.

import Data.List (nub)

data RE = Empty | Lit Char | Seq RE RE | Alt RE RE | Plus RE
  deriving (Ord, Eq)

-- I'm going to assume Empty never appears in an re input to matches.
-- Empty is meant only to be introduced internally, and immediately
-- dropped on combination with any other RE. (We never form new REs
-- internally except by Seq, which has Empty as its identity element.)
matches :: RE -> String -> Bool
matches re chars = Empty `elem` foldl step [re] chars

step :: [RE] -> Char -> [RE]
step res c = nub $ concat $ map (deriv c) res

-- deriv is not exactly the Brzozowski derivative, but isomorphic:
-- we return a list of re's instead of an re.
deriv :: Char -> RE -> [RE]
deriv c Empty       = []
deriv c (Lit c')    = if c == c' then [Empty] else []
deriv c (Seq r s)   = [compose r' s | r' <- deriv c r]
deriv c (Alt r s)   = deriv c r ++ deriv c s
deriv c rp@(Plus r) = dr ++ [compose r' rp | r' <- dr]
                      where dr = deriv c r

compose :: RE -> RE -> RE
compose Empty s = s
compose r s = Seq r s
