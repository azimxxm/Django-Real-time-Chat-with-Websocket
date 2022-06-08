# chat/views.py
from django.shortcuts import render
import requests
from . forms import PostForm
from . models import Post
from . serializer import PostSerializer
from rest_framework import generics, status
from rest_framework.response import Response

def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

def create_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.save()
        form = PostForm()
    context = {
        'form': form
    } 
    return render(request, 'chat/create_post.html', context)


def post_list(request):
    posts = Post.objects.all()
    return render(request, 'chat/post_list.html', {
        'posts': posts
    })


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get(self, request):

        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    
