from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ReviewPagination(PageNumberPagination):
    page_size = 5  # default items per page
    page_size_query_param = 'page_size'  # allow frontend to override
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            "page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "total_reviews": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "results": data,
        })
