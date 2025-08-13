from django.core.management.base import BaseCommand
from placement_test.models import AudioFile
import os


class Command(BaseCommand):
    help = 'Fix audio file names that have default values'

    def handle(self, *args, **options):
        audio_files = AudioFile.objects.filter(name__in=['Audio File', 'Audio 1', 'Audio 2', 'Audio 3', 'Audio 4', 'Audio 5'])
        
        fixed_count = 0
        for audio in audio_files:
            if audio.audio_file and audio.audio_file.name:
                # Extract filename from the file path
                filename = os.path.basename(audio.audio_file.name)
                # Remove extension
                name_without_ext = os.path.splitext(filename)[0]
                # Update the name
                audio.name = name_without_ext
                audio.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Fixed audio name: "{audio.name}" for exam "{audio.exam.name}"'
                    )
                )
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS('No audio files needed fixing.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully fixed {fixed_count} audio file names.'
                )
            )