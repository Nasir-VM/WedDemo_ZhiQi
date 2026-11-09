

import apps.accounts.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='代碼')),
                ('name', models.CharField(max_length=100, verbose_name='名稱')),
                ('is_active', models.BooleanField(default=True, verbose_name='啟用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='accounts.department', verbose_name='上層部門')),
            ],
            options={
                'verbose_name': '部門',
                'verbose_name_plural': '部門',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='CostCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='代碼')),
                ('name', models.CharField(max_length=100, verbose_name='名稱')),
                ('is_active', models.BooleanField(default=True, verbose_name='啟用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cost_centers', to='accounts.department', verbose_name='所屬部門')),
            ],
            options={
                'verbose_name': '成本中心',
                'verbose_name_plural': '成本中心',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('admin', '系統管理員'), ('finance', '財務'), ('manager', '部門主管'), ('employee', '一般員工'), ('auditor', '唯讀（稽核）')], default='employee', max_length=20, verbose_name='角色')),
                ('job_title', models.CharField(blank=True, max_length=100, verbose_name='職稱')),
                ('employee_no', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='員工編號')),
                ('phone', models.CharField(blank=True, max_length=30, verbose_name='聯絡電話')),
                ('must_change_password', models.BooleanField(default=False, verbose_name='首次登入須改密碼')),
                ('totp_secret', models.CharField(blank=True, max_length=64, verbose_name='TOTP 密鑰')),
                ('totp_enabled', models.BooleanField(default=False, verbose_name='啟用兩步驟驗證')),
                ('last_password_change', models.DateTimeField(blank=True, null=True, verbose_name='密碼最後變更')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('cost_center', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='accounts.costcenter', verbose_name='成本中心')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='accounts.department', verbose_name='部門')),
            ],
            options={
                'verbose_name': '使用者',
                'verbose_name_plural': '使用者',
                'indexes': [models.Index(fields=['role', 'department'], name='user_role_dept_idx')],
            },
            managers=[
                ('objects', apps.accounts.models.UserManager()),
            ],
        ),
    ]
