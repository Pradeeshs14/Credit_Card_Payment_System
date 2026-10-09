from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0002_card_credit_limit_card_is_blocked"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="credit_limit",
            field=models.DecimalField(
                max_digits=10,
                decimal_places=2,
                default=50000.00,
            ),
        ),
    ]
