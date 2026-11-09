

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
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=150, verbose_name='帳號快照')),
                ('action', models.CharField(choices=[('create', '新增'), ('update', '修改'), ('delete', '刪除'), ('login', '登入'), ('logout', '登出'), ('login_failed', '登入失敗'), ('export', '匯出'), ('permission_change', '權限變更'), ('backup', '備份'), ('restore', '還原')], db_index=True, max_length=30, verbose_name='動作')),
                ('model_label', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='物件類型')),
                ('object_id', models.CharField(blank=True, max_length=64, verbose_name='物件 ID')),
                ('object_repr', models.CharField(blank=True, max_length=255, verbose_name='物件摘要')),
                ('changes', models.JSONField(blank=True, default=dict, verbose_name='差異')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('user_agent', models.CharField(blank=True, max_length=255, verbose_name='User-Agent')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='時間')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'verbose_name': '稽核日誌',
                'verbose_name_plural': '稽核日誌',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['model_label', 'object_id'], name='audit_model_object_idx'), models.Index(fields=['user', 'created_at'], name='audit_user_time_idx')],
            },
        ),
    ]
