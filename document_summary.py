import os
from docx import Document
import openai

# Load your OpenAI API key from an environment variable or another secure location
openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_word_document(file_path):
    doc = Document(file_path)
    full_text = []

    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)

    text = '\n'.join(full_text)

    # Ensure the text is within the limits of the API's input size.
    if len(text) > 4096:
        text = text[:4096]

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following document:\n\n{text}",
        max_tokens=150
    )

    summary = response.choices[0].text.strip()
    return summary