create table if not exists customers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text,
  phone text,
  company text,
  created_at timestamptz default now()
);

create table if not exists devices (
  id uuid primary key default gen_random_uuid(),
  serial_number text not null unique,
  model text,
  product_type text,
  customer_id uuid references customers(id) on delete set null,
  created_at timestamptz default now()
);

create table if not exists tickets (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  status text default 'Open' check (
    status in ('Open', 'In Progress', 'Waiting on Customer', 'Resolved', 'Closed')
  ),
  priority text default 'Medium' check (priority in ('Low', 'Medium', 'High', 'Critical')),
  customer_id uuid references customers(id) on delete set null,
  device_id uuid references devices(id) on delete set null,
  assigned_user_id uuid,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists ticket_notes (
  id uuid primary key default gen_random_uuid(),
  ticket_id uuid references tickets(id) on delete cascade,
  note_text text not null,
  created_by text,
  created_at timestamptz default now()
);

create table if not exists ticket_history (
  id uuid primary key default gen_random_uuid(),
  ticket_id uuid references tickets(id) on delete cascade,
  old_status text,
  new_status text,
  changed_by text,
  changed_at timestamptz default now()
);

create table if not exists rmas (
  id uuid primary key default gen_random_uuid(),
  ticket_id uuid references tickets(id) on delete cascade,
  rma_number text not null unique,
  serial_number text,
  shipping_status text default 'Pending',
  resolution_status text default 'Pending',
  created_at timestamptz default now(),
  closed_at timestamptz
);

create index if not exists devices_customer_id_idx on devices(customer_id);
create index if not exists tickets_customer_id_idx on tickets(customer_id);
create index if not exists tickets_device_id_idx on tickets(device_id);
create index if not exists ticket_notes_ticket_id_idx on ticket_notes(ticket_id);
create index if not exists ticket_history_ticket_id_idx on ticket_history(ticket_id);
create index if not exists rmas_ticket_id_idx on rmas(ticket_id);

alter table customers enable row level security;
alter table devices enable row level security;
alter table tickets enable row level security;
alter table ticket_notes enable row level security;
alter table ticket_history enable row level security;
alter table rmas enable row level security;

insert into customers (id, name, email, phone, company, created_at)
values
  (
    '00000000-0000-4000-8000-000000000001',
    'Acme Operations',
    'ops@acme.example',
    '555-0101',
    'Acme Inc',
    timezone('utc', now()) - interval '6 days'
  ),
  (
    '00000000-0000-4000-8000-000000000002',
    'Northwind Support',
    'support@northwind.example',
    '555-0130',
    'Northwind Traders',
    timezone('utc', now()) - interval '4 days'
  ),
  (
    '00000000-0000-4000-8000-000000000003',
    'Contoso Field Team',
    'field@contoso.example',
    '555-0177',
    'Contoso',
    timezone('utc', now()) - interval '2 days'
  )
on conflict (id) do nothing;

insert into devices (id, serial_number, model, product_type, customer_id, created_at)
values
  (
    '00000000-0000-4000-8000-000000000101',
    'RTR-ACME-1001',
    'EdgeRouter X',
    'Router',
    '00000000-0000-4000-8000-000000000001',
    timezone('utc', now()) - interval '5 days'
  ),
  (
    '00000000-0000-4000-8000-000000000102',
    'LAP-NW-2044',
    'Latitude 7440',
    'Laptop',
    '00000000-0000-4000-8000-000000000002',
    timezone('utc', now()) - interval '3 days'
  ),
  (
    '00000000-0000-4000-8000-000000000103',
    'AP-CON-3319',
    'UniFi U6 Pro',
    'Access Point',
    '00000000-0000-4000-8000-000000000003',
    timezone('utc', now()) - interval '1 day'
  )
on conflict (id) do nothing;

insert into tickets (
  id,
  title,
  description,
  status,
  priority,
  customer_id,
  device_id,
  assigned_user_id,
  created_at
)
values
  (
    '00000000-0000-4000-8000-000000000201',
    'Router drops WAN during backups',
    'WAN interface flaps when nightly backup traffic spikes.',
    'Open',
    'Critical',
    '00000000-0000-4000-8000-000000000001',
    '00000000-0000-4000-8000-000000000101',
    null,
    timezone('utc', now()) - interval '2 days'
  ),
  (
    '00000000-0000-4000-8000-000000000202',
    'Laptop battery swelling',
    'User reports trackpad lifting and chassis gap near battery bay.',
    'In Progress',
    'High',
    '00000000-0000-4000-8000-000000000002',
    '00000000-0000-4000-8000-000000000102',
    null,
    timezone('utc', now()) - interval '1 day'
  ),
  (
    '00000000-0000-4000-8000-000000000203',
    'Conference room AP replaced',
    'Intermittent Wi-Fi resolved after AP swap and channel plan update.',
    'Closed',
    'Medium',
    '00000000-0000-4000-8000-000000000003',
    '00000000-0000-4000-8000-000000000103',
    null,
    timezone('utc', now()) - interval '12 hours'
  )
on conflict (id) do nothing;

insert into ticket_notes (ticket_id, note_text, created_by, created_at)
select
  '00000000-0000-4000-8000-000000000201',
  'Observed WAN drops line up with backup window. Asked customer for modem logs.',
  'Agent',
  timezone('utc', now()) - interval '36 hours'
where not exists (
  select 1 from ticket_notes where ticket_id = '00000000-0000-4000-8000-000000000201'
)
union all
select
  '00000000-0000-4000-8000-000000000202',
  'Advised customer to stop using laptop and start RMA path for battery safety.',
  'Agent',
  timezone('utc', now()) - interval '18 hours'
where not exists (
  select 1 from ticket_notes where ticket_id = '00000000-0000-4000-8000-000000000202'
)
union all
select
  '00000000-0000-4000-8000-000000000203',
  'Replacement AP installed. RSSI and roaming tests passed.',
  'Agent',
  timezone('utc', now()) - interval '8 hours'
where not exists (
  select 1 from ticket_notes where ticket_id = '00000000-0000-4000-8000-000000000203'
);

insert into ticket_history (ticket_id, old_status, new_status, changed_by, changed_at)
select
  '00000000-0000-4000-8000-000000000201',
  null,
  'Open',
  'Agent',
  timezone('utc', now()) - interval '2 days'
where not exists (
  select 1 from ticket_history where ticket_id = '00000000-0000-4000-8000-000000000201'
)
union all
select
  '00000000-0000-4000-8000-000000000202',
  'Open',
  'In Progress',
  'Agent',
  timezone('utc', now()) - interval '16 hours'
where not exists (
  select 1 from ticket_history where ticket_id = '00000000-0000-4000-8000-000000000202'
)
union all
select
  '00000000-0000-4000-8000-000000000203',
  'In Progress',
  'Closed',
  'Agent',
  timezone('utc', now()) - interval '8 hours'
where not exists (
  select 1 from ticket_history where ticket_id = '00000000-0000-4000-8000-000000000203'
);

insert into rmas (id, ticket_id, rma_number, serial_number, shipping_status, resolution_status, created_at)
values
  (
    '00000000-0000-4000-8000-000000000301',
    '00000000-0000-4000-8000-000000000202',
    'RMA-2026-1001',
    'LAP-NW-2044',
    'Label Sent',
    'Pending',
    timezone('utc', now()) - interval '12 hours'
  )
on conflict (id) do nothing;
