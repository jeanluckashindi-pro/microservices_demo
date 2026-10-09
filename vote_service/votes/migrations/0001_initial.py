from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Titre')),
                ('description', models.TextField(verbose_name='Description')),
                ('created_by_user_id', models.IntegerField(verbose_name='ID créateur')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
            ],
            options={'verbose_name': 'Sujet', 'verbose_name_plural': 'Sujets', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='ID utilisateur')),
                ('choice', models.CharField(choices=[('for', 'Pour'), ('against', 'Contre'), ('abstain', 'Abstention')], max_length=10, verbose_name='Choix')),
                ('voted_at', models.DateTimeField(auto_now_add=True, verbose_name='Voté le')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='votes.topic')),
            ],
            options={'verbose_name': 'Vote', 'verbose_name_plural': 'Votes', 'unique_together': {('topic', 'user_id')}},
        ),
    ]
