from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Literal
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

connection = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST') if os.getenv('DEBUG_MODE') == 'false' else 'localhost',
    port=os.getenv('POSTGRES_PORT'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    cursor_factory=RealDictCursor
)
connection.autocommit = True


@app.get("/")
def hello_world():
    return "<p>Hello, World!</p>"


# Create
@app.post('/equipment/create')
def create_equipment():
    body = request.json
    category = body['category']
    name = body['name']
    size = body['size']
    query = SQL("""
        INSERT INTO api_data.equipment (category, name, "SIZE")
        VALUES ({category}, {name}, {size})
        RETURNING id
    """).format(
        category=Literal(category),
        name=Literal(name),
        size=Literal(size)
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    return jsonify(result), 201


# Read
@app.get('/equipment')
def get_all_equipment():
    query = """
        WITH
        equipment_with_companies AS (
            SELECT 
                e.id,
                e.category,
                e.name,
                e."SIZE",
                COALESCE(jsonb_agg(json_build_object(
                    'id', c.id, 'title', c.title, 'phone', c.phone, 'adress', c.adress))
                    FILTER (WHERE c.id IS NOT NULL), '[]') AS companies
            FROM api_data.equipment e
            LEFT JOIN api_data.equipment_to_company etc ON e.id = etc.equipment_id
            LEFT JOIN api_data.company c ON c.id = etc.company_id
            GROUP BY e.id
        ),
        equipment_with_reviews AS (
            SELECT
                eq.id,
                eq.category,
                eq.name,
                eq."SIZE",
                COALESCE(jsonb_agg(json_build_object(
                    'id', r.id, 'text', r."text", 'grade', r.grade))
                    FILTER (WHERE r.id IS NOT NULL), '[]') AS reviews
            FROM api_data.equipment eq
            LEFT JOIN api_data.review r ON eq.id = r.equipment_id
            GROUP BY eq.id
        )
        SELECT ewc.id, ewc.category, ewc.name, ewc."SIZE", ewc.companies, ewr.reviews
        FROM equipment_with_companies ewc
        JOIN equipment_with_reviews ewr ON ewc.id = ewr.id;
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    return jsonify(result)


# Update
@app.put('/equipment/update')
def update_equipment():
    body = request.json
    id = body['id']
    category = body['category']
    name = body['name']
    size = body['size']
    query = SQL("""
        UPDATE api_data.equipment
        SET category = {category}, name = {name}, "SIZE" = {size}
        WHERE id = {id}
        RETURNING id
    """).format(
        category=Literal(category),
        name=Literal(name),
        size=Literal(size),
        id=Literal(id)
    )
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'Equipment not found'}), 404


# Delete
@app.delete('/equipment/delete')
def delete_equipment():
    body = request.json
    id = body['id']
    query = SQL("""
        DELETE FROM api_data.equipment
        WHERE id = {id}
        RETURNING id
    """).format(id=Literal(id))
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    if result:
        return '', 204
    else:
        return jsonify({'error': 'Equipment not found'}), 404


@app.get('/reviews/search_by_text')
def search_reviews_by_text():
    text = request.args.get('text', '')
    if not text:
        return jsonify({'error': 'Text query parameter is required'}), 400

    query = SQL("""
        SELECT id, equipment_id, "text", grade
        FROM api_data.review
        WHERE "text" ILIKE {text}
        ORDER BY grade DESC
    """).format(
        text=Literal(f'%{text}%')
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return jsonify(result)


@app.get('/reviews/search_by_grade')
def search_reviews_by_grade():
    try:
        grade = int(request.args.get('grade', ''))
    except ValueError:
        return jsonify({'error': 'Grade query parameter must be an integer'}), 400

    query = SQL("""
        SELECT id, equipment_id, "text", grade
        FROM api_data.review
        WHERE grade = {grade}
        ORDER BY "text"
    """).format(
        grade=Literal(grade)
    )

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()

    return jsonify(result)


if __name__ == '__main__':
    app.run(port=os.getenv('FLASK_PORT'))
