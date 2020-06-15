# Generated by Django 2.2.8 on 2020-01-04 11:52

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gamemode', '0001_initial'),
        ('game', '0001_initial'),
        ('platform', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('rules', models.CharField(blank=True, max_length=2048, null=True)),
                ('prize', models.CharField(blank=True, max_length=512, null=True)),
                ('contact_info', models.CharField(blank=True, max_length=256, null=True)),
                ('title', models.CharField(max_length=64)),
                ('winner', models.CharField(blank=True, default=None, max_length=20, null=True)),
                ('organizer', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=2048)),
                ('size', models.IntegerField()),
                ('total_participants', models.IntegerField(default=0)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(blank=True, default=None, null=True)),
                ('notifications', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), blank=True, null=True, size=None)),
                ('extra_fields', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_by', to=settings.AUTH_USER_MODEL)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='game.Game')),
                ('game_mode', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gamemode.GameMode')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='platform.Platform')),
            ],
            options={
                'ordering': ['start'],
                'verbose_name_plural': 'Tournaments',
            },
        ),
    ]