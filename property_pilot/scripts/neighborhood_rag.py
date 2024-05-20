# Importing required libraries
import pandas as pd
import numpy as np
import numpy.linalg
from google.api_core import retry
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel

def generate_prompt_rag_neighborhood(instruction, context, user_query):
    instruction = instruction.replace("{CONTEXT}", context)
    return instruction.replace("{USER_QUERY}", user_query)

embeddings_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

# Compute the cosine similarity of two vectors, wrap as returned function to make easier to use with Pandas
def get_similarity_fn(query_vector):
    def fn(row):
        return np.dot(row, query_vector) / (
            numpy.linalg.norm(row) * numpy.linalg.norm(query_vector)
        )

    return fn

# Retrieve embeddings from the specified model with retry logic
@retry.Retry(timeout=300.0)
def get_embeddings(text):
    return embeddings_model.get_embeddings([text])[0].values

def get_context(question, vector_store, num_docs):
    # Embed the search query
    query_vector = np.array(get_embeddings(question))

    # Get similarity to all other vectors and sort, cut off at num_docs
    top_matched = (
        vector_store["embeddings"]
        .apply(get_similarity_fn(query_vector))
        .sort_values(ascending=False)[:num_docs]
        .index
    )
    top_matched_df = vector_store[vector_store.index.isin(top_matched)][["texts"]]

    # Return a string with the top matches
    context = " ".join(top_matched_df.texts.values)
    return context