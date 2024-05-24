-- migrate:up

create schema api_data;

create extension if not exists "uuid-ossp";

create table api_data.equipment
(
	id uuid primary key default uuid_generate_v4(),
	category text,
	name text,
	"SIZE" int
);


CREATE TABLE api_data.company
(
    id uuid primary key default uuid_generate_v4(),
	title text,
	phone text check(length(phone) < 20),
	adress text
);


create table api_data.equipment_to_company
(
	equipment_id uuid references api_data.equipment,
	company_id uuid references api_data.company,
	primary key(equipment_id, company_id)
);



create table api_data.review
(
	id uuid primary key default uuid_generate_v4(),
	equipment_id uuid references api_data.equipment,
	"text" text,
	grade int
);


INSERT INTO api_data.equipment (category, name, "SIZE") VALUES 
('Laptop', 'Dell XPS 13', 13),
('Smartphone', 'iPhone 12', 6),
('Tablet', 'iPad Pro', 11),
('Monitor', 'Dell UltraSharp U2719D', 27),
('Printer', 'HP LaserJet Pro M404dn', NULL);

INSERT INTO api_data.company (title, phone, adress) VALUES 
('ABC Electronics', '123-456-7890', '123 Main St, City'),
('XYZ Technologies', '456-789-0123', '456 Oak Ave, Town'),
('Tech Solutions Inc.', '789-012-3456', '789 Elm St, Village'),
('Global Gadgets Ltd.', '321-654-0987', '321 Maple St, County');

INSERT INTO api_data.equipment_to_company (equipment_id, company_id) VALUES 
((SELECT id FROM api_data.equipment WHERE name = 'Dell XPS 13'), (SELECT id FROM api_data.company WHERE title = 'ABC Electronics')),
((SELECT id FROM api_data.equipment WHERE name = 'Dell XPS 13'), (SELECT id FROM api_data.company WHERE title = 'XYZ Technologies')),
((SELECT id FROM api_data.equipment WHERE name = 'iPhone 12'), (SELECT id FROM api_data.company WHERE title = 'XYZ Technologies')),
((SELECT id FROM api_data.equipment WHERE name = 'iPad Pro'), (SELECT id FROM api_data.company WHERE title = 'Tech Solutions Inc.')),
((SELECT id FROM api_data.equipment WHERE name = 'Dell UltraSharp U2719D'), (SELECT id FROM api_data.company WHERE title = 'Global Gadgets Ltd.')),
((SELECT id FROM api_data.equipment WHERE name = 'HP LaserJet Pro M404dn'), (SELECT id FROM api_data.company WHERE title = 'ABC Electronics'));

INSERT INTO api_data.review (equipment_id, "text", grade) VALUES 
((SELECT id FROM api_data.equipment WHERE name = 'Dell XPS 13'), 'Great laptop, very fast and reliable.', 5),
((SELECT id FROM api_data.equipment WHERE name = 'Dell XPS 13'), 'Bad laptop, very fast and reliable.', 2),
((SELECT id FROM api_data.equipment WHERE name = 'iPhone 12'), 'Love the camera quality but battery life could be better.', 4),
((SELECT id FROM api_data.equipment WHERE name = 'iPad Pro'), 'Excellent performance and display.', 5),
((SELECT id FROM api_data.equipment WHERE name = 'Dell UltraSharp U2719D'), 'Crystal clear display, highly recommend.', 5),
((SELECT id FROM api_data.equipment WHERE name = 'HP LaserJet Pro M404dn'), 'Fast printing speed and easy setup.', 4);


-- migrate:down
