from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from posts.models import Group, Post, Comment
from django.forms import ModelForm, Textarea
from django.core.exceptions import ValidationError
from django import forms

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
    
    def clean_text(self):
        cleaned_data = self.cleaned_data['text']
        if len(cleaned_data) < 20:
            raise forms.ValidationError("Длина поста должна быть более 20 символов!")
        return cleaned_data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 5}),
        }
    
    def clean_text(self):
        cleaned_data = self.cleaned_data['text']
        if len(cleaned_data) < 3:
            raise forms.ValidationError("Длина комментария должна быть более 3-х символов!")
        return cleaned_data