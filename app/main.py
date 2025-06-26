import os
import streamlit as st
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        database=os.environ.get('DB_NAME', 'airflow_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

st.title("Channel Recommendation")
st.write("This is a placeholder app.")

if st.button("Ping DB"):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 as val")
            result = cur.fetchone()
        st.success(f"DB Connection OK, result={result['val']}")
    except Exception as e:
        st.error(str(e))
