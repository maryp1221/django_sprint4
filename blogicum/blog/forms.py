from blog.models import Comment, Post
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'image',
            'location',
            'category',
        )
