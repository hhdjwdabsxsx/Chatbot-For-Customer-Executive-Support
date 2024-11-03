# -----------------------------------------------------------------C.L.E.A.N---------------------------------------------------------------------------------------
# --------------------------------------------Clothing.Laundry.Efficiency.and.Automation.Network-------------------------------------------------------------------

import json
import spacy
from sentence_transformers import SentenceTransformer, util
import string
import torch

# Check if GPU is available, if not fall back to CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Load Sentence-BERT model for similarity matching
model = SentenceTransformer("paraphrase-MiniLM-L6-v2").to(device)

def load_knowledge_base(file_path: str) -> dict:
    """Load the knowledge base from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        # Ensure the JSON has the expected structure
        if "questions" not in data or not isinstance(data["questions"], list):
            raise ValueError("JSON file is missing 'questions' or it is not a list.")
        return data
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error loading knowledge base: {e}")
        return None

knowledge_base = load_knowledge_base("customer_support_faq.json")


def preprocess_input(user_input: str) -> str:
    """Preprocess the user input using spaCy to remove punctuation, tokenize, and lemmatize."""
    # Convert input to lowercase
    user_input = user_input.lower()
    # Process the input with spaCy
    doc = nlp(user_input)
    # Lemmatize and remove punctuation
    tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_stop]
    return " ".join(tokens)

def calculate_similarity(user_input: str, knowledge_base: dict, threshold: float = 0.5) -> str:
    """Calculate similarity between user input and questions in the knowledge base using Sentence-BERT."""
    # Encode the user input and knowledge base questions into embeddings
    input_embedding = model.encode(user_input, convert_to_tensor=True, device=device)
    questions = [item["question"] for item in knowledge_base["questions"]]
    question_embeddings = model.encode(questions, convert_to_tensor=True, device=device)

    # Calculate the cosine similarity between the input and the questions
    similarities = util.pytorch_cos_sim(input_embedding, question_embeddings)

    # Find the most similar question
    best_match_idx = similarities.argmax()
    best_match_score = similarities[0, best_match_idx].item()

    # If the similarity score is below the threshold, return a default response
    if best_match_score < threshold:
        return "I'm sorry, I don't have information on that. Please ask something related to Dhobi G services."

    # Otherwise, return the corresponding answer
    return knowledge_base["questions"][best_match_idx]["answer"]

def generate_response(user_input: str) -> str:
    """Generate a response using the chatbot logic."""
    if not knowledge_base:
        return "Knowledge base could not be loaded."
    
    processed_input = preprocess_input(user_input)
    return calculate_similarity(processed_input, knowledge_base)

