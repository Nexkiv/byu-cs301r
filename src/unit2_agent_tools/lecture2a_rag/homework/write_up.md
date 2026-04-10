# Homework 2a

## Part 1: Reviewing In-Class Code

I initially played around with the provided code from the in-class examples. I was trying to see how I could
successfully query the first Nephi verses to find relevant verses. I found that if my query only had one word like '
fruit' It didn't return any matches. This is probably because a small query matches too many things so it is unable to
find a valid match that met the threshold of 0.32. I also looked at the relative embeddings and which words/phrases are
embedded as being similar.

## Part 2: Playing Around with Embeddings

To play around with the code more, I tried embedding the TRON 1982 script. Breaking apart the script by lines wasn't
very effective for querying the script. It made it so character's names could flood the list of valid responses. When I
played around with the embedding size I found that the larger I made the embeddings the more vague I had to make the
queries to find matching.

## Part 3: Similar/Dissimilar Inputs

I generated a python script that would allow me to compare different inputs and their associated embeddings. The script
allowed me to compare the embeddings of two words. The first thing I played around with was movie titles. Star Wars and
Star Trek were seen as 0.6681 similar while Lord of the Rings and Hobbit were only 0.4616 similar. I then tried putting
in two well know presidential quotes, but they only had a similarity score of 0.1273. The next thing I played around
with was trying to find two embeddings of different words that had a similarity score over .95. In trying to reach that
goal I made a surprising discovery: the capitalization changes the embedding of a word/phrase. This makes sense when you
think about it. The circumstances in which 'yes' is used are not the same for when 'YES' is used. Also interesting:
'pg.' and 'page' only had a similarity score of 0.5569. The only time when I was able to exceed .95 was when I used the
same word twice which yielded a score of 1.0 (not surprisingly). (My script doesn't support international characters.)

## Further Study

I wonder if it is possible to find two embeddings that are orthogonal. If I could find them, it would be interesting to
see if that reveals anything about the two sets of information.