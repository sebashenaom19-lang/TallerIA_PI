import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Show the stored embedding of a random movie"

    def handle(self, *args, **kwargs):
        # ✅ Selecciona una película al azar de la base de datos
        movie = Movie.objects.order_by('?').first()

        if movie is None:
            self.stderr.write("There are no movies in the database.")
            return

        # ✅ Recupera el embedding almacenado como binario
        embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)

        self.stdout.write(self.style.SUCCESS(f"🎬 Película seleccionada al azar: {movie.title}"))
        self.stdout.write(f"📏 Tamaño del embedding: {embedding_vector.shape[0]}")
        self.stdout.write(f"🔢 Primeros 10 valores: {embedding_vector[:10]}")
        self.stdout.write(f"🧮 Norma del vector: {np.linalg.norm(embedding_vector):.4f}")
        self.stdout.write("")
        self.stdout.write("🌐 Embedding completo:")
        self.stdout.write(str(embedding_vector))
