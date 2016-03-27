module Main where

import Data.AEq
import Data.Complex

type Value = Complex Double
data Polynomial = Polynomial [Value] -- coefficients in decreasing order of degree
  deriving Show

value :: Polynomial -> Value -> Value
value (Polynomial coeffs) x = foldl step 0 coeffs
  where step accum coeff = accum * x + coeff

derivative :: Polynomial -> Polynomial
oldderivative (Polynomial coeffs) = Polynomial (deriv coeffs)
  where deriv [] = []
        deriv [c] = []
        deriv (c:cs) = (c * fromIntegral (length cs)) : deriv cs     -- XXX inefficient

derivative (Polynomial coeffs) = Polynomial deriv
  where deriv = case reverse coeffs of
                  [] -> []
                  _:rc -> reverse $ zipWith (*) rc (map fromIntegral [1..])  -- XXX untested

-- Successive approximations to a root by Newton's method, taking the starting guess from the last argument.
newton :: Polynomial -> Value -> [Value]
newton p = iterate improve
  where improve z = z - value p z / value dp z
        dp = derivative p

findFixpoint :: [Value] -> Value
findFixpoint (z0:z1:zs) = if z0 ~== z1
                          then z1
                          else findFixpoint (z1:zs)

findRoot p z = findFixpoint (newton p z)

-- TODO:
-- how to handle nonconvergence? add a bit of randomness at each step? random restarts?
-- I/O in main
-- tests or something
-- split main from library

main :: IO ()
main = do
  putStrLn "hello world"
