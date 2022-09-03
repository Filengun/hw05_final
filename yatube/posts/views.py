from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, Follow, User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model

User =  get_user_model()

len_posts: int = 10
max_words_title: int = 30


def index(request):
    template = 'posts/index.html'
    posts_list = Post.objects.select_related('author', 'group')
    paginator = Paginator(posts_list, len_posts)
    page_namber = request.GET.get('page')
    page_ogj = paginator.get_page(page_namber)
    context = {
        'page_obj': page_ogj,
        'posts_list': posts_list,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.select_related('author')
    paginator = Paginator(posts, len_posts)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posti = author.posts.all()
    count = author.posts.count()
    paginator = Paginator(posti, len_posts)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author)
    context = {
        'page_obj': page_obj,
        'count': count,
        'author': author,
        'following': following,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id): 
    post = get_object_or_404(Post, pk=post_id)
    post_title = post.text[:max_words_title] 
    author = post.author 
    author_posts = author.posts.all().count()
    form = CommentForm()
    comments = post.comments.all()
    context = { 
        'post': post, 
        'post_title': post_title, 
        'author': author, 
        'author_posts': author_posts, 
        "form": form,
        "comments": comments,
    }
    template = 'posts/post_detail.html' 
    return render(request, template, context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST,
        files=request.FILES or None,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(f'/profile/{post.author}/', {'form': form})
    form = PostForm()
    groups = Group.objects.all()
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'groups': groups}
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    groups = Group.objects.all()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    template = 'posts/create_post.html'
    if request.user == author:
        if request.method == 'POST' and form.is_valid:
            post = form.save()
            return redirect('posts:post_detail', post_id)
        context = {
            'form': form,
            'is_edit': is_edit,
            'post': post,
            'groups': groups,
        }
        return render(request, template, context)
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts_list, len_posts)
    page_namber = request.GET.get('page')
    page_obj = paginator.get_page(page_namber)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
