# Lecture 3e

## Part 1: Harness Engineering

I spent several hours building an OWASP strike team that would be able to analyze a repository for any of the OWASP top
10 vulnerabilities and to propose suggested smart fixes. The idea was to build a plug and play system that could
accurately delegate each of the vulnerabilities to team members and then perform an effective sweep on the code base. To
test it I used Claude code to build a sample codebase with vulnerabilities to test it. I worked in parts by building an
initial team that could handle three op the top 10 OWASP security vulnerabilities. I started with a simple app
repository with some simple errors and the harness performed correctly, and then I pointed it at a more sophisticated
repo with more hidden errors. I had Claude Code summarize the process and findings in `session-summary.md`. One key
takeaway is the performance difference between the models.

I then ran it on my chess repository from cs240 and my friend's query crafting project to see how it performs on normal
repositories.

## Part 2: Project Progress

I successfully set up the RAG model chat function with a web-search tool. Something I learned is that in text entry
gradio does not support the intuitive chat typing involving an enter meaning send and a shift-enter meaning new line.
The cool part about doing this in an agent assisted coding way, it makes it, so I was able to learn that only 30 min
into playing around with it, so I don't have to take 3 hours to learn that limitation. It also took some modification to
make it so that the chat would use the correct spelling of terms even when the user was spelling them wrong. It is
really cool to have the functioning chatbot with RAG integration now. The next step is to make it possible to have the
model generate flash cards for the course materials.
