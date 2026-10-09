from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='ID utilisateur')),
                ('event_type', models.CharField(max_length=100, verbose_name="Type d’événement")),
                ('message', models.TextField(verbose_name='Message')),
                ('is_read', models.BooleanField(default=False, verbose_name='Lu')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créée le')),
            ],
            options={'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications', 'ordering': ['-created_at']},
        ),
    ]
