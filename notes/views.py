from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages

from .models import Note

class BaseNoteView(LoginRequiredMixin):
    model = Note
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

class NoteListView(BaseNoteView, ListView):
    template_name = 'notes/index.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        # recent or favorites
        filter_type = self.request.GET.get('filter')
        if filter_type == 'recent':
            queryset = queryset.order_by('-created_at')
        elif filter_type == 'favorites':
            queryset = queryset.filter(is_favorite=True)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class NoteDetailView(BaseNoteView, DetailView):
    template_name = 'notes/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        notes = list(self.get_queryset().values_list('slug', flat=True))
        current_index = notes.index(self.object.slug)
        
        context['next_note'] = notes[current_index + 1] if current_index < len(notes) - 1 else None
        context['prev_note'] = notes[current_index - 1] if current_index > 0 else None
        
        return context

class NoteCreateView(BaseNoteView, CreateView):
    template_name = 'notes/form.html'
    fields = ['title', 'content', 'thumbnail']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)

class NoteUpdateView(BaseNoteView, UpdateView):
    template_name = 'notes/form.html'
    fields = ['title', 'content', 'thumbnail']
    
    def form_valid(self, form):
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)

class NoteDeleteView(BaseNoteView, DeleteView):
    template_name = 'notes/delete.html'
    success_url = reverse_lazy('notes:index')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Note deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def make_favorite(request, slug):
    note = get_object_or_404(Note, slug=slug, user=request.user)
    note.is_favorite = not note.is_favorite
    note.save()
    
    return JsonResponse({
        'status': 'success',
        'is_favorite': note.is_favorite
    })

