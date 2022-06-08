from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Thi is title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'cols': 40, 'placeholder': 'This is content'}),
        }