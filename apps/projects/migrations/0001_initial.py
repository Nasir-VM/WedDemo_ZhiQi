

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='代碼')),
                ('name', models.CharField(max_length=80, verbose_name='名稱')),
                ('description', models.TextField(blank=True, verbose_name='說明')),
                ('is_active', models.BooleanField(default=True, verbose_name='啟用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '計畫類型',
                'verbose_name_plural': '計畫類型',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30, unique=True, verbose_name='計畫代碼')),
                ('name', models.CharField(max_length=150, verbose_name='計畫名稱')),
                ('start_date', models.DateField(verbose_name='開始日期')),
                ('end_date', models.DateField(verbose_name='結束日期')),
                ('budget_total', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='預算總額')),
                ('spent_amount', models.DecimalField(decimal_places=2, default=0, max_digits=14, verbose_name='已核銷金額')),
                ('status', models.CharField(choices=[('planning', '規劃中'), ('active', '進行中'), ('closed', '結案')], default='active', max_length=20, verbose_name='狀態')),
                ('budget_control', models.CharField(choices=[('warn', '警告'), ('block', '阻擋')], default='warn', max_length=10, verbose_name='預算控管')),
                ('description', models.TextField(blank=True, verbose_name='說明')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='accounts.department', verbose_name='部門')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='owned_projects', to=settings.AUTH_USER_MODEL, verbose_name='負責人')),
                ('project_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='projects.projecttype', verbose_name='計畫類型')),
            ],
            options={
                'verbose_name': '計畫',
                'verbose_name_plural': '計畫',
                'ordering': ['code'],
                'indexes': [models.Index(fields=['status', 'department'], name='project_status_dept_idx'), models.Index(fields=['project_type'], name='project_type_idx')],
            },
        ),
    ]
