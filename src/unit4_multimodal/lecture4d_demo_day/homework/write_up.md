# Final Project

## Project Overview

My project is a study assistant web-app. I wanted to make a system that would allow students to upload their class
notes, class slides, and study guides, and then use those items as the basis for an agentic study agent. The MVP of this
project is a web-app that has the potential to upload multiple documents and then use those with a chat and to create
flashcards. The MVP only has minimal OCR capabilities, so it only works for classes that have simple notation like art
history or philosophy. The MVP was designed around making it demo-able for the art history class I am currently enrolled
in. Here is a sample workflow: The user creates a class using the class creation button. The user then uploads the
documents for that class. They are ingested (see [RAG System](#rag-system)) and then the user can use the chat or
create flashcards feature. The chat and flashcard generation features relies heavily on the RAG system by querying the
vector database (CromaDB). For more information on hpw the flashcard generation feature works see
[Agent-as-Judge](#agent-as-judge). This project uses several of the concepts discussed over the course of the semester;
however, the three I will focus on in my write-up are its use of agent-assisted coding, a RAG system, and the use of an
agent-as-judge infrastructure.

## Agentic Principles

### Agent-Assisted Coding

From the beginning, I knew that I wanted to build an agentic study agent. Before I started coding, I spent over three
hours planning with an LLM to get my initial design document established. I used Perplexity's research mode to
accomplish this. I spent time discussing my goals for my project and then determining which frameworks would be most
effective for its implementation. I talked through the frameworks we were using in the class like ChromaDB and Gradio.
Also in the design process, I established phases that would be used to achieve the MVP that I was working towards. This
step was effective at helping me establish what was in-scope and what was out of scope. I then used this design document
along with Claude code to work on this project. Throughout the building process, I did deviate from the design as I
experienced elements that should be adapted to work another way. I feel like the final product speaks for itself. It is
a neat, organized webapp that has demo-able MVP functionality.

### RAG System

When building the chat feature, I knew that I wanted it to be built primarily on a RAG system so that users could be
confident that their conversations were accurate to the course materials. This process involved a lot of challenges. The
largest of which was the ineffective querying of the vector database. This was occurring because during the upload step
it wasn't injesting the information effectively. This took some major tinkering to fix. Initially I tried refining the
querying system by changing its parameters and making the prompt very strong and clear. These changes only had minimal
effect. That is when I changed my approach. The new system now takes the inputted files and breaks them down into
headings and subheadings. This way, the RAG model is more effective at pulling relevant information. After testing, this
has been shown to give a significant improvement. Now, when asking a question that applies in part to multiple sections,
the model will respond back with an accurate response that is accurate and contains all the relevant information.

### Agent-as-Judge

As I was working on the flashcard generation feature, I consistently ran into a problem. The problem was that I couldn't
get an accurate set of flashcards for a user defined topic. This was occurring because as I was prompt engineering the
flashcard information retrieval prompt, it worked like a pendulum and swung one of two ways. If the retrieval prompt was
strict, it would accurately only contain relevant terms; however, it would be missing some terms. On the other
appendage, if I made the prompt less strict, the retrieval system would end up including inaccurate flashcards that did
not match the user's specific request. To solve this problem, I set up an agent-as-judge system. I had the retrieval
system utilize a less strict prompt so that all relevant terms would be included with a few false positives. Then I feed
the flashcards into another system that filters out the irrelevant flashcards. This process took some work properly.
Initially it took too long to run both the retrieval and cleaning steps. I modified my solution, so that the retrieval
was more stream lined. This was a reasonable solution because the judge system was effective at removing unrelated
cards, and it could do that faster than the initial construction step could assemble a list of valid flashcards. In the
finished project, the flashcard generation system is now reasonably quick (it takes about a minute and a half) and it
constructs a collection of all the valid terms based on the user's request.

## Reflection

I learned a lot from the implementation of this project. The thing that was most impactful was the ability to taking
something that I could outline conceptually, transform that into a specific design description, and then build it in a
matter of hours. Something that people find amusing is that I am a computer science major who doesn't particularly enjoy
writing code. I like reading code, debugging code, coming up with ideas for code, and talking about code; however, I
find the process of typing out each line of code laborious. This is probably because am a perfectionist and I want every
line to be based on industry the best practice so a single line may take me as lon as 15 minutes. The difference with
this class is I was able to develop personal skills and agentic skills that allowed me to offload that part of
programming. It was a really neat experience, and it makes me very excited to build more projects moving forward.

Something I learned in particular in this class is how ineffective agentic coding tools are if you do not give them
direction. It brings to mind the expression, "If you don't know where you are going, any road will get you there." I
have come to appreciate the fact that good agent written code requires a high level of determination and intent from the
individual utilizing the tool. This came up a lot during the debugging process. When Claude code would recommend a
solution, nine times out of ten, it would be recommending a change that would be classified as a patch rather than a
solution. To get it to give me an effective solution I would have to prompt it and provide additional information about
my goals. I know that AI advances further this will become less important in some ways; however, I am currently
confident that determination and vision are the most important traits of people who will make effective agentic
engineers.

The most challenging part of this project was how draining agentic-assisted coding is. In classical coding, you make an
architectural plan for about 2 hours, and then you spend about 5 hours coding up that section of the project. The
architecting part is very mentally intensive, but the coding part is slow and almost mindless (even including good
documentation and coding practices). With agent-assisted programming, it is the thinking part the whole time (minus the
15 to 30 minutes it takes to code the thing). I like this shift because it makes coding a more thinking intensive
process. The downside is after a few hours of agentic programming I get as drained as if I had spend a day classic
programming. On the bright side, I can take a break and then be back at it later that same day. It just is challenging
because it takes a lot out of you.

I think the easiest part of this project was the framework steps. Normally when I am programming something, I spend a
long time learning the best practice for each little thing in that language, now I can request AI to use the best
practice and then ask it why it made the decisions it did. I think all the pieces that I initially set out to build are
functioning as nicely as I wanted them to. Moving forward, the only thing I would do differently is building my UI in a
way that it won't look like all the other agent-coded UIs. That is what I will look into moving forward. My friend and I
have been discussing designing a skill set up to design a webpage in a distinctive style for a person. The idea is that
the developer can develop a style for themselves and then that will be the standard for their pages.

## Testing

If you want to see the demo I performed load the web-app using the setup instructions in the readme. Then upload the
`example_study_guide.md` I have attached as a study guide. Then in the chat you can ask questions like, "Who is Jan van
Eyck". In the flashcard generation section you can set a topic like "Artists."