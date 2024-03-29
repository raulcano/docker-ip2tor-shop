# Generated by Django 4.1.5 on 2023-01-30 16:14

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re
import shop.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_host_is_test_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='host',
            name='nostr_alias_duration',
            field=models.BigIntegerField(default=86400, help_text='Lifetime of Alias (either initial or extension).', verbose_name='Alias Duration (seconds)'),
        ),
        migrations.AddField(
            model_name='host',
            name='nostr_alias_port',
            field=models.PositiveSmallIntegerField(default=80, help_text='At which port will the host access the Nostr Aliases. E.g. nostr_alias.com:80', verbose_name='Nostr Alias Port'),
        ),
        migrations.AddField(
            model_name='host',
            name='nostr_alias_price_extension',
            field=models.BigIntegerField(default=20000, help_text='Price of a Nostr Alias in milli-satoshi for extending existing bridge.', verbose_name='Alias Extension Price (mSAT)'),
        ),
        migrations.AddField(
            model_name='host',
            name='nostr_alias_price_initial',
            field=models.BigIntegerField(default=25000, help_text='Price of a Nostr Alias in milli-satoshi for initial Purchase.', verbose_name='Alias Price (mSAT)'),
        ),
        migrations.AddField(
            model_name='host',
            name='offers_nostr_aliases',
            field=models.BooleanField(default=False, verbose_name='Does host offer Nostr Aliases?'),
        ),
        migrations.CreateModel(
            name='NostrAlias',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('status', models.CharField(choices=[('I', 'initial'), ('P', 'needs activate (pending)'), ('A', 'active'), ('S', 'needs suspend'), ('H', 'suspended (hold)'), ('Z', 'archived'), ('D', 'needs delete'), ('F', 'failed')], default='I', max_length=1, verbose_name='Bridge Status')),
                ('port', models.PositiveIntegerField(blank=True, editable=False, help_text='Port - Must be in range 10000 - 65535.', null=True, validators=[django.core.validators.MinValueValidator(10000), django.core.validators.MaxValueValidator(65535)], verbose_name='Port')),
                ('comment', models.CharField(blank=True, max_length=42, null=True, verbose_name='Bridge/Tunnel comment')),
                ('suspend_after', models.DateTimeField(blank=True, null=True, verbose_name='suspend after')),
                ('is_monitored', models.BooleanField(default=True, verbose_name='Is bridge actively monitored?')),
                ('alias', models.CharField(help_text='Alias for your Nostr public key (allowed only letters, numbers, underscore and hyphens).', max_length=100, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid'), shop.validators.validate_nostr_alias_blacklist], verbose_name='Nostr Alias')),
                ('public_key', models.CharField(help_text='The public key that identifies you in the Nostr network.', max_length=5000, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid'), shop.validators.validate_nostr_pubkey], verbose_name='Nostr Public Key')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.host')),
            ],
            options={
                'verbose_name': 'Nostr Alias',
                'verbose_name_plural': 'Nostr Aliases',
                'ordering': ['-created_at'],
            },
        ),
    ]
