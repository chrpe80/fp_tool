# About

## Background
I am an occupational therapist turned Python developer specializing in AI. 
In this project, I drew from my experience working as an occupational therapist to
find ideas for tools that can help other practitioners.

## The project
Something I have always struggled with is to find the right KVÅ code for my
texts. I also wanted to get better at "förskrivnings-processen" as described by
[Socialstyrelsen](https://www.socialstyrelsen.se/globalassets/sharepoint-dokument/artikelkatalog/ovrigt/2021-12-7673).

## What the program does
It takes a text as input, corrects spelling and grammar, divides it into paragraphs,
and then it recommends a suitable KVÅ code based on the ["Åtgärdsregistrering inom arbetsterapi"](https://www.socialstyrelsen.se/globalassets/sharepoint-dokument/dokument-webb/klassifikationer-och-koder/kva-lathund-arbetsterapi.pdf).
It also returns the corrected text.

## Tech

* Python
* FLASK
* Spacy
* Sapling
* Langchain
* OpenAI (gpt-4o-mini, text-embedding-3-large)
* Dotenv
* HTML
* CSS
* Pycharm

# Testing
All Python functions have been tested using the Python unittest library, and the website has been tested manually.

# Future

I am going to learn to finetune a model from Huggingface to reduce the cost of using the website. I will also look deeper into the security aspect of AI.

