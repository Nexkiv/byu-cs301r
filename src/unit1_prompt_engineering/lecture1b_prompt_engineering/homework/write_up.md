# Homework 1b

## Part 1: Build better basic completion apps than in 1a.

It took me a while to be able to successfully force the llm to return structured output based on the
schema provided. Or at least it took a long time to format and pass in the schema successfully. I took
inspiration from the 3a homework which I hope is okay to get it right in the end.

The output is still nondeterministic for vague prompts. Something Interesting I found is that the llm
would use the provided schema also as a type of prompt. I gave the llm the list of things to classify
and no further instructions. I then gave a schema that had two specific groups defined and the llm
automatically grouped the things into those two groups.

When the two provided groups had nothing to do with the provided objects the llm would have random
response which is an expected error. By providing a schema in addition to the token predicting powers
of LLMs makes structured output a very useful tool in categorizing elements.

The code writing is about the same as the previous assignment; however, by proving a schema it makes
it easier to separate the code itself from a summary. This is very beneficial because during the last
assignment the code that was generated would have verbose comments that made it hard to read. The
comments were helpful for understanding the code, but they were unnecessary for implementation.

## Further Study

I still want to look into the alternate language capabilities of LLMs in this context, but I need to get
to sleep and I have spent three hours on this assignment. I think it would be cool to try to classify
objects into categories defined in other languages.