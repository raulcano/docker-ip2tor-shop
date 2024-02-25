# Generated by Django 4.1.5 on 2023-06-14 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_remove_bandwidthextensionoption_host_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nostralias',
            name='status',
            field=models.CharField(choices=[('I', 'initial'), ('P', 'needs activate (pending)'), ('A', 'active'), ('S', 'needs suspend'), ('H', 'suspended (hold)'), ('Z', 'archived'), ('D', 'needs delete'), ('F', 'failed'), ('B', 'needs bandwidth redirect'), ('O', 'out of bandwidth')], default='I', max_length=1, verbose_name='Bridge Status'),
        ),
        migrations.AlterField(
            model_name='rsshtunnel',
            name='status',
            field=models.CharField(choices=[('I', 'initial'), ('P', 'needs activate (pending)'), ('A', 'active'), ('S', 'needs suspend'), ('H', 'suspended (hold)'), ('Z', 'archived'), ('D', 'needs delete'), ('F', 'failed'), ('B', 'needs bandwidth redirect'), ('O', 'out of bandwidth')], default='I', max_length=1, verbose_name='Bridge Status'),
        ),
        migrations.AlterField(
            model_name='torbridge',
            name='status',
            field=models.CharField(choices=[('I', 'initial'), ('P', 'needs activate (pending)'), ('A', 'active'), ('S', 'needs suspend'), ('H', 'suspended (hold)'), ('Z', 'archived'), ('D', 'needs delete'), ('F', 'failed'), ('B', 'needs bandwidth redirect'), ('O', 'out of bandwidth')], default='I', max_length=1, verbose_name='Bridge Status'),
        ),
    ]