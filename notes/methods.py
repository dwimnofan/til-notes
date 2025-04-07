from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

def generate_unique_slug(title, model_class, current_id=None):
    base_slug = slugify(title)
    unique_slug = base_slug
    counter = 1
    
    while model_class.objects.filter(slug=unique_slug).exclude(pk=current_id).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
        
    return unique_slug


def save_note(note, title=None, content=None):
    from .tasks import create_slug, calculate_reading_time  
    
    with transaction.atomic():
        if title is not None:
            note.title = title
            if not note.slug:
                note.slug = slugify(title)
                
        if content is not None:
            note.content = content
            note.reading_time = 1 
            
        if not note.pk:  
            note.created_at = timezone.now()
        note.updated_at = timezone.now()
            
        note.save()
        
        if title is not None:
            create_slug.schedule((title,), delay=1)  
        if content is not None:
            calculate_reading_time.schedule((content,), delay=1)  
            
        return note

def get_note_url(note):
    return reverse('notes:detail', kwargs={'slug': note.slug})

def get_reading_time(content):
    words_per_minute = 200
    word_count = len(content.split())
    return max(1, round(word_count / words_per_minute))

