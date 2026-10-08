from django.db import migrations, models # type: ignore


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='is_blocked',
            field=models.BooleanField(default=False),
        ),
    ]