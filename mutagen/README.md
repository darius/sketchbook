Based on http://www.eblong.com/zarf/mutagen/about.html

This generates random text from specifications like 
http://www.eblong.com/zarf/mutagen/goreyfate.js
(only in Python instead of Javascript).

A newer system along similar lines is
https://github.com/galaxykate/tracery
which also has a Python port:
https://github.com/aparrish/pytracery

I've also made up a concrete syntax for grammars like this, to write
them 'directly' instead of as code in Python or Javascript:
https://github.com/darius/radiation
For example, here's what the above goreyfate.js looks like:
https://github.com/darius/radiation/blob/master/mutagen_grammar.js#L125
