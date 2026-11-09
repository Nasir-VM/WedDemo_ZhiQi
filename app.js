(function () {
  'use strict';

  const STORAGE_KEY = 'zhiqi-pure-frontend-v1';
  const SESSION_KEY = 'zhiqi-pure-frontend-session';
  const THEME_KEY = 'zhiqi-theme';
  const DEMO_PASSWORD = 'Demo1234!x';
  const COMPANY = '志氣企業';
  const BUYER_TAX_ID = '04595257';

  const DEMO_ACCOUNTS = [
    {
      username: 'admin',
      password: '12345678',
      name: '系統管理員',
      role: 'admin',
      department: 'HQ',
      title: '資訊主管',
      employeeNo: 'EADM',
      email: 'admin@example.com',
      totp: true,
    },
    {
      username: 'manager',
      password: DEMO_PASSWORD,
      name: '研發主管',
      role: 'manager',
      department: 'RD',
      title: '研發部經理',
      employeeNo: 'EMAN',
      email: 'manager@example.com',
      totp: false,
    },
    {
      username: 'finance',
      password: DEMO_PASSWORD,
      name: '財務專員',
      role: 'finance',
      department: 'HQ',
      title: '財務專員',
      employeeNo: 'EFIN',
      email: 'finance@example.com',
      totp: true,
    },
    {
      username: 'employee',
      password: DEMO_PASSWORD,
      name: '研發工程師',
      role: 'employee',
      department: 'RD',
      title: '資深工程師',
      employeeNo: 'EEMP',
      email: 'employee@example.com',
      totp: false,
    },
    {
      username: 'auditor',
      password: DEMO_PASSWORD,
      name: '稽核人員',
      role: 'auditor',
      department: 'HQ',
      title: '內部稽核',
      employeeNo: 'EAUD',
      email: 'auditor@example.com',
      totp: false,
    },
  ];

  const DEPARTMENTS = [
    { code: 'HQ', name: '總管理處' },
    { code: 'RD', name: '研發部' },
    { code: 'SALES', name: '業務部' },
  ];

  const CATEGORIES = [
    { code: 'TRAVEL', name: '差旅' },
    { code: 'TRANSPORT', name: '交通' },
    { code: 'MEALS', name: '餐飲' },
    { code: 'OFFICE', name: '辦公用品' },
    { code: 'EQUIPMENT', name: '設備' },
    { code: 'TRAINING', name: '教育訓練' },
    { code: 'MARKETING', name: '廣告行銷' },
    { code: 'OTHER', name: '其他' },
  ];

  const PROJECT_TYPES = [
    { code: 'GENERAL', name: '一般營運' },
    { code: 'RD', name: '研發計畫' },
  ];

  const PROJECTS = [
    {
      code: 'PRJ-2026-001',
      name: 'AI 產品研發',
      projectType: 'RD',
      department: 'RD',
      owner: 'manager',
      startDate: '2026-01-01',
      endDate: '2026-12-31',
      budgetTotal: 1200000,
      status: 'active',
      budgetControl: 'warn',
      description: '生成式 AI 產品與內部知識庫研發計畫。',
    },
    {
      code: 'PRJ-2026-002',
      name: '年度品牌行銷',
      projectType: 'GENERAL',
      department: 'SALES',
      owner: 'manager',
      startDate: '2026-01-01',
      endDate: '2026-12-31',
      budgetTotal: 600000,
      status: 'active',
      budgetControl: 'warn',
      description: '品牌重塑、數位廣告與通路活動。',
    },
    {
      code: 'PRJ-2026-003',
      name: '智慧製造導入',
      projectType: 'RD',
      department: 'RD',
      owner: 'admin',
      startDate: '2026-03-01',
      endDate: '2027-02-28',
      budgetTotal: 900000,
      status: 'active',
      budgetControl: 'block',
      description: '產線感測器、資料收集與異常預測。',
    },
  ];

  const SELLERS = [
    { name: '志氣科技股份有限公司', taxId: '04595257' },
    { name: '台灣雲端服務股份有限公司', taxId: '10458575' },
    { name: '城市商旅股份有限公司', taxId: '22099131' },
    { name: '安心辦公用品有限公司', taxId: '53114571' },
  ];

  const STATUS_META = {
    draft: { label: '草稿', badge: 'badge-slate' },
    submitted: { label: '已送審', badge: 'badge-sky' },
    manager_review: { label: '主管審核中', badge: 'badge-amber' },
    exec_review: { label: '上層加簽', badge: 'badge-purple' },
    finance_review: { label: '財務審核中', badge: 'badge-indigo' },
    approved: { label: '已核准', badge: 'badge-emerald' },
    paid: { label: '已撥款', badge: 'badge-teal' },
    returned: { label: '退回修改', badge: 'badge-orange' },
    rejected: { label: '駁回', badge: 'badge-rose' },
  };

  const ROLE_LABELS = {
    admin: '系統管理員',
    finance: '財務',
    manager: '部門主管',
    employee: '一般員工',
    auditor: '唯讀（稽核）',
  };

  const PROJECT_STATUS_META = {
    planning: { label: '規劃中', badge: 'badge-sky' },
    active: { label: '進行中', badge: 'badge-emerald' },
    closed: { label: '結案', badge: 'badge-slate' },
  };

  const AUDIT_ACTION_LABELS = {
    create: '建立',
    update: '修改',
    delete: '刪除',
    login: '登入',
    logout: '登出',
    export: '匯出',
    backup: '備份',
    restore: '還原',
  };

  const APPROVAL_ACTION_LABELS = {
    create: '建立',
    update: '修改',
    submit: '送審',
    claim: '接手審核',
    manager_approve: '主管核准',
    exec_approve: '上層加簽核准',
    finance_approve: '財務核准',
    pay: '撥款',
    return: '退回修改',
    reject: '駁回',
  };

  const ACTION_TARGET = {
    submit: 'submitted',
    claim: 'manager_review',
    exec_approve: 'finance_review',
    finance_approve: 'approved',
    pay: 'paid',
    return: 'returned',
    reject: 'rejected',
  };

  const ACTION_LABELS = {
    submit: '送審',
    claim: '接手審核',
    manager_approve: '主管核准',
    exec_approve: '上層加簽核准',
    finance_approve: '財務核准',
    pay: '撥款',
    return: '退回修改',
    reject: '駁回',
  };

  const ICONS = {
    dashboard: `<path d='M4 13h6V4H4v9Zm0 7h6v-4H4v4Zm10 0h6v-9h-6v9Zm0-16v4h6V4h-6Z'/>`,
    expenses: `<path d='M7 3h10a2 2 0 0 1 2 2v16l-3-2-3 2-3-2-3 2V5a2 2 0 0 1 2-2Z'/><path d='M9 8h6M9 12h6M9 16h4'/>`,
    plus: `<path d='M12 5v14M5 12h14'/>`,
    projects: `<path d='M3 7h6l2 2h10v10H3V7Z'/><path d='M3 7V5h6l2 2'/>`,
    reports: `<path d='M4 20V10M10 20V4M16 20v-7M22 20H2'/>`,
    bell: `<path d='M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9'/><path d='M10 21h4'/>`,
    users: `<path d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/><circle cx='9' cy='7' r='4'/><path d='M22 21v-2a4 4 0 0 0-3-3.87'/><path d='M16 3.13a4 4 0 0 1 0 7.75'/>`,
    shield: `<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z'/><path d='m9 12 2 2 4-4'/>`,
    settings: `<circle cx='12' cy='12' r='3'/><path d='M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.7 1.7 0 0 0-1.88-.34 1.7 1.7 0 0 0-1.03 1.56V21a2 2 0 1 1-4 0v-.09A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.7 1.7 0 0 0 4.6 15a1.7 1.7 0 0 0-1.56-1.03H3a2 2 0 1 1 0-4h.09A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.34-1.88l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1.03-1.56V3a2 2 0 1 1 4 0v.09A1.7 1.7 0 0 0 15 4.6a1.7 1.7 0 0 0 1.88-.34l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.7 1.7 0 0 0 19.4 9c.13.4.43.73.82.91.3.14.63.21.96.21H21a2 2 0 1 1 0 4h-.09a1.7 1.7 0 0 0-1.51 1.03Z'/>`,
    user: `<path d='M20 21a8 8 0 0 0-16 0'/><circle cx='12' cy='7' r='4'/>`,
    menu: `<path d='M4 6h16M4 12h16M4 18h16'/>`,
    close: `<path d='M18 6 6 18M6 6l12 12'/>`,
    sun: `<circle cx='12' cy='12' r='4'/><path d='M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41'/>`,
    moon: `<path d='M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z'/>`,
    logout: `<path d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/><path d='m16 17 5-5-5-5M21 12H9'/>`,
    arrow: `<path d='M5 12h14M13 6l6 6-6 6'/>`,
    check: `<path d='m5 12 4 4L19 6'/>`,
    alert: `<path d='M12 9v4M12 17h.01'/><path d='M10.3 3.6 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z'/>`,
    search: `<circle cx='11' cy='11' r='7'/><path d='m21 21-4.3-4.3'/>`,
    download: `<path d='M12 3v12M7 10l5 5 5-5'/><path d='M5 21h14'/>`,
    refresh: `<path d='M20 7v5h-5'/><path d='M4 17v-5h5'/><path d='M6.1 9A7 7 0 0 1 19 8l1 4M4 12l1 4a7 7 0 0 0 12.9-1'/>`,
  };

  const uiState = {
    expenseFilters: {
      mode: '',
      q: '',
      status: '',
      department: '',
      project: '',
      category: '',
      applicant: '',
      dateFrom: '',
      dateTo: '',
      amountMin: '',
      amountMax: '',
    },
    projectFilters: { q: '', status: '' },
    reportFilters: {
      year: String(new Date().getFullYear()),
      quarter: '',
      month: '',
    },
    auditFilters: { q: '', action: '' },
    itemRowSeq: 1,
  };

  let state = null;
  let chartInstances = {};

  function icon(name) {
    return `<svg class='h-4 w-4 shrink-0' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>${ICONS[name] || ''}</svg>`;
  }

  function esc(value) {
    return String(value === null || value === undefined ? '' : value).replace(/[&<>\u0022\u0027]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '\u0022': '&quot;', '\u0027': '&#39;' }[char];
    });
  }

  function round2(value) {
    return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
  }

  function money(value) {
    return Number(value || 0).toLocaleString('zh-TW', { maximumFractionDigits: 0 });
  }

  function moneyExact(value) {
    return Number(value || 0).toLocaleString('zh-TW', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
  }

  function pad2(value) {
    return String(value).padStart(2, '0');
  }

  function formatDate(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return esc(value).slice(0, 10);
    return date.getFullYear() + '-' + pad2(date.getMonth() + 1) + '-' + pad2(date.getDate());
  }

  function formatDateTime(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return esc(value);
    return formatDate(date) + ' ' + pad2(date.getHours()) + ':' + pad2(date.getMinutes());
  }

  function todayISO() {
    const date = new Date();
    return date.getFullYear() + '-' + pad2(date.getMonth() + 1) + '-' + pad2(date.getDate());
  }

  function nowISO() {
    return new Date().toISOString();
  }

  function monthKey(date) {
    return date.getFullYear() + '-' + pad2(date.getMonth() + 1);
  }

  function getUser(username) {
    return state.users.find(function (user) {
      return user.username === username;
    }) || null;
  }

  function currentUser() {
    if (!state) return null;
    const username = localStorage.getItem(SESSION_KEY);
    if (!username) return null;
    return getUser(username);
  }

  function departmentName(code) {
    const department = DEPARTMENTS.find(function (item) {
      return item.code === code;
    });
    return department ? department.name : code || '—';
  }

  function categoryName(code) {
    const category = CATEGORIES.find(function (item) {
      return item.code === code;
    });
    return category ? category.name : code || '—';
  }

  function projectTypeName(code) {
    const projectType = PROJECT_TYPES.find(function (item) {
      return item.code === code;
    });
    return projectType ? projectType.name : code || '—';
  }

  function getProject(code) {
    return state.projects.find(function (project) {
      return project.code === code;
    }) || null;
  }

  function getExpense(id) {
    return state.expenses.find(function (expense) {
      return expense.id === Number(id);
    }) || null;
  }

  function statusMeta(status) {
    return STATUS_META[status] || { label: status || '—', badge: 'badge-slate' };
  }

  function projectStatusMeta(status) {
    return PROJECT_STATUS_META[status] || { label: status || '—', badge: 'badge-slate' };
  }

  function roleLabel(role) {
    return ROLE_LABELS[role] || role || '—';
  }

  function itemSubtotal(item) {
    return round2(Number(item.quantity || 0) * Number(item.unitPrice || 0));
  }

  function invoiceTotals(invoice) {
    const untaxed = round2((invoice.items || []).reduce(function (sum, item) {
      return sum + itemSubtotal(item);
    }, 0));
    const tax = round2(untaxed * Number(invoice.taxRate || 0) / 100);
    return { untaxed: untaxed, tax: tax, total: round2(untaxed + tax) };
  }

  function expenseTotal(expense) {
    return round2((expense.invoices || []).reduce(function (sum, invoice) {
      return sum + invoiceTotals(invoice).total;
    }, 0));
  }

  function invoiceCategoryTotals(invoice) {
    const totals = {};
    const baseTotal = (invoice.items || []).reduce(function (sum, item) {
      return sum + itemSubtotal(item);
    }, 0);
    const total = invoiceTotals(invoice).total;
    const factor = baseTotal ? total / baseTotal : 1;
    (invoice.items || []).forEach(function (item) {
      const code = item.categoryCode || 'OTHER';
      totals[code] = round2((totals[code] || 0) + itemSubtotal(item) * factor);
    });
    return totals;
  }

  function projectSpent(code) {
    return round2(state.expenses.reduce(function (sum, expense) {
      if (expense.projectCode !== code) return sum;
      if (expense.status !== 'approved' && expense.status !== 'paid') return sum;
      return sum + expenseTotal(expense);
    }, 0));
  }

  function projectRate(project) {
    if (!project.budgetTotal) return 0;
    return projectSpent(project.code) / project.budgetTotal * 100;
  }

  function isReadonly(user) {
    return !user || user.role === 'auditor';
  }

  function canCreateExpense(user) {
    return Boolean(user) && !isReadonly(user);
  }

  function canViewAll(user) {
    return Boolean(user) && (user.role === 'admin' || user.role === 'finance' || user.role === 'auditor');
  }

  function canManageMaster(user) {
    return Boolean(user) && (user.role === 'admin' || user.role === 'finance');
  }

  function visibleExpenses(user) {
    if (!user) return [];
    if (canViewAll(user)) return state.expenses.slice();
    if (user.role === 'manager') {
      return state.expenses.filter(function (expense) {
        return expense.department === user.department;
      });
    }
    return state.expenses.filter(function (expense) {
      return expense.applicant === user.username;
    });
  }

  function visibleProjects(user) {
    if (!user) return [];
    if (canViewAll(user)) return state.projects.slice();
    return state.projects.filter(function (project) {
      return project.department === user.department;
    });
  }

  function canViewExpense(user, expense) {
    if (!user || !expense) return false;
    if (canViewAll(user)) return true;
    if (user.role === 'manager') return expense.department === user.department;
    return expense.applicant === user.username;
  }

  function canEditExpense(user, expense) {
    if (!user || !expense || isReadonly(user)) return false;
    if (!canViewExpense(user, expense)) return false;
    if (expense.status !== 'draft' && expense.status !== 'returned') return false;
    return user.role === 'admin' || expense.applicant === user.username;
  }

  function isDepartmentManager(user, expense) {
    if (!user || !expense) return false;
    if (user.role === 'admin') return true;
    return user.role === 'manager' && user.department === expense.department;
  }

  function canAct(user, expense, action) {
    if (!user || !expense || isReadonly(user)) return false;
    const status = expense.status;
    const isApplicant = expense.applicant === user.username;
    const isManager = isDepartmentManager(user, expense);
    if (action === 'submit') return isApplicant && (status === 'draft' || status === 'returned');
    if (action === 'claim') return !isApplicant && isManager && (user.role === 'admin' || user.role === 'manager') && status === 'submitted';
    if (action === 'manager_approve') return !isApplicant && isManager && (user.role === 'admin' || user.role === 'manager') && (status === 'submitted' || status === 'manager_review');
    if (action === 'exec_approve') return !isApplicant && user.role === 'admin' && status === 'exec_review';
    if (action === 'finance_approve') return !isApplicant && (user.role === 'admin' || user.role === 'finance') && status === 'finance_review';
    if (action === 'pay') return (user.role === 'admin' || user.role === 'finance') && status === 'approved';
    if (action === 'return' || action === 'reject') {
      if (!['submitted', 'manager_review', 'exec_review', 'finance_review'].includes(status) || isApplicant) return false;
      if (user.role === 'admin' || user.role === 'finance') return true;
      return isManager && user.role === 'manager';
    }
    return false;
  }

  function reviewStatusesFor(user) {
    if (!user) return [];
    if (user.role === 'admin') return ['exec_review'];
    if (user.role === 'finance') return ['finance_review'];
    if (user.role === 'manager') return ['submitted', 'manager_review'];
    return [];
  }

  function pendingReviewCount(user) {
    const statuses = reviewStatusesFor(user);
    if (!statuses.length) return 0;
    return visibleExpenses(user).filter(function (expense) {
      return statuses.includes(expense.status) && expense.applicant !== user.username;
    }).length;
  }

  function availableActions(user, expense) {
    return ['submit', 'claim', 'manager_approve', 'exec_approve', 'finance_approve', 'pay', 'return', 'reject'].filter(function (action) {
      return canAct(user, expense, action);
    });
  }

  function unreadNotificationCount(user) {
    if (!user) return 0;
    return state.notifications.filter(function (notification) {
      return notification.to === user.username && !notification.isRead;
    }).length;
  }

  function uid(key) {
    state.counters[key] = (state.counters[key] || 0) + 1;
    return state.counters[key];
  }

  function seedExpense(config) {
    const applicant = DEMO_ACCOUNTS.find(function (account) {
      return account.username === config.applicant;
    });
    const project = PROJECTS.find(function (item) {
      return item.code === config.project;
    });
    const seller = SELLERS[config.id % SELLERS.length];
    const invoiceId = config.id * 10 + 1;
    const base = round2(config.total / 1.05);
    const createdAt = config.date + 'T09:00:00+08:00';
    const submittedAt = config.date + 'T10:00:00+08:00';
    let hour = 11;
    const logs = [{
      id: config.id * 100 + 1,
      actor: config.applicant,
      action: 'create',
      fromStatus: '',
      toStatus: 'draft',
      comment: '建立核銷單',
      createdAt: createdAt,
    }];
    function pushLog(action, fromStatus, toStatus, actor, comment) {
      logs.push({
        id: config.id * 100 + logs.length + 1,
        actor: actor,
        action: action,
        fromStatus: fromStatus,
        toStatus: toStatus,
        comment: comment,
        createdAt: config.date + 'T' + pad2(hour) + ':00:00+08:00',
      });
      hour += 1;
    }
    if (config.status !== 'draft') pushLog('submit', 'draft', 'submitted', config.applicant, '送出核銷單');
    if (config.status === 'manager_review') pushLog('claim', 'submitted', 'manager_review', 'manager', '主管接手審核');
    if (['exec_review', 'finance_review', 'approved', 'paid'].includes(config.status)) {
      const target = config.total > 50000 ? 'exec_review' : 'finance_review';
      pushLog('manager_approve', 'submitted', target, 'manager', '主管核准');
    }
    if (['finance_review', 'approved', 'paid'].includes(config.status) && config.total > 50000) {
      pushLog('exec_approve', 'exec_review', 'finance_review', 'admin', '上層加簽核准');
    }
    if (config.status === 'approved' || config.status === 'paid') {
      pushLog('finance_approve', 'finance_review', 'approved', 'finance', '財務核准');
    }
    if (config.status === 'paid') pushLog('pay', 'approved', 'paid', 'finance', '完成撥款');
    if (config.status === 'returned') pushLog('return', 'manager_review', 'returned', 'manager', '請補上發票明細');
    if (config.status === 'rejected') pushLog('reject', 'manager_review', 'rejected', 'manager', '不符合核銷規定');
    const invoice = {
      id: invoiceId,
      invoiceType: 'electronic',
      invoiceNo: 'AB' + String(20260000 + config.id).slice(-8),
      issueDate: config.date,
      sellerName: seller.name,
      sellerTaxId: seller.taxId,
      buyerTaxId: BUYER_TAX_ID,
      taxRate: 5,
      note: '',
      items: [{
        id: invoiceId * 10 + 1,
        name: config.itemName || config.reason,
        spec: '',
        quantity: 1,
        unitPrice: base,
        categoryCode: config.category,
        note: '',
      }],
    };
    return {
      id: config.id,
      number: 'EX-2026-' + String(config.id).padStart(4, '0'),
      applicant: config.applicant,
      department: applicant.department,
      projectCode: project.code,
      projectTypeCode: project.projectType,
      applyDate: config.date,
      reason: config.reason,
      status: config.status,
      version: logs.length,
      submittedAt: config.status === 'draft' ? null : submittedAt,
      approvedAt: config.status === 'approved' || config.status === 'paid' ? config.date + 'T14:00:00+08:00' : null,
      paidAt: config.status === 'paid' ? config.date + 'T16:00:00+08:00' : null,
      createdAt: createdAt,
      updatedAt: logs[logs.length - 1].createdAt,
      invoices: [invoice],
      logs: logs,
    };
  }

  function seedExpenses() {
    return [
      { id: 1, applicant: 'employee', project: 'PRJ-2026-001', category: 'MEALS', reason: '客戶拜訪餐費', date: '2026-01-12', status: 'paid', total: 4800 },
      { id: 2, applicant: 'employee', project: 'PRJ-2026-001', category: 'TRANSPORT', reason: '高鐵出差交通', date: '2026-02-08', status: 'approved', total: 2600 },
      { id: 3, applicant: 'employee', project: 'PRJ-2026-001', category: 'EQUIPMENT', reason: '開發用螢幕', date: '2026-03-19', status: 'finance_review', total: 32000 },
      { id: 4, applicant: 'employee', project: 'PRJ-2026-002', category: 'MARKETING', reason: '社群廣告投放', date: '2026-04-05', status: 'exec_review', total: 68000 },
      { id: 5, applicant: 'manager', project: 'PRJ-2026-002', category: 'TRAVEL', reason: '南部客戶出差住宿', date: '2026-05-16', status: 'manager_review', total: 12000 },
      { id: 6, applicant: 'manager', project: 'PRJ-2026-001', category: 'TRAINING', reason: 'AI 技術研討會', date: '2026-06-22', status: 'submitted', total: 8000 },
      { id: 7, applicant: 'employee', project: 'PRJ-2026-001', category: 'OFFICE', reason: '實驗室文具用品', date: '2026-07-03', status: 'draft', total: 1200 },
      { id: 8, applicant: 'employee', project: 'PRJ-2026-002', category: 'OTHER', reason: '臨時雜項支出', date: '2026-08-14', status: 'returned', total: 3400 },
      { id: 9, applicant: 'employee', project: 'PRJ-2026-001', category: 'MEALS', reason: '團隊會議餐盒', date: '2026-09-09', status: 'rejected', total: 2100 },
      { id: 10, applicant: 'manager', project: 'PRJ-2026-001', category: 'EQUIPMENT', reason: '測試設備採購', date: '2026-10-21', status: 'paid', total: 56000 },
      { id: 11, applicant: 'employee', project: 'PRJ-2026-001', category: 'TRAVEL', reason: '日本出差機票', date: '2026-11-02', status: 'submitted', total: 48000 },
      { id: 12, applicant: 'finance', project: 'PRJ-2026-002', category: 'MARKETING', reason: '年度品牌廣告', date: '2026-11-06', status: 'finance_review', total: 95000 },
      { id: 13, applicant: 'employee', project: 'PRJ-2026-003', category: 'EQUIPMENT', reason: '智慧製造感測器', date: '2026-11-08', status: 'manager_review', total: 128000 },
    ].map(seedExpense);
  }

  function seedNotifications() {
    return [
      { id: 1, to: 'manager', title: '新的核銷單待審核', message: '研發工程師 送審 EX-2026-0011，金額 48,000 元。', level: 'warning', createdAt: '2026-11-02T10:05:00+08:00', isRead: false, expenseId: 11 },
      { id: 2, to: 'finance', title: '核銷單待財務審核', message: 'EX-2026-0012 已由上層加簽核准，進入財務審核。', level: 'info', createdAt: '2026-11-06T11:20:00+08:00', isRead: false, expenseId: 12 },
      { id: 3, to: 'admin', title: '核銷單待上層加簽', message: 'EX-2026-0004 金額超過 50,000 元，需要上層加簽。', level: 'warning', createdAt: '2026-11-04T15:10:00+08:00', isRead: false, expenseId: 4 },
      { id: 4, to: 'employee', title: '核銷單已撥款', message: 'EX-2026-0001 已完成撥款。', level: 'success', createdAt: '2026-01-15T16:00:00+08:00', isRead: true, expenseId: 1 },
      { id: 5, to: 'employee', title: '核銷單被退回修改', message: 'EX-2026-0008：請補上發票明細。', level: 'danger', createdAt: '2026-08-15T09:30:00+08:00', isRead: false, expenseId: 8 },
      { id: 6, to: 'employee', title: '核銷單被駁回', message: 'EX-2026-0009：不符合核銷規定。', level: 'danger', createdAt: '2026-09-10T10:00:00+08:00', isRead: false, expenseId: 9 },
      { id: 7, to: 'auditor', title: '稽核通知', message: '本示範版提供唯讀稽核視角。', level: 'info', createdAt: '2026-11-01T08:00:00+08:00', isRead: false, expenseId: null },
      { id: 8, to: 'manager', title: '核銷單已撥款', message: 'EX-2026-0010 已完成撥款。', level: 'success', createdAt: '2026-10-25T16:00:00+08:00', isRead: true, expenseId: 10 },
    ];
  }

  function seedAuditLogs() {
    return [
      { id: 1, createdAt: '2026-11-08T09:12:00+08:00', username: 'employee', action: 'login', modelLabel: 'accounts.User', objectRepr: 'employee', ip: '127.0.0.1', changes: '' },
      { id: 2, createdAt: '2026-11-08T09:15:00+08:00', username: 'employee', action: 'create', modelLabel: 'expenses.Expense', objectRepr: 'EX-2026-0013', ip: '127.0.0.1', changes: 'status: draft' },
      { id: 3, createdAt: '2026-11-08T09:20:00+08:00', username: 'employee', action: 'update', modelLabel: 'expenses.Expense', objectRepr: 'EX-2026-0013', ip: '127.0.0.1', changes: 'status: draft -> submitted' },
      { id: 4, createdAt: '2026-11-08T10:05:00+08:00', username: 'manager', action: 'login', modelLabel: 'accounts.User', objectRepr: 'manager', ip: '127.0.0.1', changes: '' },
      { id: 5, createdAt: '2026-11-08T10:12:00+08:00', username: 'manager', action: 'update', modelLabel: 'expenses.Expense', objectRepr: 'EX-2026-0013', ip: '127.0.0.1', changes: 'status: submitted -> manager_review' },
      { id: 6, createdAt: '2026-11-08T14:30:00+08:00', username: 'finance', action: 'export', modelLabel: 'expenses.Expense', objectRepr: '年度費用報表', ip: '127.0.0.1', changes: 'format: csv' },
      { id: 7, createdAt: '2026-11-09T08:40:00+08:00', username: 'admin', action: 'backup', modelLabel: 'core.SystemSetting', objectRepr: 'db.sqlite3', ip: '127.0.0.1', changes: 'destination: backup/' },
      { id: 8, createdAt: '2026-11-09T09:00:00+08:00', username: 'auditor', action: 'login', modelLabel: 'accounts.User', objectRepr: 'auditor', ip: '127.0.0.1', changes: '' },
    ];
  }

  function seedState() {
    const users = DEMO_ACCOUNTS.map(function (account) {
      return {
        username: account.username,
        name: account.name,
        role: account.role,
        department: account.department,
        title: account.title,
        employeeNo: account.employeeNo,
        email: account.email,
        active: true,
        totp: account.totp,
      };
    });
    return {
      version: 1,
      settings: {
        companyName: COMPANY,
        announcement: '歡迎使用純前端示範版。所有資料僅存在瀏覽器 localStorage，重新整理不會遺失。',
        approvalThreshold: 50000,
        defaultTaxRate: 5,
        dashboardCacheSeconds: 60,
        backupRetention: 14,
      },
      departments: DEPARTMENTS.map(function (item) { return { code: item.code, name: item.name }; }),
      categories: CATEGORIES.map(function (item) { return { code: item.code, name: item.name }; }),
      projectTypes: PROJECT_TYPES.map(function (item) { return { code: item.code, name: item.name }; }),
      projects: PROJECTS.map(function (project) { return Object.assign({}, project); }),
      users: users,
      expenses: seedExpenses(),
      notifications: seedNotifications(),
      auditLogs: seedAuditLogs(),
      counters: { expense: 20, invoice: 300, log: 5000, notification: 100, audit: 100 },
    };
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.version === 1 && Array.isArray(parsed.expenses) && Array.isArray(parsed.users)) {
          return parsed;
        }
      }
    } catch (error) {
      console.warn('無法讀取示範資料，將重新建立。', error);
    }
    const fresh = seedState();
    saveStateObject(fresh);
    return fresh;
  }

  function saveStateObject(value) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    } catch (error) {
      console.warn('無法儲存示範資料。', error);
    }
  }

  function saveState() {
    saveStateObject(state);
  }

  function addAudit(action, modelLabel, objectRepr, changes, username) {
    const user = currentUser();
    state.auditLogs.unshift({
      id: uid('audit'),
      createdAt: nowISO(),
      username: username || (user ? user.username : 'system'),
      action: action,
      modelLabel: modelLabel || '—',
      objectRepr: objectRepr || '—',
      ip: '127.0.0.1',
      changes: changes || '',
    });
    if (state.auditLogs.length > 500) state.auditLogs.length = 500;
  }

  function addNotification(to, title, message, level, expenseId) {
    state.notifications.unshift({
      id: uid('notification'),
      to: to,
      title: title,
      message: message,
      level: level || 'info',
      createdAt: nowISO(),
      isRead: false,
      expenseId: expenseId || null,
    });
  }

  function addApprovalLog(expense, action, fromStatus, toStatus, comment, actor) {
    expense.logs.push({
      id: uid('log'),
      actor: actor,
      action: action,
      fromStatus: fromStatus,
      toStatus: toStatus,
      comment: comment || '',
      createdAt: nowISO(),
    });
  }

  function notifyAfterAction(expense, action, actor, comment, target) {
    const label = expense.number;
    if (action === 'submit') {
      state.users.filter(function (user) {
        return user.role === 'manager' && user.department === expense.department && user.username !== actor.username;
      }).forEach(function (user) {
        addNotification(user.username, '新的核銷單待審核', actor.name + ' 送審 ' + label + '，金額 ' + money(expenseTotal(expense)) + ' 元。', 'warning', expense.id);
      });
    } else if (action === 'manager_approve') {
      const recipients = target === 'exec_review'
        ? state.users.filter(function (user) { return user.role === 'admin'; })
        : state.users.filter(function (user) { return user.role === 'finance'; });
      recipients.forEach(function (user) {
        addNotification(user.username, '核銷單待下一關審核', label + ' 已由 ' + actor.name + ' 核准，進入下一關卡。', 'info', expense.id);
      });
    } else if (action === 'exec_approve') {
      state.users.filter(function (user) { return user.role === 'finance'; }).forEach(function (user) {
        addNotification(user.username, '核銷單待財務審核', label + ' 已由上層加簽核准。', 'info', expense.id);
      });
    } else if (action === 'finance_approve') {
      addNotification(expense.applicant, '核銷單已核准', label + ' 已由財務核准。', 'success', expense.id);
    } else if (action === 'pay') {
      addNotification(expense.applicant, '核銷單已撥款', label + ' 已完成撥款。', 'success', expense.id);
    } else if (action === 'return') {
      addNotification(expense.applicant, '核銷單被退回修改', label + '：' + comment, 'danger', expense.id);
    } else if (action === 'reject') {
      addNotification(expense.applicant, '核銷單被駁回', label + '：' + comment, 'danger', expense.id);
    }
  }

  function filteredExpenses() {
    const filters = uiState.expenseFilters;
    const user = currentUser();
    const reviewStatuses = reviewStatusesFor(user);
    return visibleExpenses(user).filter(function (expense) {
      if (filters.mode === 'review') {
        if (!reviewStatuses.includes(expense.status)) return false;
        if (expense.applicant === user.username) return false;
      }
      if (filters.q) {
        const haystack = [expense.number, expense.reason, expense.applicant, departmentName(expense.department), expense.projectCode].join(' ').toLowerCase();
        if (!haystack.includes(filters.q.toLowerCase())) return false;
      }
      if (filters.status && expense.status !== filters.status) return false;
      if (filters.department && expense.department !== filters.department) return false;
      if (filters.project && expense.projectCode !== filters.project) return false;
      if (filters.category) {
        const hasCategory = expense.invoices.some(function (invoice) {
          return invoice.items.some(function (item) { return item.categoryCode === filters.category; });
        });
        if (!hasCategory) return false;
      }
      if (filters.applicant && expense.applicant !== filters.applicant) return false;
      if (filters.dateFrom && expense.applyDate < filters.dateFrom) return false;
      if (filters.dateTo && expense.applyDate > filters.dateTo) return false;
      const total = expenseTotal(expense);
      if (filters.amountMin !== '' && total < Number(filters.amountMin)) return false;
      if (filters.amountMax !== '' && total > Number(filters.amountMax)) return false;
      return true;
    }).sort(function (a, b) {
      return b.applyDate.localeCompare(a.applyDate) || b.id - a.id;
    });
  }

  function filteredProjects() {
    const filters = uiState.projectFilters;
    return visibleProjects(currentUser()).filter(function (project) {
      if (filters.q) {
        const haystack = (project.code + ' ' + project.name).toLowerCase();
        if (!haystack.includes(filters.q.toLowerCase())) return false;
      }
      if (filters.status && project.status !== filters.status) return false;
      return true;
    }).sort(function (a, b) {
      return a.code.localeCompare(b.code);
    });
  }

  function filteredAuditLogs() {
    const filters = uiState.auditFilters;
    return state.auditLogs.filter(function (log) {
      if (filters.q) {
        const haystack = [log.username, log.modelLabel, log.objectRepr, log.ip].join(' ').toLowerCase();
        if (!haystack.includes(filters.q.toLowerCase())) return false;
      }
      if (filters.action && log.action !== filters.action) return false;
      return true;
    }).slice().sort(function (a, b) {
      return b.createdAt.localeCompare(a.createdAt);
    });
  }

  function reportPeriodExpenses() {
    const filters = uiState.reportFilters;
    const year = Number(filters.year);
    return visibleExpenses(currentUser()).filter(function (expense) {
      if (expense.status !== 'approved' && expense.status !== 'paid') return false;
      if (!expense.applyDate.startsWith(String(year))) return false;
      const month = Number(expense.applyDate.slice(5, 7));
      if (filters.quarter && Math.ceil(month / 3) !== Number(filters.quarter)) return false;
      if (filters.month && month !== Number(filters.month)) return false;
      return true;
    });
  }

  function groupSum(rows, keyFn, valueFn) {
    const map = {};
    rows.forEach(function (row) {
      const key = keyFn(row);
      map[key] = (map[key] || 0) + valueFn(row);
    });
    return map;
  }

  function categoryTotals(expenses) {
    const totals = {};
    expenses.forEach(function (expense) {
      expense.invoices.forEach(function (invoice) {
        const parts = invoiceCategoryTotals(invoice);
        Object.keys(parts).forEach(function (code) {
          totals[code] = round2((totals[code] || 0) + parts[code]);
        });
      });
    });
    return totals;
  }

  function monthSeries(expenses, year) {
    const labels = [];
    const values = [];
    for (let month = 1; month <= 12; month += 1) {
      const key = year + '-' + pad2(month);
      labels.push(month + ' 月');
      values.push(round2(expenses.filter(function (expense) {
        return expense.applyDate.startsWith(key);
      }).reduce(function (sum, expense) {
        return sum + expenseTotal(expense);
      }, 0)));
    }
    return { labels: labels, values: values };
  }

  function navigate(path) {
    const next = '#/' + String(path || 'dashboard').replace(/^#?\/?/, '');
    if (location.hash === next) {
      render();
    } else {
      location.hash = next;
    }
  }

  function getRoute() {
    const raw = (location.hash || '').replace(/^#\/?/, '');
    const queryIndex = raw.indexOf('?');
    const pathPart = queryIndex >= 0 ? raw.slice(0, queryIndex) : raw;
    const queryPart = queryIndex >= 0 ? raw.slice(queryIndex + 1) : '';
    const parts = pathPart.split('/').filter(Boolean);
    const query = {};
    if (queryPart) {
      queryPart.split('&').forEach(function (pair) {
        const bits = pair.split('=');
        query[decodeURIComponent(bits[0] || '')] = decodeURIComponent(bits.slice(1).join('=') || '');
      });
    }
    if (!parts.length) return { name: 'dashboard', query: query };
    const name = parts[0];
    if (name === 'expenses') {
      if (parts[1] === 'new') return { name: 'expense-new', query: query };
      if (parts[1] === 'edit') return { name: 'expense-edit', id: Number(parts[2]), query: query };
      if (parts[1]) return { name: 'expense-detail', id: Number(parts[1]), query: query };
      return { name: 'expenses', query: query };
    }
    if (name === 'projects' && parts[1]) return { name: 'project-detail', code: decodeURIComponent(parts[1]), query: query };
    return { name: name, query: query };
  }

  function navItems(user) {
    const items = [
      { name: 'dashboard', href: '#/dashboard', label: '儀表板', icon: 'dashboard' },
      { name: 'expenses', href: '#/expenses', label: '核銷單', icon: 'expenses' },
    ];
    if (canCreateExpense(user)) items.push({ name: 'expense-new', href: '#/expenses/new', label: '新增核銷', icon: 'plus' });
    items.push({ name: 'projects', href: '#/projects', label: '專案', icon: 'projects' });
    items.push({ name: 'reports', href: '#/reports', label: '報表', icon: 'reports' });
    if (reviewStatusesFor(user).length) {
      items.push({ name: 'review', href: '#/expenses?review=1', label: '待我審核', icon: 'check', badge: pendingReviewCount(user) });
    }
    items.push({ name: 'notifications', href: '#/notifications', label: '通知', icon: 'bell', badge: unreadNotificationCount(user) });
    if (canManageMaster(user)) items.push({ name: 'master', href: '#/master', label: '基礎資料', icon: 'settings' });
    if (user && user.role === 'admin') items.push({ name: 'users', href: '#/users', label: '使用者', icon: 'users' });
    if (user && (user.role === 'admin' || user.role === 'auditor')) items.push({ name: 'audit', href: '#/audit', label: '稽核', icon: 'shield' });
    if (user && user.role === 'admin') items.push({ name: 'settings', href: '#/settings', label: '系統設定', icon: 'settings' });
    return items;
  }

  function isNavActive(item, route) {
    if (item.name === 'review') return route.name === 'expenses' && route.query.review === '1';
    if (item.name === 'expenses') return ['expenses', 'expense-detail', 'expense-edit'].includes(route.name) && route.query.review !== '1';
    if (item.name === 'expense-new') return route.name === 'expense-new';
    if (item.name === 'projects') return ['projects', 'project-detail'].includes(route.name);
    return route.name === item.name;
  }

  function navLink(item, route) {
    const active = isNavActive(item, route);
    const badge = item.badge ? `<span class='ml-auto rounded-full bg-rose-100 px-2 py-0.5 text-[11px] font-semibold text-rose-700 dark:bg-rose-900/50 dark:text-rose-200'>${item.badge}</span>` : '';
    return `<a href='${item.href}' class='demo-sidebar-link ${active ? 'active' : ''}' ${active ? 'aria-current=page' : ''}>${icon(item.icon)}<span>${esc(item.label)}</span>${badge}</a>`;
  }

  function routeSubtitle(name) {
    const subtitles = {
      dashboard: '掌握核銷進度、預算與待辦事項',
      expenses: '查詢、篩選與管理核銷單',
      'expense-new': '建立新的費用核銷單',
      'expense-detail': '檢視核銷內容、審核歷程與可執行動作',
      'expense-edit': '修改草稿或退回的核銷單',
      projects: '檢視專案預算與執行率',
      'project-detail': '專案基本資料與核銷明細',
      reports: '年度、季度與月度費用分析',
      notifications: '查看與管理系統通知',
      users: '示範帳號與角色權限',
      audit: '操作稽核軌跡',
      settings: '示範版系統參數',
      profile: '個人帳號與角色資訊',
      master: '部門、類別與專案類型',
    };
    return subtitles[name] || '志氣企業核銷系統';
  }

  function render() {
    if (!state) return;
    const user = currentUser();
    const route = getRoute();
    if (!user) {
      renderLogin();
      updateThemeLabels();
      return;
    }
    if (route.name === 'login') {
      navigate('dashboard');
      return;
    }
    let title = '儀表板';
    let content = '';
    if (route.name === 'dashboard') {
      title = '儀表板';
      content = renderDashboard();
    } else if (route.name === 'expenses') {
      title = '核銷單';
      content = renderExpenses(route);
    } else if (route.name === 'expense-new') {
      title = '新增核銷';
      content = renderExpenseForm(null);
    } else if (route.name === 'expense-detail') {
      title = '核銷單詳情';
      content = renderExpenseDetail(route.id);
    } else if (route.name === 'expense-edit') {
      title = '編輯核銷';
      content = renderExpenseForm(route.id);
    } else if (route.name === 'projects') {
      title = '專案';
      content = renderProjects();
    } else if (route.name === 'project-detail') {
      title = '專案詳情';
      content = renderProjectDetail(route.code);
    } else if (route.name === 'reports') {
      title = '報表';
      content = renderReports();
    } else if (route.name === 'notifications') {
      title = '通知';
      content = renderNotifications();
    } else if (route.name === 'users') {
      title = '使用者';
      content = renderUsers();
    } else if (route.name === 'audit') {
      title = '稽核';
      content = renderAudit();
    } else if (route.name === 'settings') {
      title = '系統設定';
      content = renderSettings();
    } else if (route.name === 'profile') {
      title = '個人資料';
      content = renderProfile();
    } else if (route.name === 'master') {
      title = '基礎資料';
      content = renderMaster();
    } else {
      title = '找不到頁面';
      content = renderNotFound();
    }
    renderShell(route, title, content);
    updateThemeLabels();
    if (route.name === 'dashboard') window.requestAnimationFrame(drawDashboardCharts);
    if (route.name === 'reports') window.requestAnimationFrame(drawReportCharts);
    if (route.name === 'expense-new' || route.name === 'expense-edit') window.requestAnimationFrame(recalcExpenseForm);
  }

  function renderLogin() {
    document.body.classList.remove('demo-sidebar-open');
    const accounts = DEMO_ACCOUNTS.map(function (account) {
      return `<button type='button' class='flex w-full items-center justify-between gap-3 rounded-xl border border-slate-700 bg-slate-800/70 px-3 py-2 text-left text-sm text-slate-100 transition-colors hover:border-brand-400' data-action='fill-login' data-username='${esc(account.username)}' data-password='${esc(account.password)}'><span><span class='font-semibold'>${esc(account.name)}</span><span class='ml-2 text-xs text-slate-400'>${esc(roleLabel(account.role))}</span></span><span class='text-xs text-slate-400'>${esc(account.username)}</span></button>`;
    }).join('');
    document.getElementById('app').innerHTML = `<div class='min-h-screen bg-slate-100 dark:bg-slate-950'><div class='mx-auto grid min-h-screen max-w-6xl lg:grid-cols-2'><section class='demo-login-panel flex flex-col justify-between p-8 sm:p-12'><div><div class='flex items-center gap-3'><span class='flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-500 text-lg font-bold text-white'>志</span><div><p class='text-sm font-semibold tracking-wide'>志氣企業</p><p class='text-xs text-slate-400'>EXPENSE MANAGEMENT</p></div></div><h1 class='mt-10 text-3xl font-bold tracking-tight sm:text-4xl'>核銷管理，<br>從這裡開始。</h1><p class='demo-login-muted mt-4 max-w-md text-sm leading-6'>純前端示範版使用硬編碼帳號與瀏覽器 localStorage。無需後端、無需資料庫，所有操作都在本機完成。</p><div class='mt-8 space-y-2'>${accounts}</div></div><div class='demo-login-rule mt-10 border-t pt-5 text-xs text-slate-400'><p>示範密碼：管理員 <span class='font-mono text-slate-200'>12345678</span>，其餘帳號 <span class='font-mono text-slate-200'>Demo1234!x</span></p><p class='mt-2'>資料僅存於此瀏覽器，重新整理後仍會保留。</p></div></section><section class='flex items-center justify-center bg-white p-8 dark:bg-slate-900 sm:p-12'><div class='w-full max-w-md'><div class='mb-8'><p class='text-xs font-semibold uppercase tracking-[0.2em] text-brand-600 dark:text-brand-300'>Welcome back</p><h2 class='mt-2 text-2xl font-bold tracking-tight'>登入示範系統</h2><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>選擇左側示範帳號，或直接輸入帳號密碼。</p></div><form id='login-form' class='space-y-4'><div class='form-row'><label class='form-label' for='login-username'>帳號</label><input class='input' id='login-username' name='username' autocomplete='username' placeholder='例如 admin' required></div><div class='form-row'><label class='form-label' for='login-password'>密碼</label><input class='input' id='login-password' name='password' type='password' autocomplete='current-password' placeholder='請輸入密碼' required></div><button class='btn-primary w-full' type='submit'>登入</button></form><div class='mt-4 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400'><button type='button' class='hover:text-brand-600 dark:hover:text-brand-300' data-action='reset-demo'>重設示範資料</button><button type='button' class='hover:text-brand-600 dark:hover:text-brand-300' data-action='toggle-theme'><span data-theme-label>深色模式</span></button></div><p class='mt-8 text-center text-xs text-slate-400'>此為展示用途，請勿輸入真實個資。</p></div></section></div></div>`;
  }

  function renderShell(route, title, content) {
    const user = currentUser();
    const unread = unreadNotificationCount(user);
    const links = navItems(user).map(function (item) {
      return navLink(item, route);
    }).join('');
    const subtitle = routeSubtitle(route.name);
    document.body.classList.remove('demo-sidebar-open');
    document.getElementById('app').innerHTML = `<div class='demo-shell'><button type='button' class='demo-backdrop' data-action='close-sidebar' aria-label='關閉選單'></button><aside class='demo-sidebar border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900'><div class='demo-sidebar-panel flex flex-col p-4'><a class='flex items-center gap-3 rounded-xl px-2 py-2' href='#/dashboard'><span class='flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-600 text-sm font-bold text-white'>志</span><span><span class='block text-sm font-bold tracking-tight'>志氣企業</span><span class='block text-[11px] uppercase tracking-[0.18em] text-slate-400'>Expense demo</span></span></a><nav class='mt-6 space-y-1' aria-label='主要導覽'>${links}</nav><div class='mt-auto border-t border-slate-200 pt-4 dark:border-slate-800'><a class='flex items-center gap-3 rounded-xl px-2 py-2 hover:bg-slate-100 dark:hover:bg-slate-800' href='#/profile'><span class='flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700 dark:bg-brand-900/50 dark:text-brand-200'>${esc(user.name.slice(0, 1))}</span><span class='min-w-0 flex-1'><span class='block truncate text-sm font-medium'>${esc(user.name)}</span><span class='block truncate text-xs text-slate-500 dark:text-slate-400'>${esc(roleLabel(user.role))} · ${esc(departmentName(user.department))}</span></span></a><button type='button' class='mt-2 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-sm text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white' data-action='logout'>${icon('logout')}登出</button></div></div></aside><div class='demo-main'><header class='sticky top-0 z-30 border-b border-slate-200 bg-white/85 backdrop-blur dark:border-slate-800 dark:bg-slate-900/85'><div class='flex h-16 items-center gap-3 px-4 sm:px-6'><button type='button' class='btn-ghost btn-sm lg:hidden' data-action='toggle-sidebar' aria-label='開啟選單'>${icon('menu')}</button><div class='min-w-0 flex-1'><p class='truncate text-sm font-semibold'>${esc(title)}</p><p class='truncate text-xs text-slate-500 dark:text-slate-400'>${esc(subtitle)}</p></div><button type='button' class='btn-ghost btn-sm' data-action='toggle-theme'>${icon('sun')}<span class='hidden sm:inline' data-theme-label>深色模式</span></button><a class='relative btn-ghost btn-sm' href='#/notifications' aria-label='通知'>${icon('bell')}${unread ? `<span class='absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-600 px-1 text-[10px] font-bold text-white'>${unread}</span>` : ''}</a><a class='flex items-center gap-2 rounded-lg px-2 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800' href='#/profile'><span class='flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700 dark:bg-brand-900/50 dark:text-brand-200'>${esc(user.name.slice(0, 1))}</span><span class='hidden text-left sm:block'><span class='block text-sm font-medium'>${esc(user.name)}</span><span class='block text-xs text-slate-500 dark:text-slate-400'>${esc(roleLabel(user.role))}</span></span></a></div></header><main id='main' class='px-4 py-6 sm:px-6 lg:px-8'><div class='demo-view mx-auto max-w-7xl'>${content}</div></main></div></div>`;
  }

  function pageHeader(title, subtitle, actions) {
    return `<div class='mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between'><div><h1 class='text-2xl font-bold tracking-tight'>${esc(title)}</h1><p class='mt-1 text-sm text-slate-500 dark:text-slate-400'>${esc(subtitle)}</p></div>${actions ? `<div class='flex flex-wrap gap-2'>${actions}</div>` : ''}</div>`;
  }

  function statCard(label, value, hint, tone) {
    const tones = {
      brand: 'text-brand-600 dark:text-brand-300',
      emerald: 'text-emerald-600 dark:text-emerald-300',
      amber: 'text-amber-600 dark:text-amber-300',
      rose: 'text-rose-600 dark:text-rose-300',
    };
    return `<div class='card'><p class='card-title'>${esc(label)}</p><p class='kpi-value ${tones[tone] || ''}'>${value}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${hint}</p></div>`;
  }

  function statusBadge(status) {
    const meta = statusMeta(status);
    return `<span class='${meta.badge}'>${esc(meta.label)}</span>`;
  }

  function expenseRow(expense) {
    const applicant = getUser(expense.applicant);
    const project = getProject(expense.projectCode);
    return `<tr><td><a class='font-medium text-brand-700 hover:underline dark:text-brand-300' href='#/expenses/${expense.id}'>${esc(expense.number)}</a></td><td><span class='block'>${esc(applicant ? applicant.name : expense.applicant)}</span><span class='block text-xs text-slate-500 dark:text-slate-400'>${esc(departmentName(expense.department))}</span></td><td><span class='block'>${esc(project ? project.name : expense.projectCode)}</span><span class='block text-xs text-slate-500 dark:text-slate-400'>${esc(expense.projectCode)}</span></td><td class='demo-amount font-medium'>NT$ ${money(expenseTotal(expense))}</td><td>${statusBadge(expense.status)}</td><td class='text-slate-500 dark:text-slate-400'>${esc(formatDate(expense.applyDate))}</td><td class='text-right'><a class='btn-ghost btn-sm' href='#/expenses/${expense.id}' aria-label='檢視 ${esc(expense.number)}'>${icon('arrow')}</a></td></tr>`;
  }

  function expenseTable(rows) {
    if (!rows.length) {
      return `<div class='rounded-2xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400'>沒有符合條件的核銷單。</div>`;
    }
    return `<div class='table-wrap'><table class='table'><thead><tr><th>單號</th><th>申請人</th><th>專案</th><th>金額</th><th>狀態</th><th>申請日</th><th class='text-right'>操作</th></tr></thead><tbody>${rows.map(expenseRow).join('')}</tbody></table></div>`;
  }

  function dashboardData() {
    const user = currentUser();
    const now = new Date();
    const currentMonth = monthKey(now);
    const currentYear = String(now.getFullYear());
    const expenses = visibleExpenses(user);
    const approved = expenses.filter(function (expense) {
      return expense.status === 'approved' || expense.status === 'paid';
    });
    const monthTotal = round2(approved.filter(function (expense) {
      return expense.applyDate.startsWith(currentMonth);
    }).reduce(function (sum, expense) {
      return sum + expenseTotal(expense);
    }, 0));
    const yearTotal = round2(approved.filter(function (expense) {
      return expense.applyDate.startsWith(currentYear);
    }).reduce(function (sum, expense) {
      return sum + expenseTotal(expense);
    }, 0));
    const approvedUnpaid = round2(expenses.filter(function (expense) {
      return expense.status === 'approved';
    }).reduce(function (sum, expense) {
      return sum + expenseTotal(expense);
    }, 0));
    const inReview = expenses.filter(function (expense) {
      return ['submitted', 'manager_review', 'exec_review', 'finance_review'].includes(expense.status);
    }).length;
    const pending = pendingReviewCount(user);
    const projects = visibleProjects(user);
    const budgetTotal = round2(projects.reduce(function (sum, project) {
      return sum + Number(project.budgetTotal || 0);
    }, 0));
    const spentTotal = round2(projects.reduce(function (sum, project) {
      return sum + projectSpent(project.code);
    }, 0));
    const budgetRate = budgetTotal ? spentTotal / budgetTotal * 100 : 0;
    const trend = monthSeries(approved.filter(function (expense) {
      return expense.applyDate.startsWith(currentYear);
    }), currentYear);
    const deptTotals = groupSum(approved, function (expense) { return expense.department; }, expenseTotal);
    const deptShare = Object.keys(deptTotals).map(function (code) {
      return { label: departmentName(code), value: round2(deptTotals[code]) };
    }).sort(function (a, b) { return b.value - a.value; });
    const catTotals = categoryTotals(approved);
    const categoryShare = CATEGORIES.map(function (category) {
      return { label: category.name, value: round2(catTotals[category.code] || 0) };
    }).filter(function (item) {
      return item.value > 0;
    }).sort(function (a, b) { return b.value - a.value; });
    const projectBars = projects.map(function (project) {
      return {
        code: project.code,
        name: project.name,
        budget: Number(project.budgetTotal || 0),
        spent: projectSpent(project.code),
        rate: projectRate(project),
      };
    }).sort(function (a, b) { return b.rate - a.rate; });
    const warnings = projectBars.filter(function (project) {
      return project.rate >= 90;
    });
    const todos = expenses.filter(function (expense) {
      return availableActions(user, expense).some(function (action) {
        return ['claim', 'manager_approve', 'exec_approve', 'finance_approve'].includes(action);
      });
    }).sort(function (a, b) {
      return b.updatedAt.localeCompare(a.updatedAt);
    }).slice(0, 5);
    const latest = expenses.slice().sort(function (a, b) {
      return b.updatedAt.localeCompare(a.updatedAt);
    }).slice(0, 5);
    return {
      monthTotal: monthTotal,
      yearTotal: yearTotal,
      approvedUnpaid: approvedUnpaid,
      inReview: inReview,
      pending: pending,
      budgetTotal: budgetTotal,
      spentTotal: spentTotal,
      budgetRate: budgetRate,
      trend: trend,
      deptShare: deptShare,
      categoryShare: categoryShare,
      projectBars: projectBars.slice(0, 5),
      warnings: warnings,
      todos: todos,
      latest: latest,
      announcement: state.settings.announcement,
      unread: unreadNotificationCount(user),
    };
  }

  function renderDashboard() {
    const user = currentUser();
    const data = dashboardData();
    const actions = (canCreateExpense(user) ? `<a class='btn-primary' href='#/expenses/new'>${icon('plus')}新增核銷</a>` : '') + `<button type='button' class='btn-secondary' data-action='export-report'>${icon('download')}匯出報表</button>`;
    const announcement = data.announcement ? `<div class='alert-info mb-6'>${icon('bell')}<div class='flex-1'>${esc(data.announcement)}</div></div>` : '';
    const warnings = data.warnings.length ? `<div class='card mt-6'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>預算警示</h2><span class='badge-amber'>${data.warnings.length} 個專案</span></div><div class='mt-4 space-y-4'>${data.warnings.map(function (project) { return `<div><div class='flex items-center justify-between gap-3 text-sm'><span class='font-medium'>${esc(project.name)}</span><span class='demo-amount ${project.rate > 100 ? 'text-rose-600 dark:text-rose-300' : 'text-amber-600 dark:text-amber-300'}'>${project.rate.toFixed(1)}%</span></div><div class='mt-2 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full ${project.rate > 100 ? 'bg-rose-500' : 'bg-amber-500'}' style='width: ${Math.min(100, project.rate).toFixed(1)}%'></div></div><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>已使用 NT$ ${money(project.spent)} / 預算 NT$ ${money(project.budget)}</p></div>`; }).join('')}</div></div>` : '';
    return `${pageHeader('儀表板', '歡迎回來，' + user.name + '。這裡是您目前可見的核銷概況。', actions)}${announcement}<div class='grid gap-4 sm:grid-cols-2 xl:grid-cols-4'>${statCard('本月核准金額', 'NT$ ' + money(data.monthTotal), '含已核准與已撥款', 'brand')}${statCard('年度核准金額', 'NT$ ' + money(data.yearTotal), '依申請日期統計', 'emerald')}${statCard('待我審核', data.pending + ' 筆', '需要您處理的關卡', 'amber')}${statCard('未撥款金額', 'NT$ ' + money(data.approvedUnpaid), '已核准但尚未撥款', 'rose')}</div><div class='mt-4 grid gap-4 sm:grid-cols-3'><div class='card'><p class='card-title'>審核中</p><p class='mt-2 text-2xl font-bold'>${data.inReview}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>跨部門流程中的核銷單</p></div><div class='card'><p class='card-title'>預算執行率</p><p class='mt-2 text-2xl font-bold'>${data.budgetRate.toFixed(1)}%</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>NT$ ${money(data.spentTotal)} / ${money(data.budgetTotal)}</p></div><div class='card'><p class='card-title'>未讀通知</p><p class='mt-2 text-2xl font-bold'>${data.unread}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>點擊右上角鈴鐺查看</p></div></div><div class='mt-6 grid gap-4 xl:grid-cols-2'><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>近 12 個月核准金額</h2><span class='text-xs text-slate-500 dark:text-slate-400'>NT$</span></div><div class='demo-chart mt-4'><canvas id='dash-trend'></canvas></div></div><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>部門費用占比</h2><span class='text-xs text-slate-500 dark:text-slate-400'>已核准</span></div><div class='demo-chart mt-4'><canvas id='dash-department'></canvas></div></div><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>專案預算 vs 已使用</h2><span class='text-xs text-slate-500 dark:text-slate-400'>NT$</span></div><div class='demo-chart mt-4'><canvas id='dash-projects'></canvas></div></div><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>費用類別占比</h2><span class='text-xs text-slate-500 dark:text-slate-400'>已核准</span></div><div class='demo-chart mt-4'><canvas id='dash-category'></canvas></div></div></div><div class='mt-6 grid gap-4 xl:grid-cols-2'><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>待我審核</h2><a class='text-xs font-medium text-brand-700 hover:underline dark:text-brand-300' href='#/expenses?review=1'>查看全部</a></div><div class='mt-4 space-y-3'>${data.todos.length ? data.todos.map(function (expense) { return `<a class='block rounded-xl border border-slate-200 p-3 hover:border-brand-300 dark:border-slate-800 dark:hover:border-brand-700' href='#/expenses/${expense.id}'><div class='flex items-center justify-between gap-3'><span class='text-sm font-medium'>${esc(expense.number)}</span>${statusBadge(expense.status)}</div><p class='mt-1 text-sm'>${esc(expense.reason)}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(getUser(expense.applicant) ? getUser(expense.applicant).name : expense.applicant)} · NT$ ${money(expenseTotal(expense))}</p></a>`; }).join('') : `<p class='rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400'>目前沒有待您處理的核銷單。</p>`}</div></div><div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>最新核銷</h2><a class='text-xs font-medium text-brand-700 hover:underline dark:text-brand-300' href='#/expenses'>查看全部</a></div><div class='mt-4 space-y-3'>${data.latest.length ? data.latest.map(function (expense) { return `<a class='block rounded-xl border border-slate-200 p-3 hover:border-brand-300 dark:border-slate-800 dark:hover:border-brand-700' href='#/expenses/${expense.id}'><div class='flex items-center justify-between gap-3'><span class='text-sm font-medium'>${esc(expense.number)}</span>${statusBadge(expense.status)}</div><p class='mt-1 text-sm'>${esc(expense.reason)}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(formatDate(expense.applyDate))} · NT$ ${money(expenseTotal(expense))}</p></a>`; }).join('') : `<p class='rounded-xl border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400'>尚無核銷資料。</p>`}</div></div></div>${warnings}`;
  }

  function renderNotFound() {
    return `<div class='card py-16 text-center'><p class='text-5xl font-black tracking-tight text-brand-600 dark:text-brand-300'>404</p><h1 class='mt-4 text-2xl font-bold'>找不到頁面</h1><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>此路由不存在，或您沒有存取權限。</p><a class='btn-primary mt-6' href='#/dashboard'>回到儀表板</a></div>`;
  }

  function option(value, label, current) {
    return `<option value='${esc(value)}' ${String(value) === String(current) ? 'selected' : ''}>${esc(label)}</option>`;
  }

  function selectOptions(items, current) {
    return items.map(function (item) {
      return option(item.value, item.label, current);
    }).join('');
  }

  function blankItem() {
    return { id: null, name: '', spec: '', quantity: 1, unitPrice: 0, categoryCode: 'OTHER', note: '' };
  }

  function blankInvoice() {
    return {
      invoiceType: 'electronic',
      invoiceNo: '',
      issueDate: todayISO(),
      sellerName: '',
      sellerTaxId: '',
      buyerTaxId: BUYER_TAX_ID,
      taxRate: state.settings.defaultTaxRate || 5,
      note: '',
      items: [blankItem()],
    };
  }

  function invoiceTypeLabel(type) {
    const labels = { electronic: '電子發票', triplicate: '三聯式發票', receipt: '收據' };
    return labels[type] || type || '—';
  }

  function itemRowHtml(item, seq) {
    return `<tr data-item-row='${seq}'><td><input class='input min-w-40' data-field='itemName' value='${esc(item.name)}' placeholder='品項名稱' required></td><td><input class='input min-w-28' data-field='itemSpec' value='${esc(item.spec)}' placeholder='規格'></td><td><input class='input w-24' data-field='itemQuantity' type='number' min='0.01' step='0.01' value='${esc(item.quantity)}' required></td><td><input class='input w-32' data-field='itemUnitPrice' type='number' min='0' step='0.01' value='${esc(item.unitPrice)}' required></td><td><select class='select min-w-28' data-field='itemCategory'>${selectOptions(CATEGORIES.map(function (category) { return { value: category.code, label: category.name }; }), item.categoryCode)}</select></td><td><input class='input min-w-28' data-field='itemNote' value='${esc(item.note)}' placeholder='備註'></td><td class='demo-amount text-right' data-subtotal>NT$ ${money(itemSubtotal(item))}</td><td class='text-right'><button type='button' class='btn-ghost btn-sm' data-action='remove-item' aria-label='移除品項'>${icon('close')}</button></td></tr>`;
  }

  function actionButtons(user, expense) {
    const actions = availableActions(user, expense);
    if (!actions.length) return '';
    return actions.map(function (action) {
      const danger = action === 'return' || action === 'reject';
      const className = danger ? 'btn-danger' : action === 'submit' ? 'btn-primary' : 'btn-secondary';
      return `<button type='button' class='${className} btn-sm' data-action='expense-action' data-id='${expense.id}' data-next-action='${action}'>${esc(ACTION_LABELS[action] || action)}</button>`;
    }).join('');
  }

  function workflowStepClass(status) {
    if (status === 'done') return 'bg-emerald-500 text-white';
    if (status === 'current') return 'bg-brand-600 text-white';
    if (status === 'warn') return 'bg-amber-500 text-white';
    if (status === 'danger') return 'bg-rose-500 text-white';
    return 'bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-400';
  }

  function expenseWorkflowSteps(expense) {
    const steps = [
      { status: 'draft', label: '草稿' },
      { status: 'submitted', label: '送審' },
      { status: 'manager_review', label: '主管審核' },
      { status: 'exec_review', label: '上層加簽' },
      { status: 'finance_review', label: '財務審核' },
      { status: 'approved', label: '核准' },
      { status: 'paid', label: '撥款' },
    ];
    const order = steps.map(function (step) { return step.status; });
    let current = order.indexOf(expense.status);
    if (expense.status === 'returned' || expense.status === 'rejected') current = order.indexOf('manager_review');
    return `<ol class='space-y-3'>${steps.map(function (step, index) {
      let stepState = 'todo';
      if (index < current) stepState = 'done';
      if (index === current) {
        if (expense.status === 'returned') stepState = 'warn';
        else if (expense.status === 'rejected') stepState = 'danger';
        else stepState = 'current';
      }
      return `<li class='flex items-center gap-3'><span class='flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${workflowStepClass(stepState)}'>${index + 1}</span><span class='text-sm ${stepState === 'todo' ? 'text-slate-500 dark:text-slate-400' : 'font-medium'}'>${esc(step.label)}</span>${step.status === expense.status ? `<span class='ml-auto text-xs text-slate-500 dark:text-slate-400'>目前</span>` : ''}</li>`;
    }).join('')}</ol>`;
  }

  function approvalTimeline(logs) {
    return `<ol class='demo-timeline space-y-4 pl-5'>${logs.slice().reverse().map(function (log) {
      const actor = getUser(log.actor);
      return `<li class='relative'><span class='absolute -left-5 top-1.5 h-2.5 w-2.5 rounded-full bg-brand-500 ring-4 ring-white dark:ring-slate-900'></span><div class='flex flex-wrap items-center gap-2'><span class='text-sm font-medium'>${esc(APPROVAL_ACTION_LABELS[log.action] || log.action)}</span>${log.toStatus ? statusBadge(log.toStatus) : ''}</div><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(actor ? actor.name : log.actor)} · ${esc(formatDateTime(log.createdAt))}</p>${log.comment ? `<p class='mt-1 text-sm'>${esc(log.comment)}</p>` : ''}</li>`;
    }).join('')}</ol>`;
  }

  function invoiceCard(invoice, index) {
    const totals = invoiceTotals(invoice);
    const items = (invoice.items || []).map(function (item) {
      return `<tr><td>${esc(item.name)}</td><td class='text-slate-500 dark:text-slate-400'>${esc(item.spec || '—')}</td><td class='text-right'>${esc(item.quantity)}</td><td class='text-right'>NT$ ${moneyExact(item.unitPrice)}</td><td>${esc(categoryName(item.categoryCode))}</td><td class='demo-amount text-right'>NT$ ${money(itemSubtotal(item))}</td></tr>`;
    }).join('');
    return `<div class='card mt-4'><div class='flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between'><h2 class='text-sm font-semibold'>發票 ${index + 1}</h2><span class='badge-slate'>${esc(invoiceTypeLabel(invoice.invoiceType))}</span></div><dl class='mt-4 grid gap-3 text-sm sm:grid-cols-2'><div><dt class='text-xs text-slate-500 dark:text-slate-400'>發票號碼</dt><dd class='font-medium'>${esc(invoice.invoiceNo || '—')}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>開立日期</dt><dd>${esc(formatDate(invoice.issueDate))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>賣方</dt><dd>${esc(invoice.sellerName || '—')}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>賣方統編</dt><dd>${esc(invoice.sellerTaxId || '—')}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>買方統編</dt><dd>${esc(invoice.buyerTaxId || BUYER_TAX_ID)}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>稅率</dt><dd>${esc(invoice.taxRate)}%</dd></div></dl>${invoice.note ? `<p class='mt-3 text-sm text-slate-500 dark:text-slate-400'>${esc(invoice.note)}</p>` : ''}<div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>品項</th><th>規格</th><th class='text-right'>數量</th><th class='text-right'>單價</th><th>類別</th><th class='text-right'>小計</th></tr></thead><tbody>${items}</tbody></table></div><div class='mt-4 flex justify-end'><dl class='w-full max-w-xs space-y-1 text-sm'><div class='flex justify-between'><dt class='text-slate-500 dark:text-slate-400'>未稅小計</dt><dd>NT$ ${moneyExact(totals.untaxed)}</dd></div><div class='flex justify-between'><dt class='text-slate-500 dark:text-slate-400'>稅額</dt><dd>NT$ ${moneyExact(totals.tax)}</dd></div><div class='flex justify-between border-t border-slate-200 pt-2 text-base font-bold dark:border-slate-700'><dt>總計</dt><dd class='demo-amount'>NT$ ${moneyExact(totals.total)}</dd></div></dl></div></div>`;
  }

  function renderExpenses(route) {
    const user = currentUser();
    uiState.expenseFilters.mode = route.query.review === '1' ? 'review' : '';
    const filters = uiState.expenseFilters;
    const rows = filteredExpenses();
    const total = round2(rows.reduce(function (sum, expense) {
      return sum + expenseTotal(expense);
    }, 0));
    const departments = canViewAll(user) ? DEPARTMENTS : DEPARTMENTS.filter(function (department) {
      return department.code === user.department;
    });
    const projects = visibleProjects(user);
    const applicants = canViewAll(user) ? state.users : state.users.filter(function (item) {
      return item.department === user.department || item.username === user.username;
    });
    const statusItems = [{ value: '', label: '全部狀態' }].concat(Object.keys(STATUS_META).map(function (status) {
      return { value: status, label: STATUS_META[status].label };
    }));
    const actions = (canCreateExpense(user) ? `<a class='btn-primary' href='#/expenses/new'>${icon('plus')}新增核銷</a>` : '') + `<button type='button' class='btn-secondary' data-action='export-expenses'>${icon('download')}匯出 CSV</button>`;
    const reviewAlert = filters.mode === 'review' ? `<div class='alert-warning mb-4'>${icon('check')}<div class='flex-1'>目前顯示待您審核的核銷單。您只能處理與自己部門相關且非本人申請的單據。</div></div>` : '';
    return `${pageHeader(filters.mode === 'review' ? '待我審核' : '核銷單', '共 ' + rows.length + ' 筆，合計 NT$ ' + money(total), actions)}${reviewAlert}<form id='expense-filter-form' class='card mb-4'><div class='grid gap-3 md:grid-cols-2 xl:grid-cols-4'><div class='form-row'><label class='form-label' for='filter-q'>搜尋</label><input class='input' id='filter-q' name='q' value='${esc(filters.q)}' placeholder='單號、事由、申請人'></div><div class='form-row'><label class='form-label' for='filter-status'>狀態</label><select class='select' id='filter-status' name='status'>${selectOptions(statusItems, filters.status)}</select></div><div class='form-row'><label class='form-label' for='filter-department'>部門</label><select class='select' id='filter-department' name='department'>${selectOptions([{ value: '', label: '全部部門' }].concat(departments.map(function (department) { return { value: department.code, label: department.name }; })), filters.department)}</select></div><div class='form-row'><label class='form-label' for='filter-project'>專案</label><select class='select' id='filter-project' name='project'>${selectOptions([{ value: '', label: '全部專案' }].concat(projects.map(function (project) { return { value: project.code, label: project.code + ' ' + project.name }; })), filters.project)}</select></div><div class='form-row'><label class='form-label' for='filter-category'>類別</label><select class='select' id='filter-category' name='category'>${selectOptions([{ value: '', label: '全部類別' }].concat(CATEGORIES.map(function (category) { return { value: category.code, label: category.name }; })), filters.category)}</select></div><div class='form-row'><label class='form-label' for='filter-applicant'>申請人</label><select class='select' id='filter-applicant' name='applicant'>${selectOptions([{ value: '', label: '全部申請人' }].concat(applicants.map(function (item) { return { value: item.username, label: item.name }; })), filters.applicant)}</select></div><div class='form-row'><label class='form-label' for='filter-date-from'>開始日期</label><input class='input' id='filter-date-from' name='dateFrom' type='date' value='${esc(filters.dateFrom)}'></div><div class='form-row'><label class='form-label' for='filter-date-to'>結束日期</label><input class='input' id='filter-date-to' name='dateTo' type='date' value='${esc(filters.dateTo)}'></div><div class='form-row'><label class='form-label' for='filter-amount-min'>金額下限</label><input class='input' id='filter-amount-min' name='amountMin' type='number' min='0' step='1' value='${esc(filters.amountMin)}' placeholder='0'></div><div class='form-row'><label class='form-label' for='filter-amount-max'>金額上限</label><input class='input' id='filter-amount-max' name='amountMax' type='number' min='0' step='1' value='${esc(filters.amountMax)}' placeholder='不限'></div></div><div class='mt-4 flex justify-end'><button type='button' class='btn-ghost btn-sm' data-action='reset-expense-filters'>${icon('refresh')}清除條件</button></div></form>${expenseTable(rows)}`;
  }

  function renderExpenseDetail(id) {
    const user = currentUser();
    const expense = getExpense(id);
    if (!expense || !canViewExpense(user, expense)) {
      return `<div class='card text-center'><h1 class='text-xl font-bold'>找不到核銷單</h1><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>此核銷單不存在，或您沒有檢視權限。</p><a class='btn-primary mt-4' href='#/expenses'>回到核銷單列表</a></div>`;
    }
    const applicant = getUser(expense.applicant);
    const project = getProject(expense.projectCode);
    const total = expenseTotal(expense);
    const editButton = canEditExpense(user, expense) ? `<a class='btn-secondary' href='#/expenses/edit/${expense.id}'>${icon('expenses')}編輯</a>` : '';
    const actions = editButton + actionButtons(user, expense);
    const budgetRate = project ? projectRate(project) : 0;
    const invoices = expense.invoices.map(invoiceCard).join('');
    const budget = project ? `<div class='card'><div class='flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>專案預算</h2><span class='${projectStatusMeta(project.status).badge}'>${esc(projectStatusMeta(project.status).label)}</span></div><p class='mt-3 text-sm font-medium'>${esc(project.name)}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(project.code)} · ${esc(projectTypeName(project.projectType))}</p><div class='mt-3 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full ${budgetRate > 100 ? 'bg-rose-500' : budgetRate >= 90 ? 'bg-amber-500' : 'bg-brand-600'}' style='width: ${Math.min(100, budgetRate).toFixed(1)}%'></div></div><div class='mt-2 flex justify-between text-xs text-slate-500 dark:text-slate-400'><span>已使用 NT$ ${money(projectSpent(project.code))}</span><span>${budgetRate.toFixed(1)}%</span></div><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>預算 NT$ ${money(project.budgetTotal)}</p></div>` : `<div class='card'><p class='text-sm text-slate-500 dark:text-slate-400'>找不到專案資料。</p></div>`;
    const meta = `<div class='card'><h2 class='text-sm font-semibold'>流程資訊</h2><dl class='mt-4 space-y-3 text-sm'><div><dt class='text-xs text-slate-500 dark:text-slate-400'>建立時間</dt><dd>${esc(formatDateTime(expense.createdAt))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>最後更新</dt><dd>${esc(formatDateTime(expense.updatedAt))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>送審時間</dt><dd>${esc(formatDateTime(expense.submittedAt))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>核准時間</dt><dd>${esc(formatDateTime(expense.approvedAt))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>撥款時間</dt><dd>${esc(formatDateTime(expense.paidAt))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>版本</dt><dd>v${esc(expense.version)}</dd></div></dl></div>`;
    return `${pageHeader(expense.number, expense.reason, actions)}<div class='grid gap-4 xl:grid-cols-3'><div class='xl:col-span-2'><div class='card'><div class='flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between'><div><div class='flex flex-wrap items-center gap-2'>${statusBadge(expense.status)}<span class='text-xs text-slate-500 dark:text-slate-400'>${esc(formatDate(expense.applyDate))}</span></div><p class='mt-3 text-3xl font-bold tracking-tight demo-amount'>NT$ ${moneyExact(total)}</p><p class='mt-1 text-sm text-slate-500 dark:text-slate-400'>${esc(expense.reason)}</p></div><div class='text-sm sm:text-right'><p class='font-medium'>${esc(applicant ? applicant.name : expense.applicant)}</p><p class='text-xs text-slate-500 dark:text-slate-400'>${esc(departmentName(expense.department))}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(applicant ? applicant.email : '')}</p></div></div><dl class='mt-6 grid gap-4 border-t border-slate-200 pt-4 text-sm dark:border-slate-800 sm:grid-cols-3'><div><dt class='text-xs text-slate-500 dark:text-slate-400'>專案</dt><dd class='mt-1 font-medium'>${esc(project ? project.name : expense.projectCode)}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>專案代碼</dt><dd class='mt-1'>${esc(expense.projectCode)}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>專案類型</dt><dd class='mt-1'>${esc(projectTypeName(expense.projectTypeCode))}</dd></div></dl></div>${invoices}<div class='card mt-4'><h2 class='text-sm font-semibold'>審核歷程</h2><div class='mt-4'>${approvalTimeline(expense.logs)}</div></div></div><div class='space-y-4'><div class='card'><h2 class='text-sm font-semibold'>流程進度</h2><div class='mt-4'>${expenseWorkflowSteps(expense)}</div>${expense.status === 'returned' ? `<div class='alert-warning mt-4'>${icon('alert')}<span>此單已退回，請修改後重新送審。</span></div>` : ''}${expense.status === 'rejected' ? `<div class='alert-error mt-4'>${icon('alert')}<span>此單已駁回，無法繼續流程。</span></div>` : ''}</div>${budget}${meta}</div></div>`;
  }

  function renderExpenseForm(id) {
    const user = currentUser();
    const isEdit = id !== null && id !== undefined;
    const expense = isEdit ? getExpense(id) : null;
    if (isEdit && (!expense || !canEditExpense(user, expense))) {
      return `<div class='card text-center'><h1 class='text-xl font-bold'>無法編輯</h1><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>此核銷單不存在、已進入審核流程，或您沒有編輯權限。</p><a class='btn-primary mt-4' href='#/expenses'>回到核銷單列表</a></div>`;
    }
    const projects = visibleProjects(user);
    if (!projects.length) {
      return `<div class='alert-warning'>${icon('alert')}<span>目前沒有可選專案，請先建立專案資料。</span></div>`;
    }
    const invoice = expense && expense.invoices.length ? expense.invoices[0] : blankInvoice();
    const items = invoice.items && invoice.items.length ? invoice.items : [blankItem()];
    const applicant = expense ? getUser(expense.applicant) : user;
    const project = expense ? getProject(expense.projectCode) : projects[0];
    const selectedProject = project ? project.code : projects[0].code;
    uiState.itemRowSeq = Math.max(uiState.itemRowSeq, items.length + 1);
    const projectOptions = selectOptions(projects.map(function (item) { return { value: item.code, label: item.code + ' ' + item.name }; }), selectedProject);
    const invoiceTypeOptions = selectOptions([{ value: 'electronic', label: '電子發票' }, { value: 'triplicate', label: '三聯式發票' }, { value: 'receipt', label: '收據' }], invoice.invoiceType);
    const title = isEdit ? '編輯核銷單' : '新增核銷單';
    const subtitle = isEdit ? '修改草稿或退回的核銷單，儲存後可重新送審。' : '填寫核銷內容與發票明細，儲存草稿或直接送審。';
    const cancelHref = expense ? '#/expenses/' + expense.id : '#/expenses';
    return `${pageHeader(title, subtitle, `<a class='btn-secondary' href='${cancelHref}'>取消</a>`)}<form id='expense-form' data-id='${expense ? expense.id : ''}' class='space-y-4'><div class='card'><h2 class='text-sm font-semibold'>基本資料</h2><div class='mt-4 grid gap-4 sm:grid-cols-2'><div class='form-row'><label class='form-label'>申請人</label><div class='input bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400'>${esc(applicant.name)} · ${esc(departmentName(applicant.department))}</div></div><div class='form-row'><label class='form-label' for='applyDate'>申請日期</label><input class='input' id='applyDate' name='applyDate' type='date' value='${esc(expense ? expense.applyDate : todayISO())}' required></div><div class='form-row'><label class='form-label' for='projectCode'>專案</label><select class='select' id='projectCode' name='projectCode' required>${projectOptions}</select></div><div class='form-row'><label class='form-label'>部門</label><div class='input bg-slate-50 text-slate-500 dark:bg-slate-800 dark:text-slate-400'>${esc(departmentName(applicant.department))}</div></div></div><div class='form-row mt-4'><label class='form-label' for='reason'>事由</label><textarea class='textarea' id='reason' name='reason' required placeholder='請說明費用用途'>${esc(expense ? expense.reason : '')}</textarea></div></div><div class='card'><div class='flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between'><h2 class='text-sm font-semibold'>發票資訊</h2><span class='badge-slate'>買受人統編 ${BUYER_TAX_ID}</span></div><div class='mt-4 grid gap-4 sm:grid-cols-2'><div class='form-row'><label class='form-label' for='invoiceType'>發票類型</label><select class='select' id='invoiceType' name='invoiceType'>${invoiceTypeOptions}</select></div><div class='form-row'><label class='form-label' for='invoiceNo'>發票號碼</label><input class='input' id='invoiceNo' name='invoiceNo' value='${esc(invoice.invoiceNo)}' placeholder='例如 AB12345678'></div><div class='form-row'><label class='form-label' for='issueDate'>開立日期</label><input class='input' id='issueDate' name='issueDate' type='date' value='${esc(invoice.issueDate || todayISO())}' required></div><div class='form-row'><label class='form-label' for='taxRate'>稅率 (%)</label><input class='input' id='taxRate' name='taxRate' type='number' min='0' max='100' step='0.1' value='${esc(invoice.taxRate)}' required></div><div class='form-row'><label class='form-label' for='sellerName'>賣方名稱</label><input class='input' id='sellerName' name='sellerName' value='${esc(invoice.sellerName)}' placeholder='商店或供應商名稱'></div><div class='form-row'><label class='form-label' for='sellerTaxId'>賣方統編</label><input class='input' id='sellerTaxId' name='sellerTaxId' value='${esc(invoice.sellerTaxId)}' placeholder='統一編號'></div></div><div class='form-row mt-4'><label class='form-label' for='invoiceNote'>發票備註</label><textarea class='textarea' id='invoiceNote' name='invoiceNote' placeholder='選填'>${esc(invoice.note)}</textarea></div></div><div class='card'><div class='flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between'><div><h2 class='text-sm font-semibold'>品項明細</h2><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>數量 × 單價會自動計算小計與稅額。</p></div><button type='button' class='btn-secondary btn-sm' data-action='add-item'>${icon('plus')}新增品項</button></div><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>品項</th><th>規格</th><th>數量</th><th>單價</th><th>類別</th><th>備註</th><th class='text-right'>小計</th><th></th></tr></thead><tbody id='invoice-items'>${items.map(function (item, index) { return itemRowHtml(item, index + 1); }).join('')}</tbody></table></div></div><div class='card'><div class='flex justify-end'><dl class='w-full max-w-sm space-y-2 text-sm'><div class='flex justify-between'><dt class='text-slate-500 dark:text-slate-400'>未稅小計</dt><dd id='form-subtotal'>NT$ ${moneyExact(invoiceTotals(invoice).untaxed)}</dd></div><div class='flex justify-between'><dt class='text-slate-500 dark:text-slate-400'>稅額</dt><dd id='form-tax'>NT$ ${moneyExact(invoiceTotals(invoice).tax)}</dd></div><div class='flex justify-between border-t border-slate-200 pt-2 text-lg font-bold dark:border-slate-700'><dt>總計</dt><dd class='demo-amount' id='form-total'>NT$ ${moneyExact(invoiceTotals(invoice).total)}</dd></div></dl></div></div><div class='flex flex-col-reverse gap-2 sm:flex-row sm:justify-end'><a class='btn-secondary' href='${cancelHref}'>取消</a><button type='submit' class='btn-secondary' data-submit-mode='draft'>儲存草稿</button><button type='submit' class='btn-primary' data-submit-mode='submit'>${isEdit && expense.status === 'returned' ? '儲存並重新送審' : '儲存並送審'}</button></div></form>`;
  }

  function projectRow(project) {
    const owner = getUser(project.owner);
    const rate = projectRate(project);
    return `<tr><td><a class='font-medium text-brand-700 hover:underline dark:text-brand-300' href='#/projects/${encodeURIComponent(project.code)}'>${esc(project.code)}</a></td><td><span class='block'>${esc(project.name)}</span><span class='block text-xs text-slate-500 dark:text-slate-400'>${esc(projectTypeName(project.projectType))}</span></td><td>${esc(departmentName(project.department))}</td><td>${esc(owner ? owner.name : project.owner)}</td><td class='demo-amount'>NT$ ${money(project.budgetTotal)}</td><td class='demo-amount'>NT$ ${money(projectSpent(project.code))}</td><td><div class='flex items-center gap-2'><div class='h-2 w-24 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full ${rate > 100 ? 'bg-rose-500' : rate >= 90 ? 'bg-amber-500' : 'bg-brand-600'}' style='width: ${Math.min(100, rate).toFixed(1)}%'></div></div><span class='text-xs ${rate >= 90 ? 'text-amber-600 dark:text-amber-300' : 'text-slate-500 dark:text-slate-400'}'>${rate.toFixed(1)}%</span></div></td><td><span class='${projectStatusMeta(project.status).badge}'>${esc(projectStatusMeta(project.status).label)}</span></td><td class='text-right'><a class='btn-ghost btn-sm' href='#/projects/${encodeURIComponent(project.code)}' aria-label='檢視 ${esc(project.code)}'>${icon('arrow')}</a></td></tr>`;
  }

  function renderProjects() {
    const user = currentUser();
    const rows = filteredProjects();
    const totalBudget = round2(rows.reduce(function (sum, project) { return sum + Number(project.budgetTotal || 0); }, 0));
    const totalSpent = round2(rows.reduce(function (sum, project) { return sum + projectSpent(project.code); }, 0));
    const active = rows.filter(function (project) { return project.status === 'active'; }).length;
    const filters = uiState.projectFilters;
    const statusItems = [{ value: '', label: '全部狀態' }, { value: 'planning', label: '規劃中' }, { value: 'active', label: '進行中' }, { value: 'closed', label: '結案' }];
    return `${pageHeader('專案', '共 ' + rows.length + ' 個專案，總預算 NT$ ' + money(totalBudget), canManageMaster(user) ? `<a class='btn-secondary' href='#/master'>${icon('settings')}基礎資料</a>` : '')}<div class='grid gap-4 sm:grid-cols-3'><div class='card'><p class='card-title'>專案數</p><p class='mt-2 text-2xl font-bold'>${rows.length}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${active} 個進行中</p></div><div class='card'><p class='card-title'>總預算</p><p class='mt-2 text-2xl font-bold demo-amount'>NT$ ${money(totalBudget)}</p></div><div class='card'><p class='card-title'>已使用</p><p class='mt-2 text-2xl font-bold demo-amount'>NT$ ${money(totalSpent)}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${totalBudget ? (totalSpent / totalBudget * 100).toFixed(1) : '0.0'}%</p></div></div><form id='project-filter-form' class='card my-4'><div class='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'><div class='form-row'><label class='form-label' for='project-filter-q'>搜尋</label><input class='input' id='project-filter-q' name='q' value='${esc(filters.q)}' placeholder='專案代碼或名稱'></div><div class='form-row'><label class='form-label' for='project-filter-status'>狀態</label><select class='select' id='project-filter-status' name='status'>${selectOptions(statusItems, filters.status)}</select></div><div class='flex items-end'><button type='button' class='btn-ghost btn-sm' data-action='reset-project-filters'>${icon('refresh')}清除條件</button></div></div></form><div class='table-wrap'><table class='table'><thead><tr><th>專案代碼</th><th>名稱</th><th>部門</th><th>負責人</th><th>預算</th><th>已使用</th><th>執行率</th><th>狀態</th><th></th></tr></thead><tbody>${rows.length ? rows.map(projectRow).join('') : `<tr><td colspan='9' class='py-8 text-center text-slate-500 dark:text-slate-400'>沒有符合條件的專案。</td></tr>`}</tbody></table></div>`;
  }

  function renderProjectDetail(code) {
    const user = currentUser();
    const project = getProject(code);
    if (!project || !visibleProjects(user).some(function (item) { return item.code === project.code; })) {
      return `<div class='card text-center'><h1 class='text-xl font-bold'>找不到專案</h1><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>此專案不存在，或您沒有檢視權限。</p><a class='btn-primary mt-4' href='#/projects'>回到專案列表</a></div>`;
    }
    const owner = getUser(project.owner);
    const expenses = visibleExpenses(user).filter(function (expense) {
      return expense.projectCode === project.code;
    }).sort(function (a, b) {
      return b.applyDate.localeCompare(a.applyDate);
    });
    const approved = expenses.filter(function (expense) {
      return expense.status === 'approved' || expense.status === 'paid';
    });
    const spent = projectSpent(project.code);
    const rate = projectRate(project);
    const catTotals = categoryTotals(approved);
    const catRows = CATEGORIES.map(function (category) {
      return { label: category.name, value: round2(catTotals[category.code] || 0) };
    }).filter(function (item) { return item.value > 0; }).sort(function (a, b) { return b.value - a.value; });
    const totalCat = round2(catRows.reduce(function (sum, item) { return sum + item.value; }, 0));
    return `${pageHeader(project.code, project.name, `<a class='btn-secondary' href='#/projects'>${icon('arrow')}回到專案列表</a>`)}<div class='grid gap-4 sm:grid-cols-2 xl:grid-cols-4'><div class='card'><p class='card-title'>總預算</p><p class='mt-2 text-2xl font-bold demo-amount'>NT$ ${money(project.budgetTotal)}</p></div><div class='card'><p class='card-title'>已使用</p><p class='mt-2 text-2xl font-bold demo-amount'>NT$ ${money(spent)}</p></div><div class='card'><p class='card-title'>剩餘預算</p><p class='mt-2 text-2xl font-bold demo-amount ${spent > project.budgetTotal ? 'text-rose-600 dark:text-rose-300' : ''}'>NT$ ${money(Number(project.budgetTotal) - spent)}</p></div><div class='card'><p class='card-title'>執行率</p><p class='mt-2 text-2xl font-bold ${rate >= 90 ? 'text-amber-600 dark:text-amber-300' : 'text-brand-600 dark:text-brand-300'}'>${rate.toFixed(1)}%</p></div></div><div class='mt-4 grid gap-4 xl:grid-cols-3'><div class='card xl:col-span-2'><div class='flex flex-wrap items-center gap-2'><span class='${projectStatusMeta(project.status).badge}'>${esc(projectStatusMeta(project.status).label)}</span><span class='badge-slate'>${esc(projectTypeName(project.projectType))}</span></div><p class='mt-4 text-sm leading-6 text-slate-600 dark:text-slate-300'>${esc(project.description || '尚無專案說明。')}</p><dl class='mt-5 grid gap-4 border-t border-slate-200 pt-4 text-sm dark:border-slate-800 sm:grid-cols-2'><div><dt class='text-xs text-slate-500 dark:text-slate-400'>部門</dt><dd class='mt-1'>${esc(departmentName(project.department))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>負責人</dt><dd class='mt-1'>${esc(owner ? owner.name : project.owner)}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>開始日期</dt><dd class='mt-1'>${esc(formatDate(project.startDate))}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>結束日期</dt><dd class='mt-1'>${esc(formatDate(project.endDate))}</dd></div></dl><div class='mt-5'><div class='flex justify-between text-xs text-slate-500 dark:text-slate-400'><span>預算執行</span><span>${rate.toFixed(1)}%</span></div><div class='mt-2 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full ${rate > 100 ? 'bg-rose-500' : rate >= 90 ? 'bg-amber-500' : 'bg-brand-600'}' style='width: ${Math.min(100, rate).toFixed(1)}%'></div></div></div></div><div class='card'><h2 class='text-sm font-semibold'>費用類別</h2><div class='mt-4 space-y-3'>${catRows.length ? catRows.map(function (item) { return `<div><div class='flex justify-between gap-3 text-sm'><span>${esc(item.label)}</span><span class='demo-amount'>NT$ ${money(item.value)}</span></div><div class='mt-1 h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full bg-brand-500' style='width: ${(totalCat ? item.value / totalCat * 100 : 0).toFixed(1)}%'></div></div></div>`; }).join('') : `<p class='text-sm text-slate-500 dark:text-slate-400'>尚無已核准費用。</p>`}</div></div></div><div class='mt-4'><div class='mb-3 flex items-center justify-between gap-3'><h2 class='text-sm font-semibold'>專案核銷單</h2><span class='text-xs text-slate-500 dark:text-slate-400'>共 ${expenses.length} 筆</span></div>${expenseTable(expenses)}</div>`;
  }

  function reportData() {
    const filters = uiState.reportFilters;
    const rows = reportPeriodExpenses();
    const total = round2(rows.reduce(function (sum, expense) { return sum + expenseTotal(expense); }, 0));
    const count = rows.length;
    const average = count ? round2(total / count) : 0;
    const year = Number(filters.year);
    const trend = monthSeries(rows, year);
    const deptRows = DEPARTMENTS.map(function (department) {
      const deptRowsFiltered = rows.filter(function (expense) { return expense.department === department.code; });
      return {
        label: department.name,
        count: deptRowsFiltered.length,
        value: round2(deptRowsFiltered.reduce(function (sum, expense) { return sum + expenseTotal(expense); }, 0)),
      };
    }).filter(function (item) { return item.count > 0; }).sort(function (a, b) { return b.value - a.value; });
    const catTotals = categoryTotals(rows);
    const catRows = CATEGORIES.map(function (category) {
      return {
        label: category.name,
        count: rows.filter(function (expense) {
          return expense.invoices.some(function (invoice) {
            return invoice.items.some(function (item) { return item.categoryCode === category.code; });
          });
        }).length,
        value: round2(catTotals[category.code] || 0),
      };
    }).filter(function (item) { return item.value > 0; }).sort(function (a, b) { return b.value - a.value; });
    const projectTotals = groupSum(rows, function (expense) { return expense.projectCode; }, expenseTotal);
    const projectRows = Object.keys(projectTotals).map(function (code) {
      const project = getProject(code);
      return {
        label: project ? project.name : code,
        count: rows.filter(function (expense) { return expense.projectCode === code; }).length,
        value: round2(projectTotals[code]),
      };
    }).sort(function (a, b) { return b.value - a.value; });
    const applicantTotals = groupSum(rows, function (expense) { return expense.applicant; }, expenseTotal);
    const applicantRows = Object.keys(applicantTotals).map(function (username) {
      const applicant = getUser(username);
      return {
        label: applicant ? applicant.name : username,
        count: rows.filter(function (expense) { return expense.applicant === username; }).length,
        value: round2(applicantTotals[username]),
      };
    }).sort(function (a, b) { return b.value - a.value; });
    const matrix = { departments: DEPARTMENTS.map(function (item) { return item.name; }), categories: CATEGORIES.map(function (item) { return item.name; }), values: {} };
    rows.forEach(function (expense) {
      const dept = departmentName(expense.department);
      if (!matrix.values[dept]) matrix.values[dept] = {};
      expense.invoices.forEach(function (invoice) {
        const parts = invoiceCategoryTotals(invoice);
        Object.keys(parts).forEach(function (code) {
          const category = categoryName(code);
          matrix.values[dept][category] = round2((matrix.values[dept][category] || 0) + parts[code]);
        });
      });
    });
    const matrixCategories = matrix.categories.filter(function (category) {
      return matrix.departments.some(function (dept) {
        return matrix.values[dept] && matrix.values[dept][category];
      });
    });
    return {
      rows: rows,
      total: total,
      count: count,
      average: average,
      trend: trend,
      deptRows: deptRows,
      catRows: catRows,
      projectRows: projectRows,
      applicantRows: applicantRows,
      matrix: matrix,
      matrixCategories: matrixCategories,
      year: year,
      quarter: filters.quarter,
      month: filters.month,
    };
  }

  function breakdownTable(title, rows, total) {
    const safeTotal = total || 1;
    return `<div class='card'><h2 class='text-sm font-semibold'>${esc(title)}</h2><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>項目</th><th class='text-right'>筆數</th><th class='text-right'>金額</th><th class='text-right'>占比</th></tr></thead><tbody>${rows.length ? rows.map(function (item) { return `<tr><td>${esc(item.label)}</td><td class='text-right'>${item.count}</td><td class='demo-amount text-right'>NT$ ${money(item.value)}</td><td class='text-right text-slate-500 dark:text-slate-400'>${(item.value / safeTotal * 100).toFixed(1)}%</td></tr>`; }).join('') : `<tr><td colspan='4' class='py-6 text-center text-slate-500 dark:text-slate-400'>此期間沒有資料。</td></tr>`}</tbody></table></div></div>`;
  }

  function renderReports() {
    const data = reportData();
    const filters = uiState.reportFilters;
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let year = currentYear - 2; year <= currentYear + 1; year += 1) years.push({ value: String(year), label: String(year) + ' 年' });
    const quarters = [{ value: '', label: '全年' }, { value: '1', label: 'Q1' }, { value: '2', label: 'Q2' }, { value: '3', label: 'Q3' }, { value: '4', label: 'Q4' }];
    const months = [{ value: '', label: '全部月份' }];
    for (let month = 1; month <= 12; month += 1) months.push({ value: String(month), label: month + ' 月' });
    const periodLabel = filters.month ? filters.year + ' 年 ' + filters.month + ' 月' : filters.quarter ? filters.year + ' 年 Q' + filters.quarter : filters.year + ' 年';
    return `${pageHeader('報表', periodLabel + ' 已核准費用分析', `<button type='button' class='btn-secondary' data-action='export-report'>${icon('download')}匯出 CSV</button>`)}<form id='report-filter-form' class='card mb-4'><div class='grid gap-3 sm:grid-cols-2 lg:grid-cols-4'><div class='form-row'><label class='form-label' for='report-year'>年度</label><select class='select' id='report-year' name='year'>${selectOptions(years, filters.year)}</select></div><div class='form-row'><label class='form-label' for='report-quarter'>季度</label><select class='select' id='report-quarter' name='quarter'>${selectOptions(quarters, filters.quarter)}</select></div><div class='form-row'><label class='form-label' for='report-month'>月份</label><select class='select' id='report-month' name='month'>${selectOptions(months, filters.month)}</select></div><div class='flex items-end'><button type='button' class='btn-ghost btn-sm' data-action='reset-report-filters'>${icon('refresh')}重設</button></div></div></form><div class='grid gap-4 sm:grid-cols-2 xl:grid-cols-4'><div class='card'><p class='card-title'>核准總額</p><p class='kpi-value'>NT$ ${money(data.total)}</p></div><div class='card'><p class='card-title'>核准筆數</p><p class='kpi-value'>${data.count}</p></div><div class='card'><p class='card-title'>平均單筆</p><p class='kpi-value'>NT$ ${money(data.average)}</p></div><div class='card'><p class='card-title'>最高部門</p><p class='mt-2 text-2xl font-bold'>${esc(data.deptRows.length ? data.deptRows[0].label : '—')}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${data.deptRows.length ? 'NT$ ' + money(data.deptRows[0].value) : '尚無資料'}</p></div></div><div class='mt-4 grid gap-4 xl:grid-cols-2'><div class='card'><h2 class='text-sm font-semibold'>月度趨勢</h2><div class='demo-chart mt-4'><canvas id='report-trend'></canvas></div></div><div class='card'><h2 class='text-sm font-semibold'>部門占比</h2><div class='demo-chart mt-4'><canvas id='report-department'></canvas></div></div><div class='card'><h2 class='text-sm font-semibold'>類別占比</h2><div class='demo-chart mt-4'><canvas id='report-category'></canvas></div></div><div class='card'><h2 class='text-sm font-semibold'>專案排行</h2><div class='mt-4 space-y-3'>${data.projectRows.length ? data.projectRows.map(function (item) { return `<div><div class='flex justify-between gap-3 text-sm'><span class='font-medium'>${esc(item.label)}</span><span class='demo-amount'>NT$ ${money(item.value)}</span></div><div class='mt-1 h-1.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800'><div class='h-full rounded-full bg-brand-500' style='width: ${(data.total ? item.value / data.total * 100 : 0).toFixed(1)}%'></div></div></div>`; }).join('') : `<p class='text-sm text-slate-500 dark:text-slate-400'>此期間沒有資料。</p>`}</div></div></div><div class='mt-4 grid gap-4 xl:grid-cols-2'>${breakdownTable('部門明細', data.deptRows, data.total)}${breakdownTable('類別明細', data.catRows, data.total)}${breakdownTable('專案明細', data.projectRows, data.total)}${breakdownTable('申請人明細', data.applicantRows, data.total)}</div><div class='card mt-4'><h2 class='text-sm font-semibold'>部門 × 類別交叉分析</h2><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>部門</th>${data.matrixCategories.map(function (category) { return `<th class='text-right'>${esc(category)}</th>`; }).join('')}<th class='text-right'>合計</th></tr></thead><tbody>${data.matrix.departments.map(function (dept) { const deptValues = data.matrix.values[dept] || {}; const rowTotal = round2(data.matrixCategories.reduce(function (sum, category) { return sum + Number(deptValues[category] || 0); }, 0)); return `<tr><td class='font-medium'>${esc(dept)}</td>${data.matrixCategories.map(function (category) { return `<td class='demo-amount text-right'>NT$ ${money(deptValues[category] || 0)}</td>`; }).join('')}<td class='demo-amount text-right font-semibold'>NT$ ${money(rowTotal)}</td></tr>`; }).join('')}</tbody></table></div></div>`;
  }

  function accessDenied(title) {
    return `<div class='card py-16 text-center'><p class='text-5xl font-black tracking-tight text-rose-600 dark:text-rose-300'>403</p><h1 class='mt-4 text-2xl font-bold'>沒有存取權限</h1><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>${esc(title)}僅限特定角色使用。</p><a class='btn-primary mt-6' href='#/dashboard'>回到儀表板</a></div>`;
  }

  function roleBadge(role) {
    const classes = {
      admin: 'badge-purple',
      finance: 'badge-indigo',
      manager: 'badge-amber',
      employee: 'badge-sky',
      auditor: 'badge-slate',
    };
    return `<span class='${classes[role] || 'badge-slate'}'>${esc(roleLabel(role))}</span>`;
  }

  function notificationLevelBadge(level) {
    const classes = {
      success: 'badge-emerald',
      warning: 'badge-amber',
      danger: 'badge-rose',
      info: 'badge-sky',
    };
    return `<span class='${classes[level] || 'badge-slate'}'>${esc(level === 'success' ? '成功' : level === 'warning' ? '提醒' : level === 'danger' ? '警示' : '資訊')}</span>`;
  }

  function renderNotifications() {
    const user = currentUser();
    const items = state.notifications.filter(function (notification) {
      return notification.to === user.username;
    }).slice().sort(function (a, b) {
      return b.createdAt.localeCompare(a.createdAt);
    });
    const unread = items.filter(function (notification) { return !notification.isRead; }).length;
    const actions = unread ? `<button type='button' class='btn-secondary' data-action='mark-all-notifications'>${icon('check')}全部標為已讀</button>` : '';
    const cards = items.length ? items.map(function (notification) {
      return `<div class='card ${notification.isRead ? '' : 'border-brand-200 bg-brand-50/40 dark:border-brand-900 dark:bg-brand-950/20'}'><div class='flex items-start gap-3'><span class='flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${notification.level === 'danger' ? 'bg-rose-100 text-rose-600 dark:bg-rose-900/50 dark:text-rose-300' : notification.level === 'warning' ? 'bg-amber-100 text-amber-600 dark:bg-amber-900/50 dark:text-amber-300' : notification.level === 'success' ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/50 dark:text-emerald-300' : 'bg-sky-100 text-sky-600 dark:bg-sky-900/50 dark:text-sky-300'}'>${icon(notification.level === 'danger' || notification.level === 'warning' ? 'alert' : 'bell')}</span><div class='min-w-0 flex-1'><div class='flex flex-wrap items-center gap-2'><h2 class='text-sm font-semibold'>${esc(notification.title)}</h2>${notificationLevelBadge(notification.level)}${notification.isRead ? '' : `<span class='badge-rose'>未讀</span>`}</div><p class='mt-1 text-sm text-slate-600 dark:text-slate-300'>${esc(notification.message)}</p><p class='mt-1 text-xs text-slate-500 dark:text-slate-400'>${esc(formatDateTime(notification.createdAt))}</p></div><div class='flex shrink-0 flex-col gap-2 sm:flex-row'>${notification.expenseId ? `<a class='btn-ghost btn-sm' href='#/expenses/${notification.expenseId}' data-action='read-notification' data-id='${notification.id}'>查看</a>` : ''}${notification.isRead ? '' : `<button type='button' class='btn-ghost btn-sm' data-action='read-notification' data-id='${notification.id}'>標為已讀</button>`}</div></div></div>`;
    }).join('') : `<div class='rounded-2xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400'>目前沒有通知。</div>`;
    return `${pageHeader('通知', unread ? unread + ' 則未讀通知' : '所有通知都已讀', actions)}<div class='space-y-3'>${cards}</div>`;
  }

  function renderUsers() {
    const user = currentUser();
    if (!user || user.role !== 'admin') return accessDenied('使用者管理');
    const rows = state.users.map(function (item) {
      return `<tr><td><span class='block font-medium'>${esc(item.name)}</span><span class='block text-xs text-slate-500 dark:text-slate-400'>${esc(item.username)}</span></td><td>${roleBadge(item.role)}</td><td>${esc(departmentName(item.department))}</td><td>${esc(item.title || '—')}</td><td>${esc(item.email || '—')}</td><td>${item.active ? `<span class='badge-emerald'>啟用</span>` : `<span class='badge-slate'>停用</span>`}</td><td>${item.totp ? `<span class='badge-indigo'>已啟用</span>` : `<span class='badge-slate'>未啟用</span>`}</td></tr>`;
    }).join('');
    return `${pageHeader('使用者', '示範帳號與角色權限一覽', `<button type='button' class='btn-secondary' data-action='reset-demo'>${icon('refresh')}重設示範資料</button>`)}<div class='alert-info mb-4'>${icon('shield')}<div class='flex-1'>此示範版帳號為硬編碼，不會寫入後端。登入狀態與操作資料存在瀏覽器 localStorage。</div></div><div class='table-wrap'><table class='table'><thead><tr><th>使用者</th><th>角色</th><th>部門</th><th>職稱</th><th>Email</th><th>狀態</th><th>TOTP</th></tr></thead><tbody>${rows}</tbody></table></div>`;
  }

  function auditActionBadge(action) {
    const classes = {
      create: 'badge-emerald',
      update: 'badge-sky',
      delete: 'badge-rose',
      login: 'badge-indigo',
      logout: 'badge-slate',
      export: 'badge-amber',
      backup: 'badge-purple',
      restore: 'badge-orange',
    };
    return `<span class='${classes[action] || 'badge-slate'}'>${esc(AUDIT_ACTION_LABELS[action] || action)}</span>`;
  }

  function renderAudit() {
    const user = currentUser();
    if (!user || (user.role !== 'admin' && user.role !== 'auditor')) return accessDenied('稽核軌跡');
    const filters = uiState.auditFilters;
    const rows = filteredAuditLogs();
    const actionItems = [{ value: '', label: '全部動作' }].concat(Object.keys(AUDIT_ACTION_LABELS).map(function (action) {
      return { value: action, label: AUDIT_ACTION_LABELS[action] };
    }));
    return `${pageHeader('稽核', '共 ' + rows.length + ' 筆操作紀錄', `<button type='button' class='btn-secondary' data-action='export-audit'>${icon('download')}匯出 CSV</button>`)}<form id='audit-filter-form' class='card mb-4'><div class='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'><div class='form-row'><label class='form-label' for='audit-filter-q'>搜尋</label><input class='input' id='audit-filter-q' name='q' value='${esc(filters.q)}' placeholder='使用者、模型、物件、IP'></div><div class='form-row'><label class='form-label' for='audit-filter-action'>動作</label><select class='select' id='audit-filter-action' name='action'>${selectOptions(actionItems, filters.action)}</select></div><div class='flex items-end'><button type='button' class='btn-ghost btn-sm' data-action='reset-audit-filters'>${icon('refresh')}清除條件</button></div></div></form><div class='table-wrap'><table class='table'><thead><tr><th>時間</th><th>使用者</th><th>動作</th><th>模型</th><th>物件</th><th>IP</th><th>變更</th></tr></thead><tbody>${rows.length ? rows.map(function (log) { return `<tr><td class='text-slate-500 dark:text-slate-400'>${esc(formatDateTime(log.createdAt))}</td><td>${esc(log.username)}</td><td>${auditActionBadge(log.action)}</td><td class='text-slate-500 dark:text-slate-400'>${esc(log.modelLabel)}</td><td>${esc(log.objectRepr)}</td><td class='text-slate-500 dark:text-slate-400'>${esc(log.ip)}</td><td class='max-w-xs truncate text-slate-500 dark:text-slate-400' title='${esc(log.changes)}'>${esc(log.changes || '—')}</td></tr>`; }).join('') : `<tr><td colspan='7' class='py-8 text-center text-slate-500 dark:text-slate-400'>沒有符合條件的稽核紀錄。</td></tr>`}</tbody></table></div>`;
  }

  function renderSettings() {
    const user = currentUser();
    if (!user || user.role !== 'admin') return accessDenied('系統設定');
    const settings = state.settings;
    const counts = {
      expenses: state.expenses.length,
      projects: state.projects.length,
      users: state.users.length,
      notifications: state.notifications.length,
      auditLogs: state.auditLogs.length,
    };
    return `${pageHeader('系統設定', '示範版參數與本機資料狀態', `<button type='button' class='btn-secondary' data-action='download-backup'>${icon('download')}下載備份</button>`)}<div class='grid gap-4 xl:grid-cols-3'><form id='settings-form' class='card xl:col-span-2'><h2 class='text-sm font-semibold'>一般設定</h2><div class='mt-4 grid gap-4 sm:grid-cols-2'><div class='form-row'><label class='form-label' for='settings-company'>公司名稱</label><input class='input' id='settings-company' name='companyName' value='${esc(settings.companyName)}' required></div><div class='form-row'><label class='form-label' for='settings-threshold'>上層加簽門檻 (NT$)</label><input class='input' id='settings-threshold' name='approvalThreshold' type='number' min='0' step='1000' value='${esc(settings.approvalThreshold)}' required></div><div class='form-row'><label class='form-label' for='settings-tax'>預設稅率 (%)</label><input class='input' id='settings-tax' name='defaultTaxRate' type='number' min='0' max='100' step='0.1' value='${esc(settings.defaultTaxRate)}' required></div><div class='form-row'><label class='form-label' for='settings-cache'>儀表板快取 (秒)</label><input class='input' id='settings-cache' name='dashboardCacheSeconds' type='number' min='0' step='1' value='${esc(settings.dashboardCacheSeconds)}' required></div><div class='form-row'><label class='form-label' for='settings-retention'>備份保留天數</label><input class='input' id='settings-retention' name='backupRetention' type='number' min='1' step='1' value='${esc(settings.backupRetention)}' required></div></div><div class='form-row mt-4'><label class='form-label' for='settings-announcement'>公告</label><textarea class='textarea' id='settings-announcement' name='announcement'>${esc(settings.announcement)}</textarea></div><div class='mt-4 flex justify-end'><button type='submit' class='btn-primary'>儲存設定</button></div></form><div class='space-y-4'><div class='card'><h2 class='text-sm font-semibold'>本機資料</h2><dl class='mt-4 space-y-3 text-sm'><div class='flex justify-between gap-3'><dt class='text-slate-500 dark:text-slate-400'>核銷單</dt><dd>${counts.expenses}</dd></div><div class='flex justify-between gap-3'><dt class='text-slate-500 dark:text-slate-400'>專案</dt><dd>${counts.projects}</dd></div><div class='flex justify-between gap-3'><dt class='text-slate-500 dark:text-slate-400'>使用者</dt><dd>${counts.users}</dd></div><div class='flex justify-between gap-3'><dt class='text-slate-500 dark:text-slate-400'>通知</dt><dd>${counts.notifications}</dd></div><div class='flex justify-between gap-3'><dt class='text-slate-500 dark:text-slate-400'>稽核紀錄</dt><dd>${counts.auditLogs}</dd></div></dl><p class='mt-4 text-xs text-slate-500 dark:text-slate-400'>儲存鍵：${esc(STORAGE_KEY)}</p></div><div class='card'><h2 class='text-sm font-semibold'>危險操作</h2><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>重設會清除本機示範資料並恢復預設種子資料。</p><button type='button' class='btn-danger mt-4 w-full' data-action='reset-demo'>${icon('refresh')}重設示範資料</button></div></div></div>`;
  }

  function renderProfile() {
    const user = currentUser();
    return `${pageHeader('個人資料', '目前登入的示範帳號資訊')}<div class='grid gap-4 xl:grid-cols-3'><div class='card xl:col-span-2'><div class='flex flex-col gap-4 sm:flex-row sm:items-center'><span class='flex h-16 w-16 items-center justify-center rounded-3xl bg-brand-100 text-2xl font-bold text-brand-700 dark:bg-brand-900/50 dark:text-brand-200'>${esc(user.name.slice(0, 1))}</span><div><h2 class='text-xl font-bold'>${esc(user.name)}</h2><div class='mt-1 flex flex-wrap items-center gap-2'>${roleBadge(user.role)}<span class='badge-slate'>${esc(departmentName(user.department))}</span></div><p class='mt-1 text-sm text-slate-500 dark:text-slate-400'>${esc(user.title || '')}</p></div></div><dl class='mt-6 grid gap-4 border-t border-slate-200 pt-4 text-sm dark:border-slate-800 sm:grid-cols-2'><div><dt class='text-xs text-slate-500 dark:text-slate-400'>帳號</dt><dd class='mt-1 font-medium'>${esc(user.username)}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>員工編號</dt><dd class='mt-1'>${esc(user.employeeNo || '—')}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>Email</dt><dd class='mt-1'>${esc(user.email || '—')}</dd></div><div><dt class='text-xs text-slate-500 dark:text-slate-400'>TOTP</dt><dd class='mt-1'>${user.totp ? '已啟用' : '未啟用'}</dd></div></dl></div><div class='space-y-4'><div class='card'><h2 class='text-sm font-semibold'>偏好設定</h2><button type='button' class='btn-secondary mt-4 w-full' data-action='toggle-theme'>${icon('sun')}<span data-theme-label>深色模式</span></button><button type='button' class='btn-secondary mt-2 w-full' data-action='logout'>${icon('logout')}登出</button></div><div class='card'><h2 class='text-sm font-semibold'>示範資料</h2><p class='mt-2 text-sm text-slate-500 dark:text-slate-400'>您的操作會即時寫入 localStorage。若要回到預設狀態，請重設示範資料。</p><button type='button' class='btn-ghost mt-4 w-full' data-action='reset-demo'>${icon('refresh')}重設示範資料</button></div></div></div>`;
  }

  function renderMaster() {
    const user = currentUser();
    if (!canManageMaster(user)) return accessDenied('基礎資料');
    const departments = state.departments.map(function (department) {
      return `<tr><td class='font-medium'>${esc(department.code)}</td><td>${esc(department.name)}</td></tr>`;
    }).join('');
    const categories = state.categories.map(function (category) {
      return `<tr><td class='font-medium'>${esc(category.code)}</td><td>${esc(category.name)}</td></tr>`;
    }).join('');
    const projectTypes = state.projectTypes.map(function (projectType) {
      return `<tr><td class='font-medium'>${esc(projectType.code)}</td><td>${esc(projectType.name)}</td></tr>`;
    }).join('');
    return `${pageHeader('基礎資料', '示範版部門、費用類別與專案類型', `<a class='btn-secondary' href='#/projects'>${icon('projects')}專案列表</a>`)}<div class='alert-info mb-4'>${icon('settings')}<div class='flex-1'>此示範版基礎資料為唯讀，專案內容於專案頁面檢視。</div></div><div class='grid gap-4 xl:grid-cols-3'><div class='card'><h2 class='text-sm font-semibold'>部門</h2><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>代碼</th><th>名稱</th></tr></thead><tbody>${departments}</tbody></table></div></div><div class='card'><h2 class='text-sm font-semibold'>費用類別</h2><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>代碼</th><th>名稱</th></tr></thead><tbody>${categories}</tbody></table></div></div><div class='card'><h2 class='text-sm font-semibold'>專案類型</h2><div class='mt-4 overflow-x-auto'><table class='table'><thead><tr><th>代碼</th><th>名稱</th></tr></thead><tbody>${projectTypes}</tbody></table></div></div></div>`;
  }

  const CHART_COLORS = ['#1b39b5', '#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#14b8a6', '#64748b'];

  function chartTextColor() {
    return document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569';
  }

  function chartGridColor() {
    return document.documentElement.classList.contains('dark') ? 'rgba(51,65,85,0.7)' : 'rgba(226,232,240,0.9)';
  }

  function chartOptions(showScales) {
    const color = chartTextColor();
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: color, boxWidth: 12, usePointStyle: true },
        },
      },
    };
    if (showScales) {
      options.scales = {
        x: { ticks: { color: color }, grid: { display: false } },
        y: {
          beginAtZero: true,
          ticks: { color: color, callback: function (value) { return money(value); } },
          grid: { color: chartGridColor() },
        },
      };
    }
    return options;
  }

  function createChart(id, config) {
    const canvas = document.getElementById(id);
    if (!canvas || !window.Chart) return;
    if (chartInstances[id]) chartInstances[id].destroy();
    chartInstances[id] = new window.Chart(canvas, config);
  }

  function drawDashboardCharts() {
    const data = dashboardData();
    createChart('dash-trend', {
      type: 'line',
      data: {
        labels: data.trend.labels,
        datasets: [{
          label: '核准金額',
          data: data.trend.values,
          borderColor: '#1b39b5',
          backgroundColor: 'rgba(27,57,181,0.12)',
          fill: true,
          tension: 0.35,
          pointRadius: 2,
          pointHoverRadius: 4,
        }],
      },
      options: chartOptions(true),
    });
    createChart('dash-department', {
      type: 'doughnut',
      data: {
        labels: data.deptShare.map(function (item) { return item.label; }),
        datasets: [{ data: data.deptShare.map(function (item) { return item.value; }), backgroundColor: CHART_COLORS, borderWidth: 0 }],
      },
      options: chartOptions(false),
    });
    createChart('dash-projects', {
      type: 'bar',
      data: {
        labels: data.projectBars.map(function (item) { return item.code; }),
        datasets: [
          { label: '預算', data: data.projectBars.map(function (item) { return item.budget; }), backgroundColor: 'rgba(148,163,184,0.55)', borderRadius: 4 },
          { label: '已使用', data: data.projectBars.map(function (item) { return item.spent; }), backgroundColor: '#1b39b5', borderRadius: 4 },
        ],
      },
      options: chartOptions(true),
    });
    createChart('dash-category', {
      type: 'doughnut',
      data: {
        labels: data.categoryShare.map(function (item) { return item.label; }),
        datasets: [{ data: data.categoryShare.map(function (item) { return item.value; }), backgroundColor: CHART_COLORS, borderWidth: 0 }],
      },
      options: chartOptions(false),
    });
  }

  function drawReportCharts() {
    const data = reportData();
    createChart('report-trend', {
      type: 'line',
      data: {
        labels: data.trend.labels,
        datasets: [{
          label: '核准金額',
          data: data.trend.values,
          borderColor: '#0ea5e9',
          backgroundColor: 'rgba(14,165,233,0.12)',
          fill: true,
          tension: 0.35,
          pointRadius: 2,
        }],
      },
      options: chartOptions(true),
    });
    createChart('report-department', {
      type: 'doughnut',
      data: {
        labels: data.deptRows.map(function (item) { return item.label; }),
        datasets: [{ data: data.deptRows.map(function (item) { return item.value; }), backgroundColor: CHART_COLORS, borderWidth: 0 }],
      },
      options: chartOptions(false),
    });
    createChart('report-category', {
      type: 'doughnut',
      data: {
        labels: data.catRows.map(function (item) { return item.label; }),
        datasets: [{ data: data.catRows.map(function (item) { return item.value; }), backgroundColor: CHART_COLORS, borderWidth: 0 }],
      },
      options: chartOptions(false),
    });
  }

  function currentTheme() {
    return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }

  function initTheme() {
    let stored = null;
    try {
      stored = localStorage.getItem(THEME_KEY);
    } catch (error) {
      stored = null;
    }
    if (!stored) {
      stored = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    applyTheme(stored);
  }

  function updateThemeLabels() {
    const label = currentTheme() === 'dark' ? '淺色模式' : '深色模式';
    document.querySelectorAll('[data-theme-label]').forEach(function (node) {
      node.textContent = label;
    });
  }

  function toggleTheme() {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch (error) {
      console.warn('無法儲存主題設定。', error);
    }
    applyTheme(next);
    updateThemeLabels();
    const route = getRoute();
    if (route.name === 'dashboard' || route.name === 'reports') render();
  }

  function toast(message, level) {
    const root = document.getElementById('toast-root');
    if (!root) return;
    const element = document.createElement('div');
    element.className = 'demo-toast ' + (level === 'error' ? 'alert-error' : level === 'warning' ? 'alert-warning' : level === 'info' ? 'alert-info' : 'alert-success');
    element.innerHTML = `<div class='flex items-start gap-2'>${icon(level === 'error' || level === 'warning' ? 'alert' : 'check')}<span class='flex-1'>${esc(message)}</span><button type='button' class='text-current opacity-70' data-action='dismiss-toast' aria-label='關閉'>×</button></div>`;
    root.appendChild(element);
    window.setTimeout(function () {
      element.classList.add('demo-toast-leave');
      window.setTimeout(function () {
        element.remove();
      }, 180);
    }, 3600);
  }

  function login(username, password) {
    const account = DEMO_ACCOUNTS.find(function (item) {
      return item.username === String(username || '').trim() && item.password === password;
    });
    if (!account) {
      toast('帳號或密碼錯誤，請使用示範帳號登入。', 'error');
      return;
    }
    try {
      localStorage.setItem(SESSION_KEY, account.username);
    } catch (error) {
      console.warn('無法儲存登入狀態。', error);
    }
    addAudit('login', 'accounts.User', account.username, '登入成功', account.username);
    saveState();
    navigate('dashboard');
    toast('歡迎回來，' + account.name, 'success');
  }

  function logout() {
    const user = currentUser();
    if (user) {
      addAudit('logout', 'accounts.User', user.username, '登出', user.username);
      saveState();
    }
    try {
      localStorage.removeItem(SESSION_KEY);
    } catch (error) {
      console.warn('無法清除登入狀態。', error);
    }
    document.body.classList.remove('demo-sidebar-open');
    navigate('login');
    toast('已登出。', 'info');
  }

  function resetDemo() {
    if (!window.confirm('確定要重設所有示範資料嗎？此操作會清除本機核銷單、通知與設定。')) return;
    try {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(SESSION_KEY);
    } catch (error) {
      console.warn('無法清除示範資料。', error);
    }
    state = seedState();
    saveState();
    navigate('login');
    toast('示範資料已重設。', 'success');
  }

  function transitionExpense(id, action, comment) {
    const user = currentUser();
    const expense = getExpense(id);
    if (!user || !expense) {
      toast('找不到核銷單。', 'error');
      return false;
    }
    if (!canAct(user, expense, action)) {
      toast('您沒有執行此動作的權限。', 'error');
      return false;
    }
    const cleanComment = String(comment || '').trim();
    if ((action === 'return' || action === 'reject') && !cleanComment) {
      toast('退回或駁回必須填寫意見。', 'error');
      return false;
    }
    if (action === 'submit' && expenseTotal(expense) <= 0) {
      toast('核銷單尚無金額，無法送審。', 'error');
      return false;
    }
    const fromStatus = expense.status;
    const target = action === 'manager_approve'
      ? (expenseTotal(expense) > Number(state.settings.approvalThreshold) ? 'exec_review' : 'finance_review')
      : ACTION_TARGET[action];
    if (!target) {
      toast('此動作無法執行。', 'error');
      return false;
    }
    expense.status = target;
    expense.version = (expense.version || 1) + 1;
    expense.updatedAt = nowISO();
    if (action === 'submit') expense.submittedAt = nowISO();
    if (action === 'finance_approve') expense.approvedAt = nowISO();
    if (action === 'pay') expense.paidAt = nowISO();
    addApprovalLog(expense, action, fromStatus, target, cleanComment, user.username);
    addAudit('update', 'expenses.Expense', expense.number, 'status: ' + fromStatus + ' -> ' + target);
    notifyAfterAction(expense, action, user, cleanComment, target);
    saveState();
    toast(ACTION_LABELS[action] + '完成。', 'success');
    return true;
  }

  function handleExpenseAction(id, action) {
    let comment = '';
    if (action === 'return' || action === 'reject') {
      const input = window.prompt('請輸入' + ACTION_LABELS[action] + '意見：');
      if (input === null) return;
      comment = input.trim();
      if (!comment) {
        toast('請填寫意見。', 'error');
        return;
      }
    }
    const ok = transitionExpense(id, action, comment);
    if (ok) render();
  }

  function collectInvoiceFromForm(form) {
    const rows = Array.prototype.slice.call(form.querySelectorAll('[data-item-row]'));
    if (!rows.length) {
      toast('請至少新增一個品項。', 'error');
      return null;
    }
    const items = [];
    for (let index = 0; index < rows.length; index += 1) {
      const row = rows[index];
      const value = function (field) {
        const element = row.querySelector('[data-field=' + field + ']');
        return element ? element.value : '';
      };
      const name = value('itemName').trim();
      const quantity = Number(value('itemQuantity'));
      const unitPrice = Number(value('itemUnitPrice'));
      if (!name) {
        toast('請填寫品項名稱。', 'error');
        return null;
      }
      if (!Number.isFinite(quantity) || quantity <= 0) {
        toast('品項數量必須大於 0。', 'error');
        return null;
      }
      if (!Number.isFinite(unitPrice) || unitPrice < 0) {
        toast('品項單價不可小於 0。', 'error');
        return null;
      }
      items.push({
        id: 0,
        name: name,
        spec: value('itemSpec').trim(),
        quantity: quantity,
        unitPrice: unitPrice,
        categoryCode: value('itemCategory') || 'OTHER',
        note: value('itemNote').trim(),
      });
    }
    const invoiceId = uid('invoice');
    items.forEach(function (item, index) {
      item.id = invoiceId * 10 + index + 1;
    });
    return {
      id: invoiceId,
      invoiceType: form.elements.invoiceType.value,
      invoiceNo: form.elements.invoiceNo.value.trim(),
      issueDate: form.elements.issueDate.value,
      sellerName: form.elements.sellerName.value.trim(),
      sellerTaxId: form.elements.sellerTaxId.value.trim(),
      buyerTaxId: BUYER_TAX_ID,
      taxRate: Number(form.elements.taxRate.value) || 0,
      note: form.elements.invoiceNote.value.trim(),
      items: items,
    };
  }

  function saveExpenseForm(event) {
    const form = event.target;
    const submitMode = event.submitter && event.submitter.dataset.submitMode === 'submit' ? 'submit' : 'draft';
    const invoice = collectInvoiceFromForm(form);
    if (!invoice) return;
    const id = form.dataset.id ? Number(form.dataset.id) : null;
    const user = currentUser();
    if (!user) {
      toast('登入狀態已失效。', 'error');
      return;
    }
    const applyDate = form.elements.applyDate.value;
    const projectCode = form.elements.projectCode.value;
    const reason = form.elements.reason.value.trim();
    if (!applyDate || !projectCode || !reason) {
      toast('請填寫申請日期、專案與事由。', 'error');
      return;
    }
    const project = getProject(projectCode);
    if (!project) {
      toast('找不到專案。', 'error');
      return;
    }
    let expense = id ? getExpense(id) : null;
    if (id && (!expense || !canEditExpense(user, expense))) {
      toast('您沒有編輯此核銷單的權限。', 'error');
      return;
    }
    if (expense) {
      expense.applyDate = applyDate;
      expense.projectCode = projectCode;
      expense.projectTypeCode = project.projectType;
      expense.reason = reason;
      expense.invoices = [invoice];
      expense.updatedAt = nowISO();
      expense.version = (expense.version || 1) + 1;
      addApprovalLog(expense, 'update', expense.status, expense.status, '更新核銷內容', user.username);
      addAudit('update', 'expenses.Expense', expense.number, '更新核銷內容');
    } else {
      const newId = uid('expense');
      expense = {
        id: newId,
        number: 'EX-2026-' + String(newId).padStart(4, '0'),
        applicant: user.username,
        department: user.department,
        projectCode: projectCode,
        projectTypeCode: project.projectType,
        applyDate: applyDate,
        reason: reason,
        status: 'draft',
        version: 1,
        submittedAt: null,
        approvedAt: null,
        paidAt: null,
        createdAt: nowISO(),
        updatedAt: nowISO(),
        invoices: [invoice],
        logs: [{
          id: uid('log'),
          actor: user.username,
          action: 'create',
          fromStatus: '',
          toStatus: 'draft',
          comment: '建立核銷單',
          createdAt: nowISO(),
        }],
      };
      state.expenses.unshift(expense);
      addAudit('create', 'expenses.Expense', expense.number, 'status: draft');
    }
    saveState();
    if (submitMode === 'submit') transitionExpense(expense.id, 'submit', '');
    navigate('expenses/' + expense.id);
    if (submitMode !== 'submit') toast(id ? '核銷單已更新。' : '草稿已建立。', 'success');
  }

  function recalcExpenseForm() {
    const form = document.getElementById('expense-form');
    if (!form) return;
    const rows = Array.prototype.slice.call(form.querySelectorAll('[data-item-row]'));
    let untaxed = 0;
    rows.forEach(function (row) {
      const quantityElement = row.querySelector('[data-field=itemQuantity]');
      const unitPriceElement = row.querySelector('[data-field=itemUnitPrice]');
      const quantity = Number(quantityElement ? quantityElement.value : 0);
      const unitPrice = Number(unitPriceElement ? unitPriceElement.value : 0);
      const subtotal = round2((Number.isFinite(quantity) ? quantity : 0) * (Number.isFinite(unitPrice) ? unitPrice : 0));
      untaxed += subtotal;
      const cell = row.querySelector('[data-subtotal]');
      if (cell) cell.textContent = 'NT$ ' + moneyExact(subtotal);
    });
    const taxRateElement = form.elements.taxRate;
    const taxRate = Number(taxRateElement ? taxRateElement.value : 0) || 0;
    const tax = round2(untaxed * taxRate / 100);
    const total = round2(untaxed + tax);
    const subtotalNode = document.getElementById('form-subtotal');
    const taxNode = document.getElementById('form-tax');
    const totalNode = document.getElementById('form-total');
    if (subtotalNode) subtotalNode.textContent = 'NT$ ' + moneyExact(untaxed);
    if (taxNode) taxNode.textContent = 'NT$ ' + moneyExact(tax);
    if (totalNode) totalNode.textContent = 'NT$ ' + moneyExact(total);
  }

  function addItemRow() {
    const tbody = document.getElementById('invoice-items');
    if (!tbody) return;
    uiState.itemRowSeq += 1;
    tbody.insertAdjacentHTML('beforeend', itemRowHtml(blankItem(), uiState.itemRowSeq));
    recalcExpenseForm();
  }

  function removeItemRow(button) {
    const row = button.closest('[data-item-row]');
    if (!row) return;
    const tbody = row.parentElement;
    if (tbody.querySelectorAll('[data-item-row]').length <= 1) {
      toast('至少需要保留一個品項。', 'warning');
      return;
    }
    row.remove();
    recalcExpenseForm();
  }

  function markNotificationRead(id) {
    const user = currentUser();
    if (!user) return false;
    const notification = state.notifications.find(function (item) {
      return item.id === Number(id) && item.to === user.username;
    });
    if (!notification) return false;
    if (!notification.isRead) {
      notification.isRead = true;
      saveState();
    }
    return true;
  }

  function markAllNotifications() {
    const user = currentUser();
    if (!user) return;
    let changed = false;
    state.notifications.forEach(function (notification) {
      if (notification.to === user.username && !notification.isRead) {
        notification.isRead = true;
        changed = true;
      }
    });
    if (changed) saveState();
    render();
    toast('所有通知已標為已讀。', 'success');
  }

  function saveSettings(event) {
    const form = event.target;
    state.settings.companyName = form.elements.companyName.value.trim();
    state.settings.approvalThreshold = Number(form.elements.approvalThreshold.value) || 0;
    state.settings.defaultTaxRate = Number(form.elements.defaultTaxRate.value) || 0;
    state.settings.dashboardCacheSeconds = Number(form.elements.dashboardCacheSeconds.value) || 0;
    state.settings.backupRetention = Number(form.elements.backupRetention.value) || 1;
    state.settings.announcement = form.elements.announcement.value.trim();
    addAudit('update', 'core.SystemSetting', '系統設定', '更新系統設定');
    saveState();
    render();
    toast('系統設定已儲存。', 'success');
  }

  function syncExpenseFiltersFromForm() {
    const form = document.getElementById('expense-filter-form');
    if (!form) return;
    const filters = uiState.expenseFilters;
    filters.q = form.elements.q.value.trim();
    filters.status = form.elements.status.value;
    filters.department = form.elements.department.value;
    filters.project = form.elements.project.value;
    filters.category = form.elements.category.value;
    filters.applicant = form.elements.applicant.value;
    filters.dateFrom = form.elements.dateFrom.value;
    filters.dateTo = form.elements.dateTo.value;
    filters.amountMin = form.elements.amountMin.value;
    filters.amountMax = form.elements.amountMax.value;
  }

  function syncProjectFiltersFromForm() {
    const form = document.getElementById('project-filter-form');
    if (!form) return;
    uiState.projectFilters.q = form.elements.q.value.trim();
    uiState.projectFilters.status = form.elements.status.value;
  }

  function syncReportFiltersFromForm() {
    const form = document.getElementById('report-filter-form');
    if (!form) return;
    uiState.reportFilters.year = form.elements.year.value;
    uiState.reportFilters.quarter = form.elements.quarter.value;
    uiState.reportFilters.month = form.elements.month.value;
  }

  function syncAuditFiltersFromForm() {
    const form = document.getElementById('audit-filter-form');
    if (!form) return;
    uiState.auditFilters.q = form.elements.q.value.trim();
    uiState.auditFilters.action = form.elements.action.value;
  }

  function resetExpenseFilters() {
    uiState.expenseFilters = {
      mode: '',
      q: '',
      status: '',
      department: '',
      project: '',
      category: '',
      applicant: '',
      dateFrom: '',
      dateTo: '',
      amountMin: '',
      amountMax: '',
    };
    render();
  }

  function resetProjectFilters() {
    uiState.projectFilters = { q: '', status: '' };
    render();
  }

  function resetReportFilters() {
    uiState.reportFilters = { year: String(new Date().getFullYear()), quarter: '', month: '' };
    render();
  }

  function resetAuditFilters() {
    uiState.auditFilters = { q: '', action: '' };
    render();
  }

  function downloadFile(filename, content, mime) {
    const blob = new Blob([content], { type: mime || 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 0);
  }

  function csvCell(value) {
    const quote = String.fromCharCode(34);
    return quote + String(value === null || value === undefined ? '' : value).replace(new RegExp(quote, 'g'), quote + quote) + quote;
  }

  function downloadCsv(filename, headers, rows) {
    const lines = [headers].concat(rows).map(function (row) {
      return row.map(csvCell).join(',');
    }).join('\r\n');
    downloadFile(filename, '\ufeff' + lines, 'text/csv;charset=utf-8');
  }

  function exportExpensesCsv() {
    const rows = filteredExpenses();
    downloadCsv('expenses-' + todayISO() + '.csv', ['單號', '申請人', '部門', '專案', '事由', '金額', '狀態', '申請日'], rows.map(function (expense) {
      const applicant = getUser(expense.applicant);
      const project = getProject(expense.projectCode);
      return [
        expense.number,
        applicant ? applicant.name : expense.applicant,
        departmentName(expense.department),
        project ? project.name : expense.projectCode,
        expense.reason,
        expenseTotal(expense),
        statusMeta(expense.status).label,
        expense.applyDate,
      ];
    }));
    addAudit('export', 'expenses.Expense', '核銷單列表', 'format: csv');
    saveState();
    toast('核銷單 CSV 已匯出。', 'success');
  }

  function exportReportCsv() {
    const data = reportData();
    downloadCsv('report-' + todayISO() + '.csv', ['單號', '申請人', '部門', '專案', '類別', '金額', '狀態', '申請日'], data.rows.map(function (expense) {
      const applicant = getUser(expense.applicant);
      const project = getProject(expense.projectCode);
      const categories = expense.invoices.map(function (invoice) {
        return invoice.items.map(function (item) { return categoryName(item.categoryCode); }).join(' / ');
      }).join(' / ');
      return [
        expense.number,
        applicant ? applicant.name : expense.applicant,
        departmentName(expense.department),
        project ? project.name : expense.projectCode,
        categories,
        expenseTotal(expense),
        statusMeta(expense.status).label,
        expense.applyDate,
      ];
    }));
    addAudit('export', 'expenses.Expense', '費用報表', 'format: csv');
    saveState();
    toast('報表 CSV 已匯出。', 'success');
  }

  function exportAuditCsv() {
    const rows = filteredAuditLogs();
    downloadCsv('audit-' + todayISO() + '.csv', ['時間', '使用者', '動作', '模型', '物件', 'IP', '變更'], rows.map(function (log) {
      return [formatDateTime(log.createdAt), log.username, AUDIT_ACTION_LABELS[log.action] || log.action, log.modelLabel, log.objectRepr, log.ip, log.changes];
    }));
    addAudit('export', 'audit.AuditLog', '稽核紀錄', 'format: csv');
    saveState();
    toast('稽核 CSV 已匯出。', 'success');
  }

  function downloadBackup() {
    downloadFile('zhiqi-frontend-backup-' + todayISO() + '.json', JSON.stringify(state, null, 2), 'application/json;charset=utf-8');
    addAudit('backup', 'core.SystemSetting', 'localStorage', '下載 JSON 備份');
    saveState();
    toast('JSON 備份已下載。', 'success');
  }

  document.addEventListener('click', function (event) {
    const trigger = event.target.closest('[data-action]');
    if (!trigger) return;
    const action = trigger.dataset.action;
    if (action === 'toggle-sidebar') {
      document.body.classList.toggle('demo-sidebar-open');
      return;
    }
    if (action === 'close-sidebar') {
      document.body.classList.remove('demo-sidebar-open');
      return;
    }
    if (action === 'toggle-theme') {
      toggleTheme();
      return;
    }
    if (action === 'logout') {
      logout();
      return;
    }
    if (action === 'reset-demo') {
      resetDemo();
      return;
    }
    if (action === 'fill-login') {
      const usernameInput = document.getElementById('login-username');
      const passwordInput = document.getElementById('login-password');
      if (usernameInput && passwordInput) {
        usernameInput.value = trigger.dataset.username || '';
        passwordInput.value = trigger.dataset.password || '';
        passwordInput.focus();
      }
      return;
    }
    if (action === 'expense-action') {
      handleExpenseAction(Number(trigger.dataset.id), trigger.dataset.nextAction);
      return;
    }
    if (action === 'add-item') {
      addItemRow();
      return;
    }
    if (action === 'remove-item') {
      removeItemRow(trigger);
      return;
    }
    if (action === 'read-notification') {
      markNotificationRead(Number(trigger.dataset.id));
      if (trigger.tagName === 'BUTTON') render();
      return;
    }
    if (action === 'mark-all-notifications') {
      markAllNotifications();
      return;
    }
    if (action === 'reset-expense-filters') {
      resetExpenseFilters();
      return;
    }
    if (action === 'reset-project-filters') {
      resetProjectFilters();
      return;
    }
    if (action === 'reset-report-filters') {
      resetReportFilters();
      return;
    }
    if (action === 'reset-audit-filters') {
      resetAuditFilters();
      return;
    }
    if (action === 'export-expenses') {
      exportExpensesCsv();
      return;
    }
    if (action === 'export-report') {
      exportReportCsv();
      return;
    }
    if (action === 'export-audit') {
      exportAuditCsv();
      return;
    }
    if (action === 'download-backup') {
      downloadBackup();
      return;
    }
    if (action === 'dismiss-toast') {
      const toastElement = trigger.closest('.demo-toast');
      if (toastElement) toastElement.remove();
    }
  });

  document.addEventListener('submit', function (event) {
    if (event.target.id === 'login-form') {
      event.preventDefault();
      const data = new FormData(event.target);
      login(data.get('username'), data.get('password'));
      return;
    }
    if (event.target.id === 'expense-form') {
      event.preventDefault();
      saveExpenseForm(event);
      return;
    }
    if (event.target.id === 'settings-form') {
      event.preventDefault();
      saveSettings(event);
    }
  });

  document.addEventListener('change', function (event) {
    if (event.target.closest('#expense-filter-form')) {
      syncExpenseFiltersFromForm();
      render();
      return;
    }
    if (event.target.closest('#project-filter-form')) {
      syncProjectFiltersFromForm();
      render();
      return;
    }
    if (event.target.closest('#report-filter-form')) {
      syncReportFiltersFromForm();
      render();
      return;
    }
    if (event.target.closest('#audit-filter-form')) {
      syncAuditFiltersFromForm();
      render();
      return;
    }
    if (event.target.closest('#expense-form')) recalcExpenseForm();
  });

  document.addEventListener('input', function (event) {
    if (event.target.closest('#expense-form')) recalcExpenseForm();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Enter') return;
    const form = event.target.closest('#expense-filter-form, #project-filter-form, #audit-filter-form');
    if (!form) return;
    event.preventDefault();
    if (form.id === 'expense-filter-form') syncExpenseFiltersFromForm();
    if (form.id === 'project-filter-form') syncProjectFiltersFromForm();
    if (form.id === 'audit-filter-form') syncAuditFiltersFromForm();
    render();
  });

  window.addEventListener('hashchange', render);

  function init() {
    initTheme();
    state = loadState();
    render();
  }

  init();
})();
