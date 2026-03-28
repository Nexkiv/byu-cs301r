# Lecture 1e

## Part 0: Set Up

I modified my working chat-bot to be able to store handle different levels of reasoning and then record those in the
saved .md files.

## Part 1: Try reasoning models on basic tasks

I initially started with some basic math problems and then asked a few trickier ones.
Answer key:

1. 1 + 17 = 18
2. sqrt(10! / 7) = 720
3. 53^31 (mod 7) = 4
4. is 25707225491 prime? = yes
5. factor 25505418241 = 1021 * 3061 * 8161

The minimal reasoning model solved 1 and 2. `chat_17-07-34.md`
The low reasoning model solved 1,2, and 3. `chat_17-09-07.md`
The high reasoning model was able to solve all of them except 5. `chat_17-22-29.md`

I then gave it two logic puzzles I found online:

### Medium difficulty

Hans Ernest Froopaloop, Jr. will marry one of three women: Audrey, Brenda, and Charlotte. Here are the facts: 1. Of
Audrey and Brenda: a. Either they both have blue eyes or neither has blue eyes. b. One has red hair and the other does
not. 2. Of Audrey and Charlotte: a. Either they both have red hair or neither has red hair. b. One is 5'11" and the
other is not. 3. Of Brenda and Charlotte: a. One has blue eyes and the other does not. b. One is 5'11" and the other is
not. 4. Of the three characteristics—blue eyes, red hair, and 5'11"—a. If any of the three women has exactly two of the
three characteristics, Mr. Froopaloop will marry the one with the least number of characteristics. b. If any of the
three women has exactly one of the three characteristics, Mr. Froopaloop will marry the one with the greatest number of
characteristics. Who will Mr. Froopaloop marry?

Answer: Charlotte

The minimal reasoning model could not solve the puzzle, but the low reasoning model could. `chat_17-18-16.md`,
`chat_17-19-34.md`

### Hard Difficulty

There is a ten-digit mystery number (no leading 0), represented by ABCDEFGHIJ, where each numeral 0 through 9 is used
once. Given the following clues, what is the number? 1) A + B + C + D + E is a multiple of 6. 2) F + G + H + I + J is a
multiple of 5. 3) A + C + E + G + I is a multiple of 9. 4) B + D + F + H + J is a multiple of 2. 5) AB is a multiple of
3 . 6) CD is a multiple of 4. 7) EF is a multiple of 7. 8) GH is a multiple of 8. 9) IJ is a multiple of 10. 10) FE, HC,
and JA are all prime numbers.

Answer: 5736912480

Minimal reasoning was unsuccessful. `chat_17-35-40.md`
Low reasoning was unsuccessful. `chat_17-38-45.md`
High reasoning was successful. `chat_17-46-23.md`

## Part 2: How much more expensive are responses with reasoning enabled?

The quantifications of the response time and costs are in the chat `.md` files.
The high reasoning model was able to do really well even on the tricky math and logic problems; however, that success
came at a cost. It looks like going from minimal reasoning to low reasoning is a 5x to 10x time increase and then
another 25x to 50x increase when going up to a high reasoning model. That is my intuition for it.

## Part 3: Read the Claude Constitution news release

I read the news release and part of the constitution and have discussed them with my friends and in class.

## Future Study

I wonder how effective reasoning models are at handling novel unsolved problems.
Will they get caught up in their confidence and give a false answer or will they determine that they are incapability of
solving for the answer?