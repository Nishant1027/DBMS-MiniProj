from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
import markdown
from articles.forms import ArticleForm
from articles.models import Article, ArticleComment
from mentor001.decorators import ajax_required
from articles.decorators import UserIsMentorMixin, user_is_mentor


def _articles(request, articles):
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)

    except PageNotAnInteger:
        articles = paginator.page(1)

    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return render(request, 'articles/articles.html', {
        'articles': articles,
    })


class CreateArticle(LoginRequiredMixin, UserIsMentorMixin, CreateView):
    template_name = 'articles/write.html'
    form_class = ArticleForm
    success_url = reverse_lazy('articles')

    def form_valid(self, form):
        form.instance.create_user = self.request.user
        return super(CreateArticle, self).form_valid(form)


class EditArticle(LoginRequiredMixin, UserIsMentorMixin, UpdateView):
    template_name = 'articles/edit.html'
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('articles')


@login_required
def articles(request):
    all_articles = Article.get_published()
    return _articles(request, all_articles)


@login_required
def article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.published)
    return render(request, 'articles/article.html', {'article': article})


@login_required
def drafts(request):
    drafts = Article.objects.filter(create_user=request.user,
                                    status=Article.draft)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


@login_required
@user_is_mentor
@ajax_required
def preview(request):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            html = 'Nothing to display :('
            if len(content.strip()) > 0:
                html = markdown.markdown(content, safe_mode='escape')

            return HttpResponse(html)

        else:
            return HttpResponseBadRequest()

    except Exception:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def comment(request):
    if request.method == 'POST':
        article_id = request.POST.get('article')
        article = Article.objects.get(pk=article_id)
        comment = request.POST.get('comment')
        comment = comment.strip()
        if len(comment) > 0:
            article_comment = ArticleComment(user=request.user,
                                             article=article,
                                             comment=comment)
            article_comment.save()
            user = request.user
            user.profile.notify_article_commented(article)
        html = ''
        for comment in article.get_comments():
            html = '{0}{1}'.format(html, render_to_string(
                'articles/partial_article_comment.html',
                {'comment': comment}))

        return HttpResponse(html)

    else:
        return HttpResponseBadRequest()
