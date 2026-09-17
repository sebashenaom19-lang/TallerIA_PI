import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Compare two movies and optionally a prompt using OpenAI embeddings"

    def handle(self, *args, **kwargs):
        # ✅ Load OpenAI API key
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        # ✅ Películas seleccionadas para la comparación (actividad del taller)
        movie1 = Movie.objects.get(title="A Trip to the Moon")
        movie2 = Movie.objects.get(title="The Great Train Robbery")

        # ✅ Prompt de búsqueda seleccionado para la actividad
        prompt = "película de ciencia ficción sobre un viaje espacial a la luna"

        self.stdout.write("=" * 70)
        self.stdout.write(f"🎬 Película 1: {movie1.title} ({movie1.year}) - {movie1.genre}")
        self.stdout.write(f"   Descripción: {movie1.description[:200]}...")
        self.stdout.write("")
        self.stdout.write(f"🎬 Película 2: {movie2.title} ({movie2.year}) - {movie2.genre}")
        self.stdout.write(f"   Descripción: {movie2.description[:200]}...")
        self.stdout.write("")
        self.stdout.write(f"📝 Prompt de búsqueda: '{prompt}'")
        self.stdout.write("=" * 70)

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        # ✅ Generate embeddings of both movies
        emb1 = get_embedding(movie1.description)
        emb2 = get_embedding(movie2.description)
        self.stdout.write(f"📐 Tamaño de cada embedding: {emb1.shape[0]} dimensiones")

        # ✅ Compute similarity between movies
        similarity = cosine_similarity(emb1, emb2)
        self.stdout.write(f"\U0001F3AC Similaridad entre '{movie1.title}' y '{movie2.title}': {similarity:.4f}")

        # ✅ Compare against a prompt
        prompt_emb = get_embedding(prompt)

        sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
        sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie1.title}': {sim_prompt_movie1:.4f}")
        self.stdout.write(f"\U0001F4DD Similitud prompt vs '{movie2.title}': {sim_prompt_movie2:.4f}")

        ganadora = movie1.title if sim_prompt_movie1 > sim_prompt_movie2 else movie2.title
        self.stdout.write(self.style.SUCCESS(f"🏆 La película más cercana al prompt es: {ganadora}"))
