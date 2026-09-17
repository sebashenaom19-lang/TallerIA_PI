import os

import numpy as np
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie

# ✅ Carga la API Key de OpenAI
load_dotenv('../openAI.env')


def cosine_similarity(a, b):
    """Similitud de coseno entre dos vectores."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_embedding(prompt):
    """Genera el embedding del prompt escrito por el usuario."""
    client = OpenAI(api_key=os.environ.get('openai_apikey'))
    response = client.embeddings.create(
        input=[prompt],
        model="text-embedding-3-small",
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def recommendations(request):
    prompt = request.GET.get('prompt')
    best_movie = None
    max_similarity = None
    error = None

    if prompt:
        try:
            prompt_emb = get_embedding(prompt)

            # ✅ Recorre la base de datos comparando el embedding del prompt
            #    contra el embedding almacenado de cada película
            max_similarity = -1
            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                similarity = cosine_similarity(prompt_emb, movie_emb)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie
        except Exception as e:
            error = str(e)

    return render(request, 'recommendations.html', {
        'prompt': prompt,
        'movie': best_movie,
        'similarity': max_similarity,
        'error': error,
    })
