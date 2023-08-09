from collections import OrderedDict
from math import ceil

from rest_framework.utils.urls import remove_query_param, replace_query_param

class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass

class SqlPaginator(object):

    def __init__(self, request, page=1, per_page=15, count=1):

        self.request = request
        self.page_num = int(page)
        self.per_page = int(per_page)
        self.page_query_param = 'page'

        try:
            self._count = int(count)
        except TypeError:
            self._count = None

    def get_paginated_response(self, per_page=None, current_page=None):
        return OrderedDict([
            ('count', self._count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('per_page', per_page),
            ('current_page', current_page),
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
        if self._count == 0:
            return 0
        return int(ceil(self._count / float(self.per_page)))

