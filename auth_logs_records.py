#!/usr/bin/env python3
import ipaddress
from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta

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
# LOAD USERS
# -----------------------------
cur.execute("SELECT id, signup_country FROM users")
users_data = cur.fetchall()

users = [u[0] for u in users_data]

# map user baseline country
user_country = {u[0]: u[1] for u in users_data}

# assign network behavior
user_network_type = {
    u: "internal" if random.random() < 0.3 else "external"
    for u in users
}

# -----------------------------
# STATIC DATA
# -----------------------------
devices = ["mobile", "desktop", "tablet"]
browsers = ["Chrome", "Firefox", "Safari", "Edge"]

error_weights = {
    "401 Unauthorized": 0.5,
    "403 Forbidden": 0.1,
    "429 Too Many Requests": 0.2,
    "407 Proxy Authentication Required": 0.05,
    "500 Internal Server Error": 0.05,
    "503 Service Unavailable": 0.05,
    "504 Gateway Timeout": 0.05
}

# -----------------------------
# INTERNAL IP GENERATOR
# -----------------------------
def generate_internal_ip():
    private_ranges = [
        ("10.0.0.0", "10.255.255.255"),
        ("172.16.0.0", "172.31.255.255"),
        ("192.168.0.0", "192.168.255.255")
    ]

    start, end = random.choice(private_ranges)

    return str(ipaddress.IPv4Address(
        random.randint(
            int(ipaddress.IPv4Address(start)),
            int(ipaddress.IPv4Address(end))
        )
    ))

# -----------------------------
# ATTACK CONFIG
# -----------------------------
BRUTE_FORCE_USERS = random.sample(users, 10)
STUFFING_IP = fake.ipv4()

total_logs = 100000

# -----------------------------
# GENERATION LOOP
# -----------------------------
for _ in range(total_logs):

    user_id = random.choice(users)

    # baseline behavior
    base_country = user_country[user_id]

    if user_network_type[user_id] == "internal":
        ip_address = generate_internal_ip()
    else:
        ip_address = fake.ipv4()

    country = base_country
    device_type = random.choice(devices)
    browser = random.choice(browsers)

    login_time = datetime.now() - timedelta(
        days=random.randint(0, 30),
        minutes=random.randint(0, 1440)
    )

    status = "SUCCESS"
    failure_reason = None
    error_code = None

    attack_roll = random.random()

    # -----------------------------
    # ATTACK 1: BRUTE FORCE
    # -----------------------------
    if user_id in BRUTE_FORCE_USERS and attack_roll < 0.25:
        status = "FAILED"
        failure_reason = "wrong_password"
        error_code = "401 Unauthorized"
        login_time = datetime.now() - timedelta(minutes=random.randint(0, 5))

    # -----------------------------
    # ATTACK 2: CREDENTIAL STUFFING
    # -----------------------------
    elif attack_roll < 0.30:
        ip_address = STUFFING_IP
        status = "FAILED"
        failure_reason = "automated_attack"
        error_code = "429 Too Many Requests"

    # -----------------------------
    # ATTACK 3: ACCOUNT TAKEOVER
    # -----------------------------
    elif attack_roll < 0.33:
        status = "FAILED"
        failure_reason = "wrong_password"
        error_code = "401 Unauthorized"
        login_time = datetime.now() - timedelta(minutes=random.randint(1, 3))

        if random.random() < 0.7:
            status = "SUCCESS"
            failure_reason = None
            error_code = None
            ip_address = fake.ipv4()

    # -----------------------------
    # ATTACK 4: IMPOSSIBLE TRAVEL
    # -----------------------------
    elif attack_roll < 0.35:
        country = random.choice(
            [c for c in ["Canada","USA","UK","Germany","India","Nigeria"] if c != base_country]
        )
        ip_address = fake.ipv4()
        login_time = datetime.now() - timedelta(minutes=random.randint(0, 10))

    # -----------------------------
    # ATTACK 5: INSIDER THREAT
    # -----------------------------
    elif attack_roll < 0.37:
        ip_address = generate_internal_ip()
        status = "FAILED"
        failure_reason = "suspicious_internal_activity"
        error_code = "403 Forbidden"

    # -----------------------------
    # ATTACK 6: SUSPICIOUS SUCCESS
    # -----------------------------
    elif attack_roll < 0.39:
        status = "SUCCESS"
        ip_address = fake.ipv4()
        country = random.choice(
            [c for c in ["Canada","USA","UK","Germany","India","Nigeria"] if c != base_country]
        )

    # -----------------------------
    # NORMAL FAILURE
    # -----------------------------
    elif attack_roll < 0.50:
        status = "FAILED"
        failure_reason = "wrong_password"
        error_code = random.choices(
            list(error_weights.keys()),
            weights=list(error_weights.values())
        )[0]

    # -----------------------------
    # INSERT
    # -----------------------------
    cur.execute("""
        INSERT INTO auth_logs
        (user_id, login_timestamp, ip_address, country, device_type, browser, status, failure_reason, error_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        login_time,
        ip_address,
        country,
        device_type,
        browser,
        status,
        failure_reason,
        error_code
    ))

# -----------------------------
# FINALIZE
# -----------------------------
cnx.commit()
cnx.close()