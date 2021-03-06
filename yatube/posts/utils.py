from django.core.paginator import Paginator


def paginator_util(page_number, post_list):
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page_number)
    return page_obj
