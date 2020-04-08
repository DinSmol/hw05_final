from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Post, Group, User, Comment, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Count

# Create your views here.

@cache_page(20)
def index(request):
    post_list = Post.objects.annotate(comment_count = Count('comments')).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    context = {'page': page, 
                'paginator': paginator}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 5) # показывать по 10 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, "group.html", {"group": group, 'page': page, 'paginator': paginator})  #, "posts": posts})


@login_required
def new_post(request):
    titles = {'title': 'Добавление записи',
                'form_title': 'Добавить запись',
                'button_text': 'Добавить'
    }  
    if request.method == 'POST':    
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.author = request.user # add the logged in user, as the author
            temp.save()
            return redirect('index')
        return render(request, 'new_post.html', {'titles': titles, 'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'titles': titles, 'form': form})    


def profile(request, username):
    author = get_object_or_404(User, username=username)
    follower_num = author.follower.all().count()
    following_num = author.following.all().count()
    post_cnt = Post.objects.filter(author__username=username).count()
    post_list = Post.objects.filter(author__username=username).order_by("-pub_date").all()
    paginator = Paginator(post_list, 3) # показывать по 3 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    following = Follow.objects.filter(user=request.user.id, author=User.objects.get(username=username).id)
    context = {'username': username, 
                'author': author, 
                'post_cnt': post_cnt, 
                'page': page, 
                'paginator': paginator, 
                'following': following,
                'follower_num': follower_num,
                'following_num': following_num}
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_cnt = Post.objects.filter(author__username=username).count()
    author = Post.objects.get(id=post_id).author 
    form = CommentForm(request.POST)
    items = Comment.objects.filter(post = Post.objects.get(id=post_id))
    import pdb
    # pdb.set_trace()
    follower_num = author.follower.all().count()
    following_num = author.following.all().count()
    context = {'username': username, 
                'author': author, 
                'post_cnt': post_cnt, 
                'post': post, 
                'form': form, 
                'items': items, 
                'follower_num': follower_num,
                'following_num': following_num}
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    titles = {'title': 'Редактирование записи',
                'form_title': 'Редактировать запись',
                'button_text': 'Сохранить'}   
    post = Post.objects.get(id=post_id) 
    items = post.comments.all()
    current_user = request.user
    if str(current_user) != username:   #check post's author
        return redirect('post', username, post_id)
    if request.method == 'POST':   
        form = PostForm(request.POST)
        if form.is_valid():
            form = PostForm(request.POST, files=request.FILES or None, instance=post)
            form.save()
            return redirect('post', username, post_id)
        return render(request, 'new_post.html', {'titles': titles, 'form': form})
    text, group = Post.objects.get(id=post_id).text, Post.objects.get(id=post_id).group 
    form = PostForm(initial={'text': text,'group': group})
    return render(request, 'new_post.html', {'titles': titles, 'form': form, 'post': post, 'items': items}) 

@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id) 
    if request.method == 'POST':    
        form = CommentForm(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            temp.author = User.objects.get(username=username) #request.user # add the logged in user, as the author
            temp.post = Post.objects.get(id=post_id) 
            temp.save()
            return redirect('post', username, post_id)
        return render(request, 'comments.html', {'form': form})

    form = CommentForm()
    return render(request, 'comments.html', {'post': post, 'form': form}) 


@login_required
def follow_index(request):
    author = User.objects.get(username=request.user)
    follow = author.follower.all()
    authors = [item.author for item in follow]
    post_cnt = Post.objects.filter(author__username__in=authors).count()
    post_list = Post.objects.filter(author__username__in=authors).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 3 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    context = {'author': author, 
                'post_cnt': post_cnt, 
                'page': page, 
                'paginator': paginator }
    return render(request, "follow.html", context)

@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=user, author=author).exists()
    # followobj = Follow.objects.get(user=request.user, author=User.objects.get(username=username))
    if(user != author and follow is False):
        follow = Follow.objects.create(user=user, author=author)
    # author = User.objects.get(username=username)
    post_cnt = Post.objects.filter(author__username=username).count()
    post_list = Post.objects.filter(author__username=username).order_by("-pub_date").all()
    paginator = Paginator(post_list, 3) # показывать по 3 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    context = {'username': username, 
                'author': author, 
                'post_cnt': post_cnt, 
                'page': page, 
                'paginator': paginator }
    return render(request, 'index.html', context) 


@login_required
def profile_unfollow(request, username):
    follow_delete = Follow.objects.get(user=request.user, author=User.objects.get(username=username))
    follow_delete.delete()
    author = User.objects.get(username=username)
    post_cnt = Post.objects.filter(author__username=username).count()
    post_list = Post.objects.filter(author__username=username).order_by("-pub_date").all()
    paginator = Paginator(post_list, 3) # показывать по 3 записей на странице
    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    context = {'username': username, 
                'author': author, 
                'post_cnt': post_cnt, 
                'page': page, 
                'paginator': paginator}
    return render(request, 'index.html', context) 


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
        return render(request, "misc/500.html", status=500)

