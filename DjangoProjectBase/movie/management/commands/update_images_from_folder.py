import os
from django.core.management.base import BaseCommand
from movie.models import Movie


class Command(BaseCommand):
    help = "Assign to every movie the image generated with the OpenAI API stored in media/movie/images/"

    def handle(self, *args, **kwargs):
        images_folder = 'media/movie/images/'

        if not os.path.isdir(images_folder):
            self.stderr.write(f"Folder '{images_folder}' not found.")
            return

        # ✅ Archivos disponibles en la carpeta de imágenes
        available = os.listdir(images_folder)

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        updated_count = 0
        for movie in movies:
            # ✅ Las imágenes entregadas tienen el nombre m_<TITULO>.png
            image_filename = f"m_{movie.title}.png"

            if image_filename in available:
                movie.image = os.path.join('movie/images', image_filename)
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
            else:
                self.stderr.write(f"Image not found for: {movie.title} ({image_filename})")

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movie images from folder."))
