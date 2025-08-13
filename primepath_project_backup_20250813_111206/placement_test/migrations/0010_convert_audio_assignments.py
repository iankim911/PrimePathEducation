from django.db import migrations

def convert_audio_assignments(apps, schema_editor):
    """
    Convert existing AudioFile start_question/end_question assignments 
    to new Question.audio_file relationships.
    """
    AudioFile = apps.get_model('placement_test', 'AudioFile')
    Question = apps.get_model('placement_test', 'Question')
    
    converted_count = 0
    
    # Convert one-to-one assignments (start_question == end_question)
    for audio in AudioFile.objects.filter(start_question__gte=1):
        if audio.start_question == audio.end_question:
            try:
                question = Question.objects.get(
                    exam=audio.exam,
                    question_number=audio.start_question
                )
                question.audio_file = audio
                question.save()
                converted_count += 1
                print(f"Converted: Audio {audio.id} -> Question {question.question_number} in Exam {audio.exam.name}")
            except Question.DoesNotExist:
                print(f"Warning: Question {audio.start_question} not found in exam {audio.exam.name}")
    
    print(f"Successfully converted {converted_count} audio assignments to new relationship")

def reverse_audio_assignments(apps, schema_editor):
    """
    Reverse the conversion by clearing Question.audio_file relationships.
    The original start_question/end_question data is preserved.
    """
    Question = apps.get_model('placement_test', 'Question')
    
    cleared_count = Question.objects.filter(audio_file__isnull=False).count()
    Question.objects.filter(audio_file__isnull=False).update(audio_file=None)
    
    print(f"Reversed {cleared_count} audio assignments")

class Migration(migrations.Migration):
    dependencies = [
        ('placement_test', '0009_question_audio_file'),
    ]

    operations = [
        migrations.RunPython(convert_audio_assignments, reverse_audio_assignments),
    ]