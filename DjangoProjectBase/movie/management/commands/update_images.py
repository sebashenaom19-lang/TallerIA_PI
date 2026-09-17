import os
import base64
import requests
from io import BytesIO
from PIL import Image
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate images with OpenAI and update movie image field"

    def handle(self, *args, **kwargs):
        # ✅ Load environment variables from the .env file
        load_dotenv('../openAI.env')

        # ✅ Initialize the OpenAI client with the API key
        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )
        # ✅ Folder to save images
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        # ✅ Fetch all movies
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                # ✅ Call the helper function
                image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)

                # ✅ Update database
                movie.image = image_relative_path
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))

            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            # 🔎 Process just the first movie for demonstration
            break

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))

    def generate_and_download_image(self, client, movie_title, save_folder):
        """
        Generates an image using OpenAI's image model and downloads it.
        Returns the relative image path or raises an exception.
        """
        prompt = f"Movie poster of {movie_title}"

        # ✅ Generate image with OpenAI
        # NOTA: los modelos dall-e-2 / dall-e-3 ya no están disponibles en la API,
        # por eso se usa gpt-image-1-mini (el más económico de la familia gpt-image).
        response = client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )

        # ✅ Prepare the filename and full save path
        image_filename = f"m_{movie_title}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        # ✅ Download / decode the image
        data = response.data[0]
        if getattr(data, "url", None):
            image_response = requests.get(data.url)
            image_response.raise_for_status()
            content = image_response.content
        else:
            content = base64.b64decode(data.b64_json)

        # ✅ Se reescala a 256x256 (tamaño usado en el taller) para no inflar el repositorio
        image = Image.open(BytesIO(content)).convert("RGB")
        image = image.resize((256, 256))
        image.save(image_path_full, format="PNG")

        # ✅ Return relative path to be saved in the DB
        return os.path.join('movie/images', image_filename)
