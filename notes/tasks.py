from huey.contrib.djhuey import db_task
from .models import Note
from . import methods

@db_task()
def create_slug(title):
    slug = methods.generate_unique_slug(title, Note) if title else "-"
    Note.objects.filter(title=title).update(slug=slug)
    return slug

@db_task()
def calculate_reading_time(content):
    reading_time = methods.get_reading_time(content) if content else 1
    Note.objects.filter(content=content).update(reading_time=reading_time)
    return reading_time