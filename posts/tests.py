from posts.models import Post, Follow
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core.cache import cache


class PlansPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        

    def test_CheckProfilePage(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345') 
        self.response = self.client.get('/testuser1/')
        self.assertEqual(self.response.status_code, 200)


    def test_CheckPageNew(self):
        self.login = self.client.login(username='testuser1', password='12345')
        self.response = self.client.get('/new/', follow=True)
        self.assertEqual(self.response.status_code, 200)


    def test_CheckUnregisteredAction(self):
        logout = self.client.logout()
        self.response = self.client.get('/new/')
        self.assertNotEqual(self.response.status_code, 200)


    def test_CheckCreatePost(self):
        cache.clear()  
        post_text = 'test_text'
        test_user1 = User.objects.create_user(username='testuser1', password='12345') 
        login = self.client.login(username='testuser1', password='12345')
        post = Post.objects.create(text=post_text, author = test_user1)
        for test_url in ['/', '/testuser1/']:   #check index and profile pages
            self.response = self.client.get(test_url)
            self.assertEqual(post_text, self.response.context['page'].object_list[0].text)
        link_name = '/testuser1/' + str(post.id) + '/'  #check post page
        self.response = self.client.get(link_name)
        self.assertEqual(post_text, self.response.context['post'].text)


    def test_PostEdit(self):
        init_text, new_text = 'init_text', 'new_text_with_many_symbols_more_then_20'
        test_user1 = User.objects.create_user(username='testuser1', password='12345') 
        login = self.client.login(username='testuser1', password='12345')
        self.assertTrue(login)
        post = Post.objects.create(text=init_text, author = test_user1)
        link_name = '/testuser1/' + str(post.id) + '/edit/'
        self.response = self.client.get(link_name)
        self.assertEqual(self.response.status_code, 200)
        self.response = self.client.post(link_name, data = {'text': new_text, 'post_id': post.id})  #change post
        self.assertEqual(self.response.status_code, 302)                                            #check redirect
        cache.clear()                                                                               #reset cache
        for test_url in ['/', '/testuser1/']:
            self.response = self.client.get(test_url)
            self.assertEqual(new_text, self.response.context['page'].object_list[0].text)
        self.response = self.client.get('/testuser1/' + str(post.id) + '/')
        self.assertEqual(new_text, self.response.context['post'].text)

    
    def test_PageNotFound(self):
        self.response = self.client.get('/bad_url/')
        self.assertEqual(self.response.status_code, 404)


    def test_PageContent(self):
        post_text = 'test_text__________________________'
        test_user1 = User.objects.create_user(username='testuser1', password='12345') 
        login = self.client.login(username='testuser1', password='12345')
        with open("media/posts/file.jpg", mode='rb') as fp:
            post = self.client.post('/new/', {'text':post_text, 'image':fp})    #self.client.post('/new/', {'text': post_text, 'image': fp})
        cache.clear() 
        link_name = '/'  #check post page
        self.response = self.client.get(link_name)
        self.assertContains(self.response, 'img')
        cache.clear()                                                                               #reset cache
        for test_url in ['/', '/testuser1/']:
            self.response = self.client.get(test_url)
            self.assertContains(self.response, 'img')
        self.response = self.client.get('/testuser1/1/') # + str(post.id) + '/')
        self.assertContains(self.response, 'img')


    def test_NonImageUpload(self):
        post_text = 'test_text__________________________'
        test_user1 = User.objects.create_user(username='testuser1', password='12345') 
        login = self.client.login(username='testuser1', password='12345')
        with open("media/posts/homework.py", mode='rb') as fp:
            self.response = self.client.post('/new/', {'text':post_text, 'image':fp})    #self.client.post('/new/', {'text': post_text, 'image': fp})
        self.assertNotEqual(self.response.status_code, 302)                             #check redirect
        cache.clear() 
        link_name = '/'  #check post page
        self.response = self.client.get(link_name)
        self.assertNotContains(self.response, 'img')


    def test_Follow(self):
        init_text = 'new_text_for_check_exist_Post_in_follower\'s_pages'
        test_user1 = User.objects.create_user(username='testuser1', password='12345')   #create test_user1
        login = self.client.login(username='testuser1', password='12345')               #login
        self.assertTrue(login)
        test_user2 = User.objects.create_user(username='testuser2', password='12345')   #create test_user1
        self.response = self.client.get('/testuser2/follow/')                           #test_user1 is follower of test_user2
        self.assertEqual(self.response.status_code, 200)
        follow = Follow.objects.all()                                                
        self.assertEqual(follow[0].user.username, test_user1.username)
        self.assertEqual(follow[0].author.username, test_user2.username)
        post = Post.objects.create(text=init_text, author = test_user2)                 #create test Post
        self.response = self.client.get('/follow/')                                     #get favourite's page
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['page'].object_list[0].text, init_text)  #check Post exist
        self.response = self.client.get('/testuser2/unfollow/')                         #unfollow
        self.assertEqual(self.response.status_code, 200)
        self.assertFalse(Follow.objects.filter(user=test_user1.id, author=test_user2.id).exists())
        self.response = self.client.get('/follow/')
        self.assertEqual(self.response.status_code, 200)
        self.assertFalse(self.response.context['page'])                                 #check: Post is not exist


    def test_Comments(self):
        init_text = 'Some text for commenting Post'
        comment_text = 'comment fot Post'
        test_user1 = User.objects.create_user(username='testuser1', password='12345')   #create test_user1
        post = Post.objects.create(text=init_text, author = test_user1)
        test_user2 = User.objects.create_user(username='testuser2', password='12345')   #create test_user2
        login = self.client.login(username='testuser2', password='12345')               #login
        self.assertTrue(login)
        link_for_comment = '/testuser1/' +  str(post.id) + '/comment/'
        self.response = self.client.post(link_for_comment, data = {'post':post, 'user':test_user2, 'text': comment_text})
        self.response = self.client.get('/testuser1/' + str(post.id) + '/')
        self.assertEqual(self.response.context['items'][0].text, comment_text)

        
    def test_Cache(self):
        self.response = self.client.get('/')
        init_text = 'Some text for check cache'
        test_user1 = User.objects.create_user(username='testuser1', password='12345')   #create test_user1
        post = Post.objects.create(text=init_text, author = test_user1)
        self.response = self.client.get('/')
        self.assertIsNone(self.response.context)
        cache.clear()
        self.response = self.client.get('/')
        self.assertTrue(self.response.context)

