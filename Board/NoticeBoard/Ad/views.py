from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from .models import Notice, Author, Comment, Category, UserCategory
from .forms import NoticeForm, NoticeEditForm, ComForm
from .filters import CommentFilter
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.core.mail import send_mail
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache


class AdList(LoginRequiredMixin, ListView):
    model = Notice
    ordering = 'date_create'
    template_name = 'ads.html'
    context_object_name = 'ads'
    paginate_by = 5


class CustomSuccessMessageMixin:
    @property
    def success_msg(self):
        return False

    def form_valid(self, form):
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)


@receiver(post_save, sender=Comment)
def notify_author(sender, instance, created, **kwargs):
    if instance.status:
        send_mail(
            subject=f'{instance.User.username}, Your comment approved by {instance.notice.Author.authUser.username}',
            message=instance.com_text,
            from_email='anel031@yandex.ru',
            recipient_list=[instance.User.email]
        )
    else:
        send_mail(
            subject=f'{instance.notice.Author.authUser.username}, You got comment from {instance.User.username}',
            message=instance.com_text,
            from_email='anel031@yandex.ru',
            recipient_list=[instance.notice.Author.authUser.email]
        )


@receiver(post_save, sender=UserCategory)
def notify_author(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject=f'{instance.user.username}, подписка на рассылку',
            message=f'Вы подписаны на категорию {instance.category.category_name}',
            from_email='anel031@yandex.ru',
            recipient_list=[instance.user.email]
        )


@receiver(post_save, sender=Notice)
def post(sender, instance, *args, **kwargs):
    cat_id = instance.category.id
    users = UserCategory.objects.filter(category_id=cat_id)
    for i in users:
        send_mail(
            subject=f"{instance.title}",
            message=f"Здравствуй, {i.user.username}."
                    f" Новая статья в твоём любимом разделе! \n Заголовок статьи: {instance.title} \n"
                    f" Текст статьи: {instance.content}",
            from_email='anel031@yandex.ru',
            recipient_list=[i.user.email]
        )


class AdDetail(LoginRequiredMixin, FormMixin, DetailView):
    model = Notice
    template_name = 'ad.html'
    context_object_name = 'ad'
    form_class = ComForm
    success_url = '/posts/'

    def get_success_url(self, **kwargs):
        return reverse_lazy('ad.html', kwargs={'pk': self.get_object().id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['truecount'] = Comment.objects.filter(notice=self.get_object(), status=True).count()
        context['is_subscribed'] = UserCategory.objects.filter(user=self.request.user,
                                                               category=self.get_object().category).exists()
        return context

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}', None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.notice = self.get_object()
        self.object.User = self.request.user
        self.object.save()
        return super().form_valid(form)


class AdCreate(LoginRequiredMixin, CreateView):
    model = Notice
    template_name = 'ad_create.html'
    form_class = NoticeForm

    def get_initial(self):
        initial = super(AdCreate, self).get_initial()
        initial.update({'Author': Author.objects.get(authUser=self.request.user)})
        return initial

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.Author = Author.objects.get(authUser=self.request.user)
        self.object.save()
        return redirect(self.get_success_url())


class AdUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'ad_create.html'
    form_class = NoticeEditForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Notice.objects.get(pk=id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user != kwargs['instance'].Author.authUser:
            return self.handle_no_permission()
        return kwargs


class AdDelete(LoginRequiredMixin, DeleteView):
    template_name = 'ad_delete.html'
    queryset = Notice.objects.all()
    context_object_name = 'ad'
    success_url = '/posts/'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.Author.authUser:
            return self.handle_no_permission()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class ComList(LoginRequiredMixin, ListView):
    model = Comment
    ordering = '-com_date'
    template_name = 'comments.html'
    context_object_name = 'comments'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user.id
        context['filter'] = CommentFilter(self.request.GET, queryset=self.get_queryset())
        return context


@login_required()
def update_comment(request, pk, type):
    item = Comment.objects.get(pk=pk)
    if type == 'public':
        item.status = True
        item.save()
        return HttpResponse('Принято')
    elif type == 'delete':
        item.delete()
        return HttpResponse('Отклонено')


@login_required()
def subscribe_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    subscriber = UserCategory(user_id=user.id, category_id=category.id)
    subscriber.save()
    return redirect('/posts/')


@login_required()
def unsubscribe_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    subscriber = UserCategory.objects.get(user_id=user.id, category_id=category.id)
    subscriber.delete()
    return redirect('/posts/')


class ComDelete(LoginRequiredMixin, DeleteView):
    template_name = 'com_delete.html'
    queryset = Comment.objects.all()
    context_object_name = 'comment'
    success_url = '/posts/comments'
