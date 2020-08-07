import django
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate

from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Article, Comment
import json


def signup(request):
    """
    Makes a new User account

    POST: Creates a user with the information given by request JSON body
    """

    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']

            User.objects.create_user(username=username, password=password)
            return HttpResponse(status=201)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['POST'])



def signin(request):
    """
    Logs in to an account

    POST: Authenticates with the information given by request JSON body, and decides whether to log in or response an error
    """
    
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']

            # Authentication
            user = authenticate(request,username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponse("Successfully signed in!", status=204)          
            else:
                return JsonResponse({"error":"Wrong Authentication"}, status=401)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['POST'])



def signout(request):
    """
    Logs out from currently signed in account

    GET: Logs out if the user is authenticated; responses an error if not
    """

    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse("Successfully signed out!", status=204)
        else:
            return JsonResponse({"error":"Cannot sign out when not signed in"}, status=401)
    
    else:
        return HttpResponseNotAllowed(['GET'])



@login_required
def article(request):
    """
    When generally requesting for article, the user can GET or POST.

    GET: Responses with a JSON having a dictionary for the target article's title, content, and author
    POST: Creates an article with the information given by request JSON body, and responses the created article as a JSON
    """

    if request.method == 'GET':
        # Gets articles and makes them into a list of dictionaries
        articles = Article.objects.all()
        articles = list(articles.values('title','content','author'))
        return JsonResponse(articles, safe=False, status=200)
    
    elif request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            title = req_data['title']
            content = req_data['content']

            # Makes an Article object and saves it in the database
            article = Article(title=title, content=content, author=request.user)
            article.save()
            return HttpResponse(json.dumps(model_to_dict(article)), status=201)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['GET','POST'])



@login_required
def article_id(request, id):
    """
    When specified an article id in the url, the user can GET, PUT, or DELETE.

    GET: Responses with a JSON having a dictionary for the target article's title, content, and author
    PUT: Update the target article with the information given by request JSON body, and responses the updated article as a JSON
    DELETE: Deletes the target article, including the comments written under the article
    """

    if request.method == 'GET':
        try:
            # Gets targeted article, and changes it to a dictionary
            article = Article.objects.get(id=id)
            return JsonResponse(model_to_dict(article), status=200)
        
        except Article.DoesNotExist:
            # Exception: The targeted article with the id not existing
            return JsonResponse({"error":"Article with such id does not exist"}, status=404)
    
    elif request.method == 'PUT':
        try:
            req_data = json.loads(request.body.decode())
            title = req_data['title']
            content = req_data['content']

            # Gets targeted article
            article = Article.objects.get(id=id)
            
            if article.author == request.user:
                article.title = title
                article.content = content
                article.save()
                return HttpResponse(json.dumps(model_to_dict(article)), status=200)
            else:
                return JsonResponse({"error": "Cannot PUT because you do not have access to article with id " + str(id)}, status=403)
        
        except Article.DoesNotExist:
            # Exception: The targeted article with the id not existing
            return JsonResponse({"error": "Cannot PUT because article with id " + str(id) + " does not exist"}, status=404)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having unexpected format
            return HttpResponseBadRequest()
    
    elif request.method == 'DELETE':
        try:
            # Gets targeted article
            article = Article.objects.get(id=id)

            if article.author == request.user:
                # Article deletion causes Comment to be automatically deleted 
                # (because for Comment Article is a ForeignKey that is on_delete CASCADE)
                article.delete()
                return HttpResponse(status=200)      
            else:
                return JsonResponse({"error": "Cannot DELETE because you do not have access to article with id " + str(id)}, status=403)
        
        except Article.DoesNotExist:
            # Exception: The targeted article with the id not existing
            return JsonResponse({"error":"Article with such id does not exist"}, status=404)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['GET','POST','DELETE'])



@login_required
def article_id_comment(request, id):
    """
    When generally requesting for comment of a specified article id in the url, the user can GET or POST.

    GET: Responses with a JSON having a list of dictionaries for each comment's article, content, and author
    POST: Creates a comment with the information given by request JSON body, and responses the created comment as a JSON
    """

    if request.method == "GET":
        try:
            # Gets targeted article
            article = Article.objects.get(id=id)

            # Gets comments that are written under the targeted article and makes them into a list of dictionaries
            comments = Comment.objects.filter(article=article)
            comments = list(comments.values('article','content','author'))
            return JsonResponse(comments, safe=False, status=200)
        
        except Article.DoesNotExist:
            # Exception: The targeted article with the id not existing
            return JsonResponse({"error":"Article with such id does not exist"}, status=404)
    
    elif request.method == "POST":
        try:
            req_data = json.loads(request.body.decode())
            content = req_data['content']

            # Gets targeted article
            article = Article.objects.get(id=id)

            # Makes a Comment object and saves it in the database
            comment = Comment(article=article,content=content,author=request.user)
            comment.save()
            return HttpResponse(json.dumps(model_to_dict(comment)), status=201)
        
        except Article.DoesNotExist:
            # Exception: The targeted article with the id not existing
            return JsonResponse({"error":"Article with such id does not exist"}, status=404)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having an unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['GET','POST'])



@login_required
def comment_id(request, id):
    """
    When specified a comment id in the url, the user can GET, PUT, or DELETE.

    GET: Responses with a JSON having a dictionary for the target comment's article, content, and author
    PUT: Updates the target comment with the information given by request JSON body, and responses the updated comment as a JSON
    DELETE: Deletes the target comment, but not the article or author of it
    """

    if request.method == "GET":
        try:
            # Gets target comment; changes it to a dictionary
            comment = Comment.objects.get(id=id)
            return JsonResponse(model_to_dict(comment), status=200)
            
        except Comment.DoesNotExist:
            # Exception: The targeted comment with the id not existing
            return JsonResponse({"error":"Comment with such id does not exist"}, status=404)

    elif request.method == "PUT":
        try:
            req_data = json.loads(request.body.decode())
            content = req_data['content']

            # Gets target comment
            comment = Comment.objects.get(id=id)

            if comment.author == request.user:
                comment.content = content
                comment.save()
                return HttpResponse(json.dumps(model_to_dict(comment)), status=200)         
            else:
                return JsonResponse({"error": "Cannot PUT because you do not have access to comment with id " + str(id)}, status=403)

        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having an unexpected format
            return HttpResponseBadRequest()

    elif request.method == "DELETE":
        try:
            # Gets target comment
            comment = Comment.objects.get(id=id)

            if comment.author == request.user:
                comment.delete()
                return HttpResponse(status=200)
            
            else:
                return JsonResponse({"error": "Cannot DELETE because you do not have access to comment with id " + str(id)}, status=403)
        
        except Comment.DoesNotExist:
            # Exception: The targeted comment with the id not existing
            return JsonResponse({"error":"Comment with such id does not exist"}, status=404)
        
        except (KeyError, json.JSONDecodeError):
            # Exception: req_data having an unexpected format
            return HttpResponseBadRequest()
    
    else:
        return HttpResponseNotAllowed(['GET','POST','DELETE'])



@ensure_csrf_cookie
def token(request):
    """ 
    Get a CSRF TOKEN that will be used in the HEADERS of the Rest API
    """

    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])
