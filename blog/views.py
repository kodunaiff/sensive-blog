from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.db.models import Prefetch


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    all_posts = Post.objects.prefetch_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts'))))
    most_popular_posts = all_posts.popular()[:5].fetch_with_comments_count()
    most_fresh_posts = all_posts.order_by('-published_at')[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    queryset = Post.objects.annotate(likes_count=Count('likes'))
    post = get_object_or_404(queryset, slug=slug)
    comments = Comment.objects.filter(post=post).prefetch_related('author')

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.annotate(posts_count=Count('posts'))

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]
    all_posts = Post.objects.prefetch_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts'))))
    most_popular_posts = all_posts.popular()[:5].fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    all_posts = Post.objects.prefetch_related('author').prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(posts_count=Count('posts'))))
    most_popular_posts = all_posts.popular()[:5].fetch_with_comments_count()

    most_popular_tags = Tag.objects.popular()[:5]

    related_posts = tag.posts.prefetch_related("author")[:20].prefetch_related(
        Prefetch('tags', queryset=Tag.objects.annotate(
            posts_count=Count('posts')))).fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
