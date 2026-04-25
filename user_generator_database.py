#!/usr/bin/env python3
from faker import Faker
import mysql.connector
import random

fake = Faker()

# -----------------------------
# DB CONNECTION
# -----------------------------
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="p@55w0rD",
    database="fakedb"
)

cur = cnx.cursor()

# -----------------------------
# BASELINE DATA
# -----------------------------
countries = ["Canada", "USA", "UK", "Germany", "India", "Nigeria"]
devices = ["mobile", "desktop", "tablet"]

total_users = 100000

for _ in range(total_users):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password()

    signup_ip = fake.ipv4()
    signup_country = random.choice(countries)
    signup_device = random.choice(devices)

    cur.execute("""
        INSERT INTO users 
        (first_name, last_name, email, password, signup_ip, signup_country, signup_device)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        first_name,
        last_name,
        email,
        password,
        signup_ip,
        signup_country,
        signup_device
    ))

cnx.commit()
cnx.close()