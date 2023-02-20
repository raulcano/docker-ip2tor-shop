# Generated by Django 4.1.5 on 2023-02-17 10:41

import django.core.validators
from django.db import migrations, models
import re
import shop.validators


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_host_nostr_alias_port'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nostralias',
            name='alias',
            field=models.CharField(help_text='Alias for your Nostr public key (allowed only letters, numbers, underscore and hyphens).', max_length=100, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid'), shop.validators.validate_nostr_alias_blacklist], verbose_name='Nostr Alias'),
        ),
    ]
