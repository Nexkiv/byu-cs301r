# Lecture 4a

## Part 1: Image Generation Practice

Based on the in-class discussion we talked about how models perform when they are tasked with generating images that
contain several distinct styles together. I initially tested this by providing the llm with this prompt: "A
self-portrait of Jan Van Eick, Van Goh, and Raphael, all in their original styles in an art gallery." This way I could
establish boundaries between the styles. This performed reasonably well. Next I have it this prompt: "A business meeting
with Jan Van Eick, Van Goh, and Raphael, all in their original styles in attendance." This also worked for the most
part, and I found that a little surprising. One interesting note though is that all of their hands look to be in the
same art style. I then tried to merge the painted people styles with a photorealistic style with this prompt: "A
business meeting with Jan Van Eick, Van Goh, and a photorealiastc traditional tube man uses an electrical fan blowing
air through a lightweight fabric sleeve to create its signature flailing motion, all in their original styles in
attendance." This resulted in a poor blending of styles with the model defaulting to a blend of Van Eick's and Van Goh's
style.

## Part 2: Explore Image Information Extraction

To play around with image information extraction I gave the model an example of an image with Greek handwriting. I then
asked it to extract the information. I don't think it has access to OCR libraries, so I used this to test its
out-of-the-box capabilities. It was surprisingly effective at this. One thing of note was that in its transcription it
separated out reach handwritten line into a new line. This makes sense for a true to document transcription; however, it
may have resulted in more difficulty for the translation. It did successfully transcribe around crossed out words. This
is something I will have to play around with in the future.

## Part 3: Project Progress

Following up with where I left off in the last section. I continued using the web-extension llm assistant to analyze the
UI/UX of the webpage. This resulted in it pointing out some features that were a little out of scope, but would be good
quality of life improvements. Some of these included hovering colors, and splitting the page into different parts,
separating out each flashcard set, manual editing of or removing of single flashcards, or consistent drop down menus. I
implemented these changes. The assistant also gave other recommendations that were out of scope like enabling
keyboard-shortcuts or mass file upload. This process was a good experiment into keeping to goals and staying within a
scop of a project. The current state of the project I feel is presentation worthy; however, there are still some things
I would like to work on like improving the effectiveness of the RAG system in pulling from the class document and
implementing some kind of memory for the chat feature to persist across sessions.