from rest_framework.views import APIView as DrfAPIView
from rest_framework.generics import GenericAPIView as DrfGenericAPIView
from rest_framework.viewsets import (
    ViewSet as DrfViewSet,
    ModelViewSet as DrfModelViewSet,
    GenericViewSet as DrfGenericViewSet,
)


class APIView(DrfAPIView):
    pass


class ViewSet(APIView, DrfViewSet):
    pass


class GenericAPIView(APIView, DrfGenericAPIView):
    """
    基礎 View 屬性，包含:
    - ordering_fields: "__all__"
    """

    ordering_fields = "__all__"

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        self.extra_kwargs_on_save = {}


class GenericViewSet(GenericAPIView, DrfGenericViewSet):
    pass


class ModelViewSet(GenericViewSet, DrfModelViewSet):
    def perform_create(self, serializer):
        return serializer.save(**self.extra_kwargs_on_save)

    def perform_update(self, serializer):
        return serializer.save(**self.extra_kwargs_on_save)


