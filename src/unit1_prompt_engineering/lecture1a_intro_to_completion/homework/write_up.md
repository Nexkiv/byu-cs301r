# Homework 1a

## Part 1: Build a basic completion app.

I used the class text_processor.py for most of my completion app.
While working on it, I learned more about how Python imports worked in multi-
level file systems.

## Part 2: Try your app with different prompts.

### Classifier

With the classifier, I found that small changes to the prompt resulted in different classifications;
however, the general groups created for any given group of words will be about the same.
When I forced its number of groups down to two it gave about the same classification regardless of the
theming of the type of classifier it was described as.

### Code Generator

This is something interesting I noticed. When given the context that it was presenting a
seminar it gave me multiple sorting algorithm scripts even when I asked for 'a' script.
When I modified the target audience from new developers to first year students it changed from
giving a quicksort algorithm to a insertion sort algorithm because it is more 'intuitive'

## Part 3: Develop an intuition for the abilities and limitations of various models.

**Note: I am already 4 hours in to this homework assignment**

Some things that I have been playing around with is response times.
It seems like when I give the model a more significant role it will generate more tokens
compared to when I give it a more simplified role.

I played around with some numbers because LLMs are based on token prediction so they
do a poor job at solving problems that have symbolic deterministic answers.
gpt-5-nano did well at identifying famous and small prime numbers,
but when I gave it a big prime number it stopped giving me a straight answer.
When I forced it to answer with yes or no it would guess no for large number and
would be wrong. This makes sense because as numbers get larger primes become more sparse
so given a large number and asked if it is prime it will most likely not be.

## Further Study

In some of the later homeworks I think I will play around with language comprehension
especially greek-lish which is a version of Greek where the words are writen using latin characters.

