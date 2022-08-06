from django.db import models
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.cache import cache


class Author(models.Model):
    authUser = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f' {self.authUser}'


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        author = Author.objects.create(authUser=user)
        author.save()
        return user


class Category(models.Model):
    tank = 'TK'
    hill = 'HL'
    dd = 'DD'
    seller = 'SL'
    gmast = 'GM'
    kgiv = 'KG'
    smith = 'KZ'
    tanner = 'TN'
    pois = 'ZV'
    spell = 'SP'
    choice = [(tank, 'Танки'), (hill, 'Хилы'), (dd, 'ДД'),
              (seller, 'Торговцы'), (gmast, 'Гилдмастеры'),
              (kgiv, 'Квестгиверы'), (smith, 'Кузнецы'),
              (tanner, 'Кожевники'), (pois, 'Зельевары'),
              (spell, 'Мастера заклинаний')]
    category_name = models.CharField(max_length=2, choices=choice)
    subscribers = models.ManyToManyField(User, through='UserCategory', related_name='subscribers')

    def __str__(self):
        return f' {self.category_name}'


class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)


class Notice(models.Model):
    Author = models.ForeignKey(Author, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = RichTextUploadingField()
    date_create = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    
    def get_absolute_url(self):
        return f'/posts/{self.id}'

    def __str__(self):
        return f'{self.title} {self.content}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post{self.pk}')


class Comment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='comments')
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    com_text = models.TextField(verbose_name='Текст комментария')
    com_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(verbose_name="Видимость комментария", default=False)

    def get_absolute_url(self):
        return f'/posts/comments/{self.id}'

    def __str__(self):
        return 'Comment by {} on {}'.format(self.User, self.notice)


