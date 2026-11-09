

import apps.expenses.models
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='代碼')),
                ('name', models.CharField(max_length=80, verbose_name='名稱')),
                ('description', models.TextField(blank=True, verbose_name='說明')),
                ('is_active', models.BooleanField(default=True, verbose_name='啟用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '費用科目',
                'verbose_name_plural': '費用科目',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='DocumentSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scope', models.CharField(max_length=30, verbose_name='用途')),
                ('period', models.CharField(max_length=10, verbose_name='期間')),
                ('last_value', models.PositiveIntegerField(default=0, verbose_name='最後序號')),
            ],
            options={
                'verbose_name': '單號流水號',
                'verbose_name_plural': '單號流水號',
                'constraints': [models.UniqueConstraint(fields=('scope', 'period'), name='uniq_sequence_scope_period')],
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(blank=True, max_length=30, unique=True, verbose_name='單號')),
                ('apply_date', models.DateField(default=django.utils.timezone.localdate, verbose_name='申請日期')),
                ('reason', models.TextField(verbose_name='事由')),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14, verbose_name='總金額')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('submitted', '已送審'), ('manager_review', '主管審核中'), ('exec_review', '上層加簽'), ('finance_review', '財務審核中'), ('approved', '已核准'), ('paid', '已撥款'), ('returned', '退回修改'), ('rejected', '駁回')], default='draft', max_length=20, verbose_name='狀態')),
                ('version', models.PositiveIntegerField(default=0, verbose_name='版本')),
                ('submitted_at', models.DateTimeField(blank=True, null=True, verbose_name='送審時間')),
                ('approved_at', models.DateTimeField(blank=True, null=True, verbose_name='核准時間')),
                ('paid_at', models.DateTimeField(blank=True, null=True, verbose_name='撥款時間')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to=settings.AUTH_USER_MODEL, verbose_name='申請人')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='expenses', to='accounts.department', verbose_name='部門')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='projects.project', verbose_name='計畫')),
                ('project_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='projects.projecttype', verbose_name='計畫類型')),
            ],
            options={
                'verbose_name': '核銷單',
                'verbose_name_plural': '核銷單',
                'ordering': ['-apply_date', '-id'],
            },
        ),
        migrations.CreateModel(
            name='ApprovalLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', '建立'), ('update', '修改'), ('submit', '送審'), ('claim', '接手審核'), ('manager_approve', '主管核准'), ('exec_approve', '上層加簽核准'), ('finance_approve', '財務核准'), ('pay', '撥款'), ('return', '退回修改'), ('reject', '駁回')], max_length=30, verbose_name='動作')),
                ('from_status', models.CharField(blank=True, max_length=20, verbose_name='原狀態')),
                ('to_status', models.CharField(blank=True, max_length=20, verbose_name='新狀態')),
                ('comment', models.TextField(blank=True, verbose_name='意見')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='時間')),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_logs', to=settings.AUTH_USER_MODEL, verbose_name='操作人')),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='expenses.expense', verbose_name='核銷單')),
            ],
            options={
                'verbose_name': '簽核紀錄',
                'verbose_name_plural': '簽核紀錄',
                'ordering': ['created_at', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_type', models.CharField(choices=[('electronic', '電子發票'), ('triplicate', '三聯式'), ('duplicate', '二聯式'), ('receipt', '收據'), ('other', '其他')], default='electronic', max_length=20, verbose_name='發票類型')),
                ('invoice_no', models.CharField(blank=True, max_length=10, verbose_name='發票號碼')),
                ('issue_date', models.DateField(verbose_name='開立日期')),
                ('seller_name', models.CharField(max_length=150, verbose_name='賣方名稱')),
                ('seller_tax_id', models.CharField(blank=True, max_length=8, verbose_name='賣方統編')),
                ('buyer_tax_id', models.CharField(blank=True, max_length=8, verbose_name='買方統編')),
                ('untaxed_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14, verbose_name='未稅金額')),
                ('tax_rate', models.DecimalField(decimal_places=2, default=Decimal('5.00'), max_digits=5, verbose_name='稅率(%)')),
                ('tax_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14, verbose_name='稅額')),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=14, verbose_name='含稅總額')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='備註')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expense', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='expenses.expense', verbose_name='核銷單')),
            ],
            options={
                'verbose_name': '發票',
                'verbose_name_plural': '發票',
                'ordering': ['issue_date', 'id'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=apps.expenses.models.invoice_upload_path, verbose_name='檔案')),
                ('original_name', models.CharField(max_length=255, verbose_name='原始檔名')),
                ('content_type', models.CharField(max_length=50, verbose_name='MIME')),
                ('size', models.PositiveIntegerField(default=0, verbose_name='大小')),
                ('sha256', models.CharField(blank=True, max_length=64, verbose_name='SHA256')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='expenses.invoice', verbose_name='發票')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attachments', to=settings.AUTH_USER_MODEL, verbose_name='上傳者')),
            ],
            options={
                'verbose_name': '發票附件',
                'verbose_name_plural': '發票附件',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='品名')),
                ('spec', models.CharField(blank=True, max_length=150, verbose_name='規格')),
                ('quantity', models.DecimalField(decimal_places=2, default=Decimal('1'), max_digits=10, verbose_name='數量')),
                ('unit_price', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12, verbose_name='單價')),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0'), editable=False, max_digits=14, verbose_name='小計')),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='備註')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='排序')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='line_items', to='expenses.expensecategory', verbose_name='費用科目')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='expenses.invoice', verbose_name='發票')),
            ],
            options={
                'verbose_name': '品項',
                'verbose_name_plural': '品項',
                'ordering': ['sort_order', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='廠商名稱')),
                ('tax_id', models.CharField(blank=True, max_length=8, null=True, unique=True, verbose_name='統一編號')),
                ('contact_person', models.CharField(blank=True, max_length=80, verbose_name='聯絡人')),
                ('phone', models.CharField(blank=True, max_length=40, verbose_name='電話')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('address', models.CharField(blank=True, max_length=200, verbose_name='地址')),
                ('is_active', models.BooleanField(default=True, verbose_name='啟用')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '廠商',
                'verbose_name_plural': '廠商',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='vendor_name_idx')],
            },
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['status', 'apply_date'], name='expense_status_date_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['department', 'status'], name='expense_dept_status_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['applicant', 'status'], name='expense_applicant_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['project', 'status'], name='expense_project_idx'),
        ),
        migrations.AddIndex(
            model_name='expense',
            index=models.Index(fields=['apply_date'], name='expense_date_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['invoice_no'], name='invoice_no_idx'),
        ),
        migrations.AddIndex(
            model_name='invoice',
            index=models.Index(fields=['seller_tax_id'], name='invoice_seller_idx'),
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.UniqueConstraint(condition=models.Q(('invoice_no', ''), _negated=True), fields=('invoice_no', 'seller_tax_id'), name='uniq_invoice_no_seller_tax'),
        ),
        migrations.AddIndex(
            model_name='lineitem',
            index=models.Index(fields=['category'], name='lineitem_category_idx'),
        ),
    ]
