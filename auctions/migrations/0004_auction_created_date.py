# Generated by Django 5.0.7 on 2024-08-17 07:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0003_alter_auction_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="auction",
            name="created_date",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
