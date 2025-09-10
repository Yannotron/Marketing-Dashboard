alter table posts enable row level security;
alter table insights enable row level security;

create policy "read posts" on posts for select using (true);
create policy "read insights" on insights for select using (true);

