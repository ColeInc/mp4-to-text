# MP4 to Text Converter

Simple tool which lets you paste an mp4 file into a directory, extracts the transcript from the mp4 file, lints the grammar of the text, then outputs it in a .txt file.

Uses Google's Gemini API to format the video's transcript in human readable english, with corresponding paragraphs, syntax and spacing.

## Setup

- Need to create a Gemini API Key which can be done by following the steps [here](https://ai.google.dev/gemini-api/docs/api-key)
- Create a new environment variable in your .env called GEMINI_API_KEY with your corresponding API key.
