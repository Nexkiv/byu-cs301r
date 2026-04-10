# Lecture 2c

## Overview

The article that I chose to read about RAG models was,
[Path to high-quality LLM-based Dasher support automation](https://careersatdoordash.com/blog/large-language-modules-based-dasher-support-automation/),
a blog post made in September 2024 on DoorDash's adoption plan for a RAG system.

Within the blog post, it explained DoorDash's motivation for enhancing the current Dasher, the delivery drivers, support
system using LLMs. They pointed out, however, that finding the source with the correct information and finding it in the
Dasher's language was a major hurdle they were facing. That is why they implemented their RAG system.

The problems that they were attempting to solve were:

* Groundedness and relevance of responses in RAG system
* Context summarization accuracy
* Language consistency in responses
* Consistent action and response
* Latency

## System

They implemented the following system, which works in a similar way to the RAG systems that we talked about in class:

```text
==========================================================================================================
                                      RAG-Based Support System
==========================================================================================================

 [ USER INTERFACE ]
   +--------------+                                  +------------------+
   |  User Query  |                                  | Response to User |<------------+
   +------+-------+                                  +------------------+             |
          |                                                                           |
----------|---------------------------------------------------------------------------|-------------------
 [ LLM USER SUPPORT SYSTEM ]                                                          |
          v                                                                           |
   +--------------+    +------------+     +-----------+       +---------------+       |  +-------------+
   |              |    |            |     | Retrieval |  Yes  |               |       +->|  Case Data  |
   | Summarization|--->| RAG System |---->| Success?  |------>| LLM Guardrail |       |  |  (Database) |
   |              |    |            |     +-----+-----+       |               |       |  +------+------+
   +------+-------+    +------+-----+           |             +-------+-------+       |         |
          ^                   ^                 | No                  |               |         |
          |                   |                 |                     v               |         |
          |                   |                 |             +---------------+  Yes  |         v
          |                   |                 |             |  Is response  |-------+  +--------------+
          |                   |                 |             |     good?     |          | LLM as Judge |
          |                   |                 |             +-------+-------+          +------+-------+
          |                   |                 |                     | No                      |
          |                   |                 |                     |                         |
----------|-------------------|-----------------|---------------------|-------------------------|---------
 [ META DATA ]                |        |        | [ DEVELOPERS ]      |                         |
   +------+-------+    +------+-----+  |        v                     v                         v
   | Case Context |    | Knowledge  |  |  +-----------+         +-----------+             +-------------+
   |              |    | Base (DB)  |<-|--|  Expert   |         |   Human   |             | Engineering |
   +--------------+    +------------+  |  |  Review   |         |   Agent   |             | Improvements|
                                       |  +-----------+         +-----------+             +-------------+
```

## Insights

Something that I found interesting was their way of implementing the LLM-as-Judge system to perform quality improvement.
Way it worked was by converting open-ended answers to multiple-choice questions and then using those to judge its
accuracy. This makes a lot of sense because open-ended answers are always naturally vague in their accuracy because of
the 'there is no right answer' kind of format. I think it is a creative solution to convert them to multiple choice
responses because those would have a correct answer, or at the very least a most correct answer.