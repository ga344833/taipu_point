# -*- coding: utf-8 -*-
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class DemoPageNumberPagination(PageNumberPagination):
    """
    自定義分頁器
    - 預設每頁 10 筆
    - 可選分頁：若 URL 無 page 參數，返回全部資料
    - 自訂回應格式
    """
    page_size = 10
    page_size_query_param = "size"
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        if "page" not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view=None)

    def get_paginated_response(self, data):
        """
        格式修正為模仿Rapid7官方分頁回應
        {"page": {
            "size": <目前所使用一頁顯示筆數>,
            "totalPages": <總頁數>,
            "totalResources": <總資料筆數>
        }}
        """
        totalResources = self.page.paginator.count
        size = self.get_page_size(self.request)

        quotient, remainder = divmod(totalResources, size)
        totalPages = quotient + 1 if remainder > 0 else quotient
        return Response(
            {
                "page": {
                    "size": size,
                    "totalPages": totalPages,
                    "totalResources": totalResources,
                },
                "results": data,
            }
        )


class LimitOffsetPaginatorInspectorClass:
    """
    如何客製化Pagination於swagger document顯示內容
    注意views使用時的掛載動作, 否則無法生效此物件功能
    https://stackoverflow.com/questions/66124992/drf-yasg-show-custom-pagination-for-listapiview-in-swagger-docs
    """

    def get_paginated_response(self, paginator, response_schema):
        """
        :param BasePagination paginator: the paginator
        :param openapi.Schema response_schema: the response schema that must be paged.
        :rtype: openapi.Schema
        """

        return inline_serializer(
            name="ResponseSerializer",
            fields={
                "page": inline_serializer(
                    name="PageSerializer",
                    fields={
                        "size": serializers.IntegerField(),
                        "totalPages": serializers.IntegerField(),
                        "totalResources": serializers.IntegerField(),
                    },
                ),
                "results": response_schema,
            },
            required=["results"],
        )


