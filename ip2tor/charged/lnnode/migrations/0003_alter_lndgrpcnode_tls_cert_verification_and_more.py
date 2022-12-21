# Generated by Django 4.1.4 on 2022-12-20 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lnnode', '0002_alter_lndgrpcnode_tls_cert_verification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lndgrpcnode',
            name='tls_cert_verification',
            field=models.BooleanField(default=True, help_text='Verify TLS connections using the provided certificate? Should *always* be *enabled* in production.', verbose_name='TLS Verification'),
        ),
        migrations.AlterField(
            model_name='lndrestnode',
            name='tls_cert_verification',
            field=models.BooleanField(default=True, help_text='Verify TLS connections using the provided certificate? Should *always* be *enabled* in production.', verbose_name='TLS Verification'),
        ),
    ]
