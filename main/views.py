from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status, serializers
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib.auth import authenticate, login
from .serializers import UserSerializer, UserInfoSerializer, UserMoodSerializer, MemoriesSerializer
from django.contrib.auth.hashers import make_password
from . import models
from django.utils import timezone
import json
from supabase import create_client, Client

# Create your views here.
@api_view(['GET'])
def home(request):
    return Response({"message": "Hello, world!"})

@api_view(['POST'])
def singup(request):
    postdata = request.POST
    try:
        user = User.objects.filter(Q(username=postdata['email']) | Q(email=postdata['email'])).count()
    except:
        user = None
    if not user:
        user = User.objects.create(username=postdata['email'],password=make_password(postdata['password']),email=postdata['email'],first_name=postdata['name'])
        return Response({"user": UserSerializer(user).data}	)
    else:
        return Response({"message": "Email already Exists."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def login(request):
    postdata = request.POST
    email = postdata['email']
    password = postdata['password']
    try:
        user = User.objects.get(username=postdata['email'])
    except:
        user = None
    if user and email and password:
        user = authenticate(username=email, password=password)
        if user:
            return Response({"user": UserSerializer(user).data})
        else:
            return Response({"message": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "user not found"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def user_info(request):
    weight = request.POST['weight']
    height = request.POST['weight']
    user = request.POST['user_id']
    if weight and height and user:
        models.UserInfo.objects.create(user_id=user,weight=weight,height=height)
        return Response({"message": "User Info Added"})
    else:
        return Response({"message": "User Info Not Added"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def user_mood(request):
    mood = request.POST['mood']
    user = request.POST['user_id']
    if mood and user:
        models.UserMood.objects.create(user_id=user,mood=mood,date=timezone.now().date())
        return Response({"message": "User Mood Added"})
    else:
        return Response({"message": "User Mood Not Added"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def user_data(request):
    user_id = request.GET.get('user_id')
    if user_id:
        user = User.objects.get(id=user_id)
        user_info = models.UserInfo.objects.get(user_id=user_id)
        user_mood = models.UserMood.objects.filter(user_id=user_id).order_by('-date')
        return Response({
                "user": UserSerializer(user).data,
                "user_info":UserInfoSerializer(user_info).data,
                "user_mood":UserMoodSerializer(user_mood, many=True).data
            })
    else:
        return Response({"message": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def meds_data(request):
    json_file_path = 'output.json'

    # Read the JSON data from the file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)
        
    serialized_data = json_data[0::1000]

    # Return the JSON data as a response
    return JsonResponse(serialized_data, safe=False)

@api_view(['POST','GET'])
def memories(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if user_id:
            memories = models.Memories.objects.filter(author_id=user_id).order_by('-date_posted')
            serializer = MemoriesSerializer(memories, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        postdata = request.POST
        author = postdata['user_id']
        content = postdata['content']
        image = request.FILES.get('image')
        alt_text = postdata['alt_text']
        if author and content:
            url: str = "https://qwrranvmkfmxcmjilkam.supabase.co"
            key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3cnJhbnZta2ZteGNtamlsa2FtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NzI2NDI3MywiZXhwIjoyMDEyODQwMjczfQ.O2suIZCGyNwbPV7PC8EyK8jrvyrF3iTv31cdKwsVD4M"
            supabase: Client = create_client(url, key)
            print(image.name,image.content_type)
            try:
                name = image.name.split('.')[0]
                file_type = image.content_type
                image_content = image.read()
                supabase.storage.from_("images").upload(file=image_content,path=name, file_options={"content-type": file_type})
                url = supabase.storage.from_('images').get_public_url(name)
                print(url)
                print(type(url))
            except Exception as e:
                return Response({"message": "Memory Not Added"}, status=status.HTTP_400_BAD_REQUEST)
            models.Memories.objects.create(author_id=author,content=content,image=url,alt_text=alt_text)
            return Response({"message": "Memory Added"})
        else:
            return Response({"message": "Memory Not Added"}, status=status.HTTP_400_BAD_REQUEST)