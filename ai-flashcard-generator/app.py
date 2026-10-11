import json
import os

import streamlit as st
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


# Load environment variables from .env
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL")


# Configure the Streamlit page
st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="📚",
    layout="centered"
)


# Application heading
st.title("📚 AI Flashcard Generator")

st.write(
    "Generate question-and-answer flashcards "
    "from your study topics or notes."
)


# Collect user input
topic = st.text_input(
    "Enter your topic",
    placeholder="Example: Photosynthesis"
)

notes = st.text_area(
    "Paste your study notes (optional)",
    placeholder="Paste your notes here..."
)

number_of_cards = st.slider(
    "Number of flashcards",
    min_value=3,
    max_value=15,
    value=5
)


def generate_flashcards(topic, notes, number_of_cards):
    """Generate flashcards using a Hugging Face model."""

    if not HF_TOKEN:
        raise ValueError(
            "HF_TOKEN is missing. Add your token to the .env file."
        )

    if not HF_MODEL:
        raise ValueError(
            "HF_MODEL is missing. Add a compatible model ID to .env."
        )

    client = InferenceClient(
        model=HF_MODEL,
        token=HF_TOKEN
    )

    source_text = notes.strip() if notes.strip() else topic.strip()

    prompt = f"""
You are an educational assistant.

Create exactly {number_of_cards} useful study flashcards
based on the material provided below.

Requirements:
1. Each flashcard must contain a question and an answer.
2. Keep questions clear and specific.
3. Keep answers accurate and concise.
4. Return only valid JSON.
5. Do not include Markdown code fences.

Use this exact JSON structure:
{{
    "flashcards": [
        {{
            "question": "Question text",
            "answer": "Answer text"
        }}
    ]
}}

Study material:
{source_text}
"""

    response = client.chat_completion(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=2000,
        temperature=0.4
    )

    generated_text = response.choices[0].message.content

    if not generated_text:
        raise ValueError("The model returned an empty response.")

    # Extract JSON if the model includes surrounding text.
    start = generated_text.find("{")
    end = generated_text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "The model did not return a valid JSON object."
        )

    json_text = generated_text[start:end + 1]

    data = json.loads(json_text)

    flashcards = data.get("flashcards")

    if not isinstance(flashcards, list) or not flashcards:
        raise ValueError(
            "The response does not contain any flashcards."
        )

    # Validate the generated cards.
    valid_cards = []

    for card in flashcards:
        if not isinstance(card, dict):
            continue

        question = card.get("question")
        answer = card.get("answer")

        if (
            isinstance(question, str)
            and isinstance(answer, str)
            and question.strip()
            and answer.strip()
        ):
            valid_cards.append(
                {
                    "question": question.strip(),
                    "answer": answer.strip()
                }
            )

    if not valid_cards:
        raise ValueError(
            "The model did not generate valid question-answer pairs."
        )

    return valid_cards[:number_of_cards]


# Generate flashcards when the button is clicked.
if st.button("Generate Flashcards", type="primary"):

    if not topic.strip() and not notes.strip():
        st.warning(
            "Please enter a topic or paste your study notes."
        )

    else:
        try:
            with st.spinner("Generating your flashcards..."):

                flashcards = generate_flashcards(
                    topic,
                    notes,
                    number_of_cards
                )

            st.session_state["flashcards"] = flashcards

        except Exception as error:
            st.error(
                f"Could not generate flashcards: {error}"
            )


# Display the generated flashcards.
if st.session_state.get("flashcards"):

    flashcards = st.session_state["flashcards"]

    st.subheader("Your Flashcards")

    for index, card in enumerate(flashcards, start=1):

        with st.expander(f"Flashcard {index}"):

            st.markdown("**Question**")

            st.write(card["question"])

            st.markdown("**Answer**")

            st.write(card["answer"])

    # Prepare a downloadable JSON file.
    download_data = json.dumps(
        {"flashcards": flashcards},
        indent=4,
        ensure_ascii=False
    )

    st.download_button(
        label="Download Flashcards as JSON",
        data=download_data,
        file_name="flashcards.json",
        mime="application/json"
    )