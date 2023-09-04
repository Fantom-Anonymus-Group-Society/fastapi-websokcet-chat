from math import ceil


class PaginationService:
    @staticmethod
    def get_pagination_data(count: int, elem_per_page: int = 20):
        return {
            'pages': [*range(1, ceil(count / elem_per_page) + 1)],
            'count': count,
            'per_page': elem_per_page
        }
