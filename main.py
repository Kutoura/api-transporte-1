import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import psycopg2


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# 🔥 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se recomienda restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)


# ============================================================
# 🔹 MAPEO DE VEHÍCULO
# ============================================================

def map_vehiculo(row):
    return {
        "id": row[0],
        "placa": row[1],
        "estado": row[2],
        "indice": row[3],
        "empresa": row[4],
        "n_padron": row[5],
        "codigo": row[6],
        "dni_p": row[7],
        "nombres_p": row[8],
        "apellidos_p": row[9],
        "direccion_p": row[10],
        "dni_c": row[11],
        "nombres_c": row[12],
        "apellidos_c": row[13],
        "direccion_c": row[14],
        "licencia": row[15],
        "marca": row[16],
        "modelo": row[17],
        "color": row[18],
        "anio": row[19],
        "seguro": row[20]
    }


# ============================================================
# 🔥 GET VEHÍCULO POR CÓDIGO (QR)
# ============================================================

@app.get("/vehiculo/{codigo}")
def get_vehiculo(codigo: str):

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM vehiculos WHERE codigo = %s",
        (codigo,)
    )

    row = cur.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="No encontrado"
        )

    return map_vehiculo(row)


# ============================================================
# 🔹 LISTAR VEHÍCULOS
# ============================================================

@app.get("/vehiculos")
def listar():

    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM vehiculos LIMIT 50"
    )

    rows = cur.fetchall()

    return [map_vehiculo(r) for r in rows]


# ============================================================
# 🔹 CREAR VEHÍCULO
# ============================================================

@app.post("/vehiculo")
def crear(data: dict):

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO vehiculos (
            placa,
            estado,
            indice,
            persona_juridica,
            n_padron,
            codigo,
            dni_p,
            nombres_p,
            apellidos_p,
            direccion_p,
            dni_c,
            nombres_c,
            apellidos_c,
            direccion_c,
            licencia,
            marca,
            modelo,
            color,
            anio,
            seguro
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
    """, (
        data.get("placa"),
        data.get("estado"),
        data.get("indice"),
        data.get("empresa"),
        data.get("n_padron"),
        data.get("codigo"),
        data.get("dni_p"),
        data.get("nombres_p"),
        data.get("apellidos_p"),
        data.get("direccion_p"),
        data.get("dni_c"),
        data.get("nombres_c"),
        data.get("apellidos_c"),
        data.get("direccion_c"),
        data.get("licencia"),
        data.get("marca"),
        data.get("modelo"),
        data.get("color"),
        data.get("anio"),
        data.get("seguro")
    ))

    conn.commit()

    return {
        "mensaje": "Vehículo creado"
    }


# ============================================================
# 🔹 ACTUALIZAR VEHÍCULO
# ============================================================

@app.put("/vehiculo/{codigo}")
def actualizar(codigo: str, data: dict):

    cur = conn.cursor()

    cur.execute("""
        UPDATE vehiculos
        SET
            placa = %s,
            estado = %s,
            persona_juridica = %s
        WHERE codigo = %s
    """, (
        data.get("placa"),
        data.get("estado"),
        data.get("empresa"),
        codigo
    ))

    conn.commit()

    return {
        "mensaje": "Actualizado"
    }


# ============================================================
# 🔹 ELIMINAR VEHÍCULO
# ============================================================

@app.delete("/vehiculo/{codigo}")
def eliminar(codigo: str):

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM vehiculos WHERE codigo = %s",
        (codigo,)
    )

    conn.commit()

    return {
        "mensaje": "Eliminado"
    }


# ============================================================
# 🔹 LISTAR VEHÍCULOS POR EMPRESA / ASOCIACIÓN
# ============================================================
#
# Se utiliza TRIM() para ignorar espacios al inicio y al final
# del nombre de la persona jurídica.
#
# Ejemplo:
#
# "ASOCIACION DE MOTOTAXIS SANTA ROSA DE LIMA EL AGUSTINO"
#
# será considerado igual que:
#
# "ASOCIACION DE MOTOTAXIS SANTA ROSA DE LIMA EL AGUSTINO "
#
# ============================================================

@app.get("/vehiculos/empresa/{empresa}")
def listar_por_empresa(empresa: str):

    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM vehiculos
        WHERE TRIM(persona_juridica) = TRIM(%s)
        ORDER BY codigo ASC
    """, (empresa,))

    rows = cur.fetchall()

    return [map_vehiculo(r) for r in rows]


# ============================================================
# 🔹 LISTAR EMPRESAS / ASOCIACIONES
# ============================================================
#
# TRIM() elimina espacios innecesarios al inicio y al final.
# Esto evita que el frontend reciba nombres como:
#
# "SANTA ROSA DE LIMA EL AGUSTINO "
#
# ============================================================

@app.get("/empresas")
def listar_empresas():

    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT TRIM(persona_juridica)
        FROM vehiculos
        WHERE persona_juridica IS NOT NULL
          AND TRIM(persona_juridica) <> ''
        ORDER BY TRIM(persona_juridica) ASC
    """)

    rows = cur.fetchall()

    return [r[0] for r in rows]
