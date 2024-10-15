from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def sum_column(salary_table, month):
    return sum(row.get(month, 0) for row in salary_table)