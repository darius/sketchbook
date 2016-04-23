module Polyroot where

import Data.AEq
import Data.Complex

type Value = Complex Double
data Polynomial = Polynomial [Value] -- coefficients in decreasing order of degree
  deriving Show

-- Evaluate a polynomial at a point z. Uses Horner's rule.
value :: Polynomial -> Value -> Value
value (Polynomial coeffs) z = foldl step 0 coeffs
  where step accum coeff = accum * z + coeff

-- The rate of change of a polynomial is a polynomial of next-lower
-- degree.
derivative :: Polynomial -> Polynomial
oldderivative (Polynomial coeffs) = Polynomial (deriv coeffs)
  where deriv [] = []
        deriv [c] = []
        deriv (c:cs) = (c * fromIntegral (length cs)) : deriv cs     -- XXX inefficient

derivative (Polynomial coeffs) = Polynomial deriv
  where deriv = case reverse coeffs of
                  [] -> []
                  _:rc -> reverse $ zipWith (*) rc (map fromIntegral [1..])  -- XXX untested

-- Successive approximations to a root by Newton's method, taking the
-- starting guess from the last argument.
newton :: Polynomial -> Value -> [Value]
newton p = iterate improve
  where improve z = z - value p z / value dp z
        dp = derivative p

-- The first approximate repeat in successive elements.
findFixpoint :: [Value] -> Value
findFixpoint (z0:z1:zs) = if z0 ~== z1
                          then z1
                          else findFixpoint (z1:zs)

-- A value z' near the z'' where value p z'' would be 0 if we were
-- using infinite-precision real numbers. (For some inputs the current
-- implementation won't terminate, even though z'' would exist.)
findRoot p z = findFixpoint (newton p z)

-- TODO:
-- how to handle nonconvergence? add a bit of randomness at each step? random restarts?
-- I/O in main
-- tests or something
