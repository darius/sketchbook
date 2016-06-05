module Main where

import System.Environment
import Polyroot

main :: IO ()
main = do
  args <- getArgs
  let (seed : coeffs) = map read args
  putStrLn $ show $ findRoot (Polynomial coeffs) seed
