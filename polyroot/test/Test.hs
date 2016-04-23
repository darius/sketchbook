import Test.QuickCheck

propYay = True

propBoo = False

runSuite = mapM runTest 

runTest (name, test) = do
  putStrLn name
  quickCheck test

main = 
  runSuite [("yay", propYay),
            ("boo", propBoo)]
