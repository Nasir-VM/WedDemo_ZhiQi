

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(default='志氣企業', max_length=100, verbose_name='公司名稱')),
                ('announcement', models.TextField(blank=True, verbose_name='公司公告')),
                ('announcement_updated_at', models.DateTimeField(blank=True, null=True, verbose_name='公告更新時間')),
                ('approval_threshold', models.DecimalField(decimal_places=2, default=Decimal('50000.00'), max_digits=14, verbose_name='加簽金額門檻')),
                ('default_tax_rate', models.DecimalField(decimal_places=2, default=Decimal('5.00'), max_digits=5, verbose_name='預設稅率(%)')),
                ('dashboard_cache_seconds', models.PositiveSmallIntegerField(default=60, verbose_name='Dashboard 快取秒數')),
                ('backup_retention', models.PositiveSmallIntegerField(default=14, verbose_name='備份保留份數')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '系統設定',
                'verbose_name_plural': '系統設定',
            },
        ),
    ]
