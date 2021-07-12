# Generated by Django 3.2.4 on 2021-07-12 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_listing_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='category',
            field=models.CharField(choices=[('JANUARY', 'January'), ('FEBRUARY', 'February'), ('MARCH', 'March'), ('DECEMBER', 'December')], default='JANUARY', max_length=64),
        ),
    ]
