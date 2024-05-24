-- migrate:up

INSERT INTO api_data.review (equipment_id, "text", grade)
SELECT
    (SELECT id FROM api_data.equipment ORDER BY random() LIMIT 1) AS equipment_id,
    'Review_' || chr(trunc(65 + random() * 26)::int) || chr(trunc(65 + random() * 26)::int) || '_' || row_number() OVER () || '_' || uuid_generate_v4() AS text,
    trunc(random() * 5 + 1)::int AS grade
FROM
    generate_series(1, 100000);



-- migrate:down
