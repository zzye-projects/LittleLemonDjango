# Generated by Django 4.2.16 on 2024-09-28 14:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0003_alter_order_date_alter_order_total_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateField(db_index=True, default=datetime.datetime(2024, 9, 28, 14, 24, 46, 235729)),
        ),
    ]
