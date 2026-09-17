import os
import base64
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

from PIL import Image
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


class Command(BaseCommand):
    """Genera con la API de OpenAI la imagen de TODAS las películas.

    Equivale a la carpeta de imágenes entregada por el docente: solo crea los
    archivos m_<titulo>.png dentro de media/movie/images/. La asignación de esas
    imágenes a la base de datos la hace el comando update_images_from_folder.
    """

    help = "Generate the m_<title>.png image of every movie using the OpenAI API"

    def handle(self, *args, **kwargs):
        load_dotenv('../openAI.env')
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        movies = list(Movie.objects.all())
        self.stdout.write(f"Found {len(movies)} movies")

        def generate(movie):
            path = os.path.join(images_folder, f"m_{movie.title}.png")
            if os.path.exists(path):
                return f"Already exists: {movie.title}"
            try:
                response = client.images.generate(
                    model="gpt-image-1-mini",
                    prompt=f"Movie poster of {movie.title}",
                    size="1024x1024",
                    quality="low",
                    n=1,
                )
                content = base64.b64decode(response.data[0].b64_json)
                image = Image.open(BytesIO(content)).convert("RGB")
                image.resize((256, 256)).save(path, format="PNG")
                return f"Generated: {movie.title}"
            except Exception as e:
                return f"Failed {movie.title}: {e}"

        with ThreadPoolExecutor(max_workers=6) as pool:
            for result in pool.map(generate, movies):
                self.stdout.write(result)

        self.stdout.write(self.style.SUCCESS("Finished generating the images folder."))
