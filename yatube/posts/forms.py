from django.forms import ModelForm
from django import forms
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_texts = {'text': 'Оставь любую надпись', 'group': 'существующие'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        help_texts = {'text': 'Введите комментарий'}
