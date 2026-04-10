# Lecture 2d

## Part 1: Building Tools and Chatbot

I started by building a new version of the `chatbot.py` that now has access to tool calls. I added a debug mode that
outputs all the tool calls to the terminal so that the user can see them being used and their responses. When I tried
playing around with the chatbot initially, I found that it wasn't making the tool calls. I fixed this by adding better
descriptions ot my tools and modifying my system prompt. It also took some modification to get the `--debug`
functionality to work correctly.

## Part 2: Playing around with Tools

The primality testing tool I wrote was called when it should, but the ratio tool went uncalled even in circumstances
when it should have been (see `chat_18-04-20.md`). It took several iterations on this process ot get the model to start
using the tool calls. I didn't get it to work every time, but I did start to get better results.

## Part 3: URL Functionality

The ability to retrieve content using a url seems to be working well (see `chat_19-33-45.md`). I was able to get it to
be able to find popular conference quotes; however, I couldn't get it to follow my instructions to search the Church's
general conference page to find the content..

## Further Study

I think there should be a way to hone-in the web_search tool to constrain the model to a limited portion of the
internet. That is something that I will play around with in the future.