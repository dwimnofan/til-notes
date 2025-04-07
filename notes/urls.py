from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.NoteListView.as_view(), name='index'),
    path('note/new/', views.NoteCreateView.as_view(), name='create'),
    path('note/<slug:slug>/', views.NoteDetailView.as_view(), name='detail'),
    path('note/<slug:slug>/edit/', views.NoteUpdateView.as_view(), name='update'),
    path('note/<slug:slug>/delete/', views.NoteDeleteView.as_view(), name='delete'),
    path('note/<slug:slug>/favorite/', views.make_favorite, name='favorite'),
] 