# Homework 2a

## Part 1: Reviewing In-Class Code

I initially played around with the provided code from the in-class examples. I was trying to see how I
could successfully query the first Nephi verses to find relevant verses. I found that if my query only
had one word like 'fruit' It didn't return any matches. This is probably because a small query matches
too many things so it is unable to find a valid match that met the threshold of 0.32. I also looked at
the relative embeddings and which words/phrases are embedded as being similar.

## Part 2: Playing Around with Embeddings

To play around with the code more, I tried embedding the TRON 1982 script. Breaking apart the script by
lines wasn't very effective for querying the script. It made it so character's names could flood the
list of valid responses. When I played around with the embedding size I found that the larger I made
the embeddings the more vague I had to make the queries to find matching.

## Further Study

I wonder if it is possible to find two embeddings that are orthogonal. If I could find them, it would
be interesting to see if that reveals anything about the two sets of information.