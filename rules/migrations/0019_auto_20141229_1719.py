# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0018_auto_20141229_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 29, 17, 19, 57, 423323), verbose_name=b'date created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sourceatversion',
            name='updated_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 29, 17, 19, 57, 422642), verbose_name=b'date updated', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sourceupdate',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2014, 12, 29, 17, 19, 57, 422970), verbose_name=b'date of update', blank=True),
            preserve_default=True,
        ),
    ]
