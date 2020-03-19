from django.conf.urls import url
from info import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^robots\.txt$', TemplateView.as_view(
        template_name="core/robots.txt", content_type='text/plain')),
    url(r'^$', views.identification, name='home'),
    url(r'^symptoms', views.get_symptoms, name='symptoms'),
    url(r'^verification', views.verify_user, name='verification'),
    url(r'^results', views.results, name='results')
]
