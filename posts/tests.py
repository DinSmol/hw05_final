from posts.models import Post, Follow
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.cache import cache
import pytest


class PlansPageTest(TestCase):
    test_user_name, test_user_pass = 'testuser1', '12345'
    def setUp(self):
        self.client = Client()
        self.test_user1 = User.objects.create_user(username=self.test_user_name, password=self.test_user_pass) 
        self.login = self.client.login(username=self.test_user_name, password=self.test_user_pass)
        

    def test_profile_page(self):
        self.response = self.client.get('/testuser1/')
        self.assertEqual(self.response.status_code, 200)


    def test_page_new(self):
        self.response = self.client.get('/new/', follow=True)
        self.assertEqual(self.response.status_code, 200)


    def test_unregistered_action(self):
        logout = self.client.logout()
        self.response = self.client.get('/new/')
        self.assertNotEqual(self.response.status_code, 200)


    def test_create_post(self):
        cache.clear()  
        post_text = 'test_text'
        post = Post.objects.create(text=post_text, author=self.test_user1)

        for test_url in ['/', '/testuser1/']:   
            self.response = self.client.get(test_url)
            self.assertEqual(post_text, self.response.context['page'].object_list[0].text)

        link_name = '/testuser1/' + str(post.id) + '/'  
        self.response = self.client.get(link_name)
        self.assertEqual(post_text, self.response.context['post'].text)


    def test_post_edit(self):
        init_text, new_text = 'init_text', 'new_text_with_many_symbols_more_then_20'
        post = Post.objects.create(text=init_text, author=self.test_user1)
        link_name = '/testuser1/' + str(post.id) + '/edit/'

        self.response = self.client.get(link_name)
        self.assertEqual(self.response.status_code, 200)

        self.response = self.client.post(link_name, data={'text':new_text, 'post_id':post.id})  
        self.assertEqual(self.response.status_code, 302)                                        

        for test_url in ['/', '/testuser1/']:
            cache.clear()
            self.response = self.client.get(test_url)
            self.assertEqual(new_text, self.response.context['page'].object_list[0].text)
        self.response = self.client.get('/testuser1/' + str(post.id) + '/')
        self.assertEqual(new_text, self.response.context['post'].text)

    
    def test_page_not_found(self):
        self.response = self.client.get('/bad_url/')
        self.assertEqual(self.response.status_code, 404)


    def test_page_content(self):
        post_text = 'test_text__________________________'
        with open("media/posts/file.jpg", mode='rb') as fp:
            post = self.client.post('/new/', {'text':post_text, 'image':fp})  
                                                                                   
        for test_url in ['/', '/testuser1/']:
            cache.clear()
            self.response = self.client.get(test_url)
            self.assertContains(self.response, 'img')

        self.response = self.client.get('/testuser1/1/') 
        self.assertContains(self.response, 'img')


    def test_non_image_upload(self):
        post_text = 'test_text__________________________'
        with open("media/posts/homework.py", mode='rb') as fp:
            self.response = self.client.post('/new/', {'text':post_text, 'image':fp})    
        self.assertNotEqual(self.response.status_code, 302)   

        cache.clear() 
        link_name = '/'  
        self.response = self.client.get(link_name)
        self.assertNotContains(self.response, 'img')


    def test_follow_object_create(self):
        init_text = 'new_text_for_check_exist_Post_in_follower\'s_pages'
        test_user2 = User.objects.create_user(username='testuser2', password=self.test_user_pass)   

        self.response = self.client.get('/testuser2/follow/')                                       
        self.assertEqual(self.response.status_code, 200)

        follow = Follow.objects.all()                                                
        self.assertEqual(follow[0].user.username, self.test_user1.username)
        self.assertEqual(follow[0].author.username, test_user2.username)


    def test_follow(self):
        init_text = 'new_text_for_check_exist_Post_in_follower\'s_pages'
        test_user2 = User.objects.create_user(username='testuser2', password=self.test_user_pass)   
        post = Post.objects.create(text=init_text, author=test_user2) 

        self.response = self.client.get('/testuser2/follow/')       
        self.assertEqual(self.response.status_code, 200)

        self.response = self.client.get('/follow/')                                                
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['page'].object_list[0].text, init_text)              


    def test_unfollow(self):
        init_text = 'new_text_for_check_exist_Post_in_follower\'s_pages'
        test_user2 = User.objects.create_user(username='testuser2', password=self.test_user_pass)   
        post = Post.objects.create(text=init_text, author=test_user2) 

        self.response = self.client.get('/testuser2/follow/')    
        self.assertEqual(self.response.status_code, 200)                                                  
        self.response = self.client.get('/testuser2/unfollow/') 
        self.assertEqual(self.response.status_code, 200)

        self.response = self.client.get('/follow/')
        self.assertEqual(self.response.status_code, 200)
        self.assertFalse(self.response.context['page'])  


    def test_comments(self):
        post_text, comment_text = 'Some text for commenting Post', 'comment fot Post'
        post = Post.objects.create(text=post_text, author=self.test_user1)

        test_user2 = User.objects.create_user(username='testuser2', password=self.test_user_pass)   
        login = self.client.login(username='testuser2', password=self.test_user_pass)               
        self.assertTrue(login)

        link_for_comment = '/testuser1/' +  str(post.id) + '/comment/'
        self.response = self.client.post(link_for_comment, data={'post':post, 'user':test_user2, 'text':comment_text})

        link_for_post = '/testuser1/' +  str(post.id) + '/'
        self.response = self.client.get(link_for_post)
        self.assertEqual(self.response.context['items'][0].text, comment_text)

        
    def test_cache(self):
        init_text = 'Some text for check cache'
        self.response = self.client.get('/')    #generate cache
        
        post = Post.objects.create(text=init_text, author = self.test_user1)
        self.response = self.client.get('/')
        self.assertIsNone(self.response.context)

        cache.clear()                           #reset cache
        self.response = self.client.get('/')
        self.assertTrue(self.response.context)

