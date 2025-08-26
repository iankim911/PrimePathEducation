"""
Management command to fix audio files with old default assignments.

This command updates audio files that have start_question=1 and end_question=1
(old default) to use start_question=0 and end_question=0 (new unassigned indicator),
but only if they are truly unassigned (not intentionally assigned to Question 1).
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from placement_test.models import PlacementAudioFile as AudioFile


class Command(BaseCommand):
    help = 'Fix audio files with old default assignments to use new unassigned indicator'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find audio files that have the old default assignment (1,1)
        # We need to be careful not to change files that are intentionally assigned to Q1
        audio_files_to_update = AudioFile.objects.filter(
            start_question=1,
            end_question=1
        )
        
        if not audio_files_to_update.exists():
            self.stdout.write(
                self.style.SUCCESS('No audio files need updating.')
            )
            return
        
        self.stdout.write(f'Found {audio_files_to_update.count()} audio files with Q1 assignments.')
        
        # For safety, we'll assume that multiple audio files assigned to the same Q1 
        # in the same exam are likely to be unassigned defaults
        update_count = 0
        
        for audio in audio_files_to_update:
            exam = audio.exam
            
            # Check if there are multiple audio files assigned to Q1 in this exam
            q1_audio_count = AudioFile.objects.filter(
                exam=exam,
                start_question=1,
                end_question=1
            ).count()
            
            # If there are multiple Q1 assignments, they're likely defaults
            # If there's only one, it might be intentional
            if q1_audio_count > 1:
                if dry_run:
                    self.stdout.write(
                        f'Would update: Exam {exam.id} - Audio {audio.id} '
                        f'"{audio.name}" (1 of {q1_audio_count} Q1 assignments)'
                    )
                else:
                    audio.start_question = 0
                    audio.end_question = 0
                    audio.save()
                    self.stdout.write(
                        f'Updated: Exam {exam.id} - Audio {audio.id} '
                        f'"{audio.name}" -> unassigned'
                    )
                update_count += 1
            else:
                self.stdout.write(
                    f'Skipping: Exam {exam.id} - Audio {audio.id} '
                    f'"{audio.name}" (single Q1 assignment - possibly intentional)'
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {update_count} audio files. '
                    'Run without --dry-run to apply changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {update_count} audio files to unassigned status.'
                )
            )