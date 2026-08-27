from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Blog


def blog_list(request):
    blogs_qs = Blog.objects.all().order_by('-published_date')
    paginator = Paginator(blogs_qs, 6)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    return render(request, 'blog/blogs.html', {'blogs': blogs})


def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blog/blog_details.html', {'blog': blog})
