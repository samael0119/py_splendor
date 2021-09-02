from sqlalchemy.orm.session import query


class PageHelper:

    def __init__(self, q: query, page_size):
        self._query = q
        self._page_size = page_size
        self._total_page = q.count()

    def get_page(self, page_no):
        if page_no > (self._total_page / self._page_size) + 1:
            return []
        return self._query.limit((page_no - 1) * self._page_size).offset(self._page_size)

    def get_next_page(self, current_page_no):
        if current_page_no * self._page_size > self._total_page:
            return []
        return self._query.limit(current_page_no * self._page_size).offset(self._page_size)

    def get_pre_page(self, current_page_no):
        if current_page_no <= 1:
            return []
        return self._query.limit((current_page_no - 2) * self._page_size).offset(self._page_size)

    def get_total_page(self):
        return self._total_page
