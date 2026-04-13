# Lecture 3g

## Part 1: What I learned from [OpenAI's evals page](https://developers.openai.com/api/docs/guides/evals)

Reading this page was interesting, because in my machine learning class these are the types of things we are discussing
for our models and how they can be evaluated. The vibe that I was getting from the evals description was its intent to
ins some way monitor the LLM's performance. Something interesting is that it enables individuals to define what
"correct" or "good" looks like. so that there is a reliable testable performance metric. OpenAI outlines that they have
two different grading systems depending on if the response can be deterministically graded or not. This is similar to
the LLM Evaluation Quadrants we discussed in class. The LLM-as-a-Judge system a validation endpoint that can be used to
experiment with grading prompts so that the judge's system is more consistent. It seems that building a system with LLM
graders has many advantages; however, meta-grading still is something that will have to be done at some point along in
the process.

*Side note*: On their page OpenAi made the distinction between evals and datasets as evals are for evaluating against
external models or on a larger scale while datasets are a more iterative environment to create evaluations that set up
initial test prompts.

## Part 2: Project progress

At this point in my projects development, I decided to look into the UI and see if I could make it a better user
experience based on the Gradio format. The resulting page is okay, so the next thing I do will most likely be a
migration from Gradio to something like Flask + Tailwind CSS + HTML because that is what Gradio recommends. I will look
into that. Along with the Gradio visual improvements, I added initial OCR support for documents like PDFs to improve the
knowledge base of the RAG system. I also modified the way that the system build the flashcards to reduce hallucinations;
however, I will need to rework the way that the model builds the flashcards from the RAG system, because it currently is
ineffective at it. All in all, I have been learning a lot about designing systems that function visibly well and are
intuitive for use (things which Gradio can only partially provide).