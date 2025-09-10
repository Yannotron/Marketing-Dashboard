-- Optional seed data for development only
insert into posts (id, source, title, url, author, score, num_comments, created_utc)
values ('dev-1', 'reddit', 'Hello World', 'https://example.com', 'dev', 1, 0, now())
on conflict (id) do update set title = excluded.title;


