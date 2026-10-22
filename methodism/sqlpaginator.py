from collections import OrderedDict
from math import ceil

from rest_framework.utils.urls import remove_query_param, replace_query_param


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


def _to_positive_int(value, default):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


class SqlPaginator(object):
    """
    SQL zaproslar uchun paginator.

    EXP:
        paginator = SqlPaginator(request, page=params.get('page'), per_page=20, count=total)
        sql = f"select * from table limit {paginator.limit} offset {paginator.offset}"
        ...
        return custom_response(True, data={"items": rows, **paginator.get_paginated_response()})
    """

    def __init__(self, request, page=1, per_page=15, count=1, max_per_page=None, page_query_param='page'):

        self.request = request
        self.page_num = _to_positive_int(page, 1)
        self.per_page = _to_positive_int(per_page, 15)
        if max_per_page:
            self.per_page = min(self.per_page, int(max_per_page))
        self.page_query_param = page_query_param

        try:
            self._count = int(count)
        except (TypeError, ValueError):
            self._count = None

    @property
    def count(self):
        return self._count

    @property
    def limit(self):
        """ SQL LIMIT uchun """
        return self.per_page

    @property
    def offset(self):
        """ SQL OFFSET uchun """
        return (self.page_num - 1) * self.per_page

    def get_paginated_response(self, per_page=None, current_page=None):
        return OrderedDict([
            ('count', self._count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('per_page', per_page if per_page is not None else self.per_page),
            ('current_page', current_page if current_page is not None else self.page_num),
            ('num_pages', self.num_pages()),
        ])

    def get_next_link(self):

        if not self.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)

    def has_next(self):
        return self.page_num < self.num_pages()

    def has_previous(self):
        return self.page_num > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.validate_number(self.page_num + 1)

    def previous_page_number(self):
        return self.validate_number(self.page_num - 1)

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages():
            if number == 1:
                pass
            else:
                return 1
        return number

    def num_pages(self):
        """
        Returns the total number of pages.
        """
        if not self._count:
            return 0
        return int(ceil(self._count / float(self.per_page)))
