# Generated by Django 3.2.4 on 2021-07-15 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0011_rename_bidder_comment_writer'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_listing',
            field=models.ManyToManyField(related_name='watchlist', to='auctions.Listing'),
        ),
    ]