from blog.forms import CommentForm, PostForm, ProfileEditForm
from blog.models import Category, Comment, Post
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

User = get_user_model()


def _get_q_available(request: HttpRequest, *, own: bool = True) -> Q:
    q_available = Q(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    if own and request.user.is_authenticated:
        q_available = q_available | Q(author=request.user)
    return q_available


def index(request: HttpRequest) -> HttpResponse:
    posts = (
        Post.objects.filter(_get_q_available(request, own=False))
        .order_by('-pub_date')
        .select_related('category', 'author', 'location')
        .annotate(comment_count=Count('comments'))
    )

    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    qs = (
        Post.objects.filter(Q(pk=post_id), _get_q_available(request))
        .order_by('-pub_date')
        .select_related('category', 'author', 'location')
    )
    post = get_object_or_404(qs)

    form = CommentForm(initial={'author': request.user, 'post': post})
    comments = (
        Comment.objects.filter(post=post)
        .order_by('created_at')
        .select_related('author', 'post')
    )

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
        },
    )


def category_posts(request: HttpRequest, slug: str) -> HttpResponse:
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = (
        category.posts.filter(_get_q_available(request, own=False))
        .order_by('-pub_date')
        .select_related('category', 'author', 'location')
        .annotate(comment_count=Count('comments'))
    )

    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(
        request,
        'blog/category.html',
        {
            'page_obj': page_obj,
            'category': category,
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    user = get_object_or_404(User, username=username)
    posts = (
        user.posts.filter(_get_q_available(request))
        .order_by('-pub_date')
        .select_related('category', 'author', 'location')
        .annotate(comment_count=Count('comments'))
    )

    page_obj = Paginator(posts, 10).get_page(request.GET.get('page'))
    return render(
        request,
        'blog/profile.html',
        {
            'profile': user,
            'page_obj': page_obj,
        },
    )


@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    form = ProfileEditForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(
    request: HttpRequest, post_id: int | None = None
) -> HttpResponse:
    if post_id is not None:
        instance = get_object_or_404(
            Post,
            Q(id=post_id),
            _get_q_available(request),
        )
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
    else:
        instance = None
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        initial={
            'pub_date': timezone.now(),
        },
        instance=instance,
    )
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.is_published = True
        post.save()
        if post_id is None:
            return redirect('blog:profile', username=request.user.username)
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request: HttpRequest, post_id: int) -> HttpResponse:
    instance = get_object_or_404(
        Post,
        Q(id=post_id),
        _get_q_available(request),
    )
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(
    request: HttpRequest, post_id: int, comment_id: int | None = None
) -> HttpResponse:
    instance = get_object_or_404(
        Post,
        Q(id=post_id),
        _get_q_available(request),
    )
    if comment_id is None:
        # add comment
        if request.method != 'POST':
            return redirect('blog:post_detail', post_id=post_id)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment: Comment = form.save(commit=False)
            comment.post = instance
            comment.author = request.user
            comment.is_published = True
            comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    # edit comment
    qs = Comment.objects.filter(id=comment_id).select_related('post', 'author')
    comment = get_object_or_404(qs)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(
        request, 'blog/comment.html', {'form': form, 'comment': comment}
    )


@login_required
def delete_comment(
    request: HttpRequest, post_id: int, comment_id: int
) -> HttpResponse:
    instance = get_object_or_404(
        Post,
        Q(id=post_id),
        _get_q_available(request),
    )

    qs = Comment.objects.filter(post=instance, id=comment_id).select_related(
        'post', 'author'
    )
    comment = get_object_or_404(qs)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})
