from django.urls import path
from . import views

app_name = 'experiment'

urlpatterns = [
    path('', views.ExperimentView.as_view(), name='experiment'),
    # path('<id>/', views.ExperimentUpdate.as_view(), name='edit'),
    # path('<id>/delete', views.SoftDeleteExperimentAPIView.as_view(),name='delete'),
    # path('list', views.ListActiveExperimentAPIView.as_view(), name='list_active'),
    # path('pagination', views.ListPaginatedExperimentAPIView.as_view(), name='pagination'),
]