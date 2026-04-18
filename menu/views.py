from django.db.models import Prefetch
from django.shortcuts import render

from .models import Category, Product


def menu_list(request):
    categories = (
        Category.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "products",
                queryset=Product.objects.filter(is_active=True).prefetch_related(
                    "variants"
                ),
            )
        )
        .order_by("name")
    )
    return render(request, "menu/menu_list.html", {"categories": categories})
