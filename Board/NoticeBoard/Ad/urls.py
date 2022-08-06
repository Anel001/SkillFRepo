from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import AdList, AdDetail, AdCreate, AdUpdate, AdDelete, ComList, update_comment, ComDelete
from .views import subscribe_category, unsubscribe_category
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('', AdList.as_view()),
    path('<int:pk>', AdDetail.as_view(), name='ad.html'),
    path('add/', AdCreate.as_view(), name='ad_create.html'),
    path('edit/<int:pk>', AdUpdate.as_view(), name='ad_create.html'),
    path('delete/<int:pk>', AdDelete.as_view(), name='ad_delete.html'),
    path('comments/', ComList.as_view(), name='comments.html'),
    path('subscribe/<int:pk>', subscribe_category, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe_category, name='unsubscribe'),
    #ajax
    path('update_comment/<int:pk>/<slug:type>', update_comment, name='update_comment'),
    path('comments/delete/<int:pk>', ComDelete.as_view(), name='com_delete.html'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
