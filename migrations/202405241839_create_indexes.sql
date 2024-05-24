-- migrate:up
create extension if not exists pg_trgm;
create index review_text_gin_idx on api_data.review using gin("text" gin_trgm_ops);

create index review_grade_btree_idx on api_data.review using btree(grade);

-- migrate:down
