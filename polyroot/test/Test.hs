{-# OPTIONS_GHC -fno-warn-orphans #-}
import Test.QuickCheck
import Polyroot

instance Arbitrary Polynomial where
  arbitrary = do
    coeffs <- arbitrary
    return $ Polynomial coeffs

prop_derivativeHasLowerDegree :: Polynomial -> Bool
prop_derivativeHasLowerDegree p =
    degree p == 0 || degree p == degree (derivative p) + 1
      where degree (Polynomial coeffs) = 0 `max` (length coeffs - 1)

main :: IO ()
main = do
  putStrLn "prop_derivativeHasLowerDegree"; quickCheck prop_derivativeHasLowerDegree
