-- E.g.: (lit 'a' . many (lit 'b' `alt` lit 'c') . lit 'd') `matches` "abbcd"
-- Like Thompson: doesn't dedup the states, and loops forever on (a*)*.
-- Unlike Thompson there's no 'fork' node in the compiled graph, which
-- in consequence may be asymptotically bigger.

data State = Accept | Expect Char [State]
  deriving Eq

after _ Accept             = []
after c (Expect c' states) = if c' == c then states else []

step states c = concat $ map (after c) states

re `matches` cs = Accept `elem` foldl step (re [Accept]) cs

lit c       states = [Expect c states]
alt re1 re2 states = re1 states ++ re2 states
many re     states = loop where loop = states ++ re loop
