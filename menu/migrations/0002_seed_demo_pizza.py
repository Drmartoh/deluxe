# Data migration: one demo pizza with sizes so cart/checkout can be tested.

from decimal import Decimal

from django.db import migrations


def seed_demo_pizza(apps, schema_editor):
    Category = apps.get_model("menu", "Category")
    Product = apps.get_model("menu", "Product")
    ProductVariant = apps.get_model("menu", "ProductVariant")

    # Avoid UNIQUE name/slug clashes if admin already created a Pizza category.
    cat = Category.objects.filter(slug="pizza").first()
    if not cat:
        cat = Category.objects.filter(name__iexact="pizza").first()
    if not cat:
        cat = Category.objects.create(
            name="Pizza",
            slug="pizza",
            emoji="🍕",
            is_active=True,
        )

    product, created = Product.objects.get_or_create(
        slug="margherita-demo",
        defaults={
            "category": cat,
            "name": "Margherita — Demo",
            "description": "Test pizza: tomato, mozzarella, basil. Use Add to Cart below.",
            "is_active": True,
            "is_featured": True,
        },
    )
    if not created:
        product.is_active = True
        product.is_featured = True
        product.save(update_fields=["is_active", "is_featured"])

    sizes = [
        ("small", Decimal("499.00"), False),
        ("medium", Decimal("799.00"), True),
        ("large", Decimal("1099.00"), False),
    ]
    for size, price, is_default in sizes:
        ProductVariant.objects.get_or_create(
            product=product,
            size=size,
            defaults={"price": price, "is_default": is_default},
        )


def unseed_demo_pizza(apps, schema_editor):
    Product = apps.get_model("menu", "Product")
    Product.objects.filter(slug="margherita-demo").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_pizza, unseed_demo_pizza),
    ]
