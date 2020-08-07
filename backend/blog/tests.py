import blog.views
from django.test import TestCase, Client
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import authenticate

from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Article, Comment
import json


class BlogTestCase(TestCase):
    def setUp(self):
        user_a = User.objects.create_user(username="alice", password="alice1212")
        user_b = User.objects.create_user(username="bobby", password="bobby1212")

        article1 = Article(title="Introducing myself", content="Hi my name is Alice!", author=user_a) # Written by Alice
        article1.save()
        article2 = Article(title="Introducing myself", content="Hi my name is Bobby!", author=user_b) # Written by Bobby
        article2.save()
        article3 = Article(title="Meant to be deleted", content="this article is meant to be deleted.", author=user_a) # Written by Alice
        article3.save()

        comment1 = Comment(article=article1, content="I'm Bobby, nice to meet you Alice!", author=user_b) # Written by Bobby to Alice's article
        comment1.save()
        comment2 = Comment(article=article2, content="My name is Alice, nice to meet you Bobby.", author=user_a) # Written by Alice to Bobby's article
        comment2.save()
        comment3 = Comment(article=article1, content="Test Comment.", author=user_a) # Written by Alice to Alice's article
        comment3.save()

        self.client = Client()
        self.article1 = article1
        self.article2 = article2
        self.article3 = article3
        self.comment1 = comment1
        self.comment2 = comment2
        self.comment3 = comment3
        self.user_a_id = user_a.id
        self.user_b_id = user_b.id
    
    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup', json.dumps({'username': 'chris', 'password': 'chris'}),
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection
    
    def test_signup_success(self):
        response = self.client.post('/api/signup', json.dumps({"username":"chris", "password":"chris1212"}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_signup_failure(self):
        response = self.client.get('/api/signup')
        self.assertEqual(response.status_code, 405)



    ### /api/signin

    def test_signin_success(self):
        response = self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        self.assertEqual(response.status_code, 204)
    
    def test_signin_failure(self):
        response = self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice12123"}), content_type='application/json')
        self.assertEqual(response.status_code, 401)



    ### /api/signout

    def test_signout_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/signout')
        self.assertEqual(response.status_code, 204)

    def test_signout_failure(self):
        response = self.client.get('/api/signout')
        self.assertEqual(response.status_code, 401)



    ### /api/article

    def test_article_get_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/article')
        self.assertEqual(response.status_code, 200)

        decodedVal = response.content.decode()
        self.assertIn(json.dumps({"title": "Introducing myself", "content": "Hi my name is Alice!", "author": self.user_a_id}), decodedVal)

    def test_article_post_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.post('/api/article', json.dumps({"title": "Hello!", "content": "Alice says hello!", "author": self.user_a_id}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        content = json.loads(response.content)
        self.assertEqual("Hello!", content['title'])
        self.assertEqual("Alice says hello!", content['content'])
        self.assertEqual(self.user_a_id, content['author'])
    
    def test_article_unauth_failure(self):
        response = self.client.get('/api/article')
        self.assertEqual(response.status_code, 302)

    def test_article_notallowed_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/article')
        self.assertEqual(response.status_code, 405)



    ### /api/article/<int:id>

    def test_article_id_get_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/article/' + str(self.article1.id))
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual("Introducing myself", content['title'])
        self.assertEqual("Hi my name is Alice!", content['content'])
        self.assertEqual(self.user_a_id, content['author'])

    def test_article_id_get_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/article/0')
        self.assertEqual(response.status_code, 404)
        
    def test_article_id_put_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.put('/api/article/' + str(self.article1.id), json.dumps({"title":"Introducing myself", "content":"Hello My name is Alice.", "author":self.user_a_id}))
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual("Introducing myself", content['title'])
        self.assertEqual("Hello My name is Alice.", content['content'])
        self.assertEqual(self.user_a_id, content['author'])

    def test_article_id_put_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.put('/api/article/100', json.dumps({"title":"Hi!", "content":"Hello! My name is Alice!", "author":self.user_a_id}))
        self.assertEqual(response.status_code, 404)
    
    def test_article_id_put_unauth_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.put('/api/article/' + str(self.article2.id), json.dumps({"title":"Hi!", "content":"Hello! My name is Alice!", "author":self.user_a_id}))
        self.assertEqual(response.status_code, 403)

    def test_article_id_delete_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/article/' + str(self.article3.id))
        self.assertEqual(response.status_code, 200)

    def test_article_id_delete_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/article/100')
        self.assertEqual(response.status_code, 404)

    def test_article_id_delete_unauth_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/article/' + str(self.article2.id))
        self.assertEqual(response.status_code, 403)



    ### /api/comment/<int:id>

    def test_comment_id_get_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/comment/' + str(self.comment1.id))
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(self.article1.id, content['article'])
        self.assertEqual("I'm Bobby, nice to meet you Alice!", content['content'])
        self.assertEqual(self.user_b_id, content['author'])

    def test_comment_id_get_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/comment/0')
        self.assertEqual(response.status_code, 404)
        
    def test_comment_id_put_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.put('/api/comment/' + str(self.comment2.id), json.dumps({"article":self.article2.id, "content":"My name is Alice.", "author":self.user_a_id}))
        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(self.article2.id, content['article'])
        self.assertEqual("My name is Alice.", content['content'])
        self.assertEqual(self.user_a_id, content['author'])

    def test_comment_id_put_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.put('/api/comment/' + str(self.comment1.id), json.dumps({"article":self.article1.id, "content":"I'm Bobby, glad to see you Alice!", "author":self.user_b_id}))
        self.assertEqual(response.status_code, 403)

    def test_comment_id_delete_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/comment/' + str(self.comment2.id))
        self.assertEqual(response.status_code, 200)

    def test_comment_id_delete_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/comment/100')
        self.assertEqual(response.status_code, 404)

    def test_comment_id_delete_unauth_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/comment/' + str(self.comment1.id))
        self.assertEqual(response.status_code, 403)



    ### /api/article/<int:id>/comment

    def test_article_id_comment_get_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/article/' + str(self.article1.id) + '/comment')
        self.assertEqual(response.status_code, 200)

        comments = [model_to_dict(self.comment1, fields=['article','content','author']),  \
            model_to_dict(self.comment3, fields=['article','content','author'])]

        content = json.loads(response.content)
        for comment in comments:
            self.assertIn(comment, content)

    def test_article_id_comment_get_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.get('/api/article/100/comment')
        self.assertEqual(response.status_code, 404)

    def test_article_id_comment_post_success(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.post('/api/article/' + str(self.article2.id) + '/comment', json.dumps({"article": self.article2.id, "content": "Alice here -- nice to meet you Bobby", "author": self.user_a_id}), content_type='application/json')
        self.assertEqual(response.status_code, 201)

        content = json.loads(response.content)
        self.assertEqual(self.article2.id, content['article'])
        self.assertEqual("Alice here -- nice to meet you Bobby", content['content'])
        self.assertEqual(self.user_a_id, content['author'])
    
    def test_article_id_comment_post_nonexist_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.post('/api/article/100/comment', json.dumps({"article": self.article2.id, "content": "Alice here -- nice to meet you Bobby", "author": self.user_a_id}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_article_id_comment_notallowed_failure(self):
        self.client.post('/api/signin', json.dumps({"username":"alice", "password":"alice1212"}), content_type='application/json')
        response = self.client.delete('/api/article/' + str(self.article1.id) + '/comment')
        self.assertEqual(response.status_code, 405)
