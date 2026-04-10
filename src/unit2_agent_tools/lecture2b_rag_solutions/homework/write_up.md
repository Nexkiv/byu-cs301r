## Lecture 2b

[//]: # (Future reference: I saved the General Conference Talks at `../../../shared/text/gc`)

## Part 1: Playing with the class code

I downloaded the Oct. 2025 General Conference talks using the downloader tool. I also downloaded the April 1971 talks to
do some comparison. I experienced an error when playing around with the provided code that occurred because my chromadb
version wasn't updated. I then ingested the general conference addresses using the default parameters.

## Part 2: Playing with the chatbot

Using claude, I built a chatbot to the lab specifications, I also imported the usage.md file we were using in unit 1.
I started with all the default embedding setting, and it seemed to work reasonably well. (see `chat_10-41-34.md`)
However, after playing around with my chatbot, I found that the chatbot would hallucinate a previous conversation. I
next played around with a larger chunk size. When I doubled the chunk size it did not seem to have a noticeable effect.
I then increased the chunk size to 5000, resulting in only 79 chunks. This also didn't seem to have a major effect on
the results. Something interesting I found was that when asked to summarize the conference's main themes it only pulled
from two talks.

For testing in the extreme, I then experimented with a chunk size of 150 which resulted in 23323 chunks. It worked
intermittedly with sometimes it could handle the RAG model information and other times it would crash because it was too
much information for the api to handle. When it did work, it gave different responses than the same questions with
larger chunk sizes.

I messed around with the prompt size and complexity and found that by making the prompt more restrictive, the responses
became more regimented. (compare `chat_10-41-34.md` with `chat_21-26-19`) I also found through testing that the return
values of the RAG model with the vector database was non-deterministic. This surprised me, I had initially assumed that
the talks given the same chunk size would then correspond to the same questions with the same embeddings, but
surprisingly not.

## Further study

I didn't play around with the number of chunks returned by the model, I just left it at a default value of 3. I am
curious how increasing that value would affect the responses or if it would at all. 