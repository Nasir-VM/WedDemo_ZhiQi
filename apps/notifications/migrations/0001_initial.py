

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='標題')),
                ('message', models.TextField(blank=True, verbose_name='內容')),
                ('url', models.CharField(blank=True, max_length=300, verbose_name='連結')),
                ('level', models.CharField(choices=[('info', '資訊'), ('success', '成功'), ('warning', '提醒'), ('danger', '警示')], default='info', max_length=20, verbose_name='等級')),
                ('is_read', models.BooleanField(default=False, verbose_name='已讀')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='建立時間')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='收件人')),
            ],
            options={
                'verbose_name': '站內通知',
                'verbose_name_plural': '站內通知',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['user', 'is_read', 'created_at'], name='notif_user_read_idx')],
            },
        ),
    ]
