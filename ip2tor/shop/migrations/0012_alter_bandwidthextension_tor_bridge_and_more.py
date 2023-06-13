# Generated by Django 4.1.5 on 2023-06-10 06:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_bandwidthextension'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bandwidthextension',
            name='tor_bridge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bandwidth_extensions', to='shop.torbridge'),
        ),
        migrations.CreateModel(
            name='BandwidthExtensionOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('duration', models.BigIntegerField(default=2592000, help_text='Lifetime of this extension in seconds, from the moment of its purchase. Any unused bandwidth after the expiry date will be lost.', verbose_name='Extension duration (seconds)')),
                ('bandwidth', models.BigIntegerField(default=1073741824, help_text='Amount of traffic purchased. That is, bandwidth in bytes that can be used during the life of this extension.', verbose_name='Offered traffic allocation (bandwidth in bytes)')),
                ('price', models.BigIntegerField(default=20000000, help_text='Price in milli-satoshi of this extension.', verbose_name='Bandwidth extension price (mSAT)')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bandwidth_extension_options', to='shop.host')),
            ],
        ),
    ]
