from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta

fake = Faker()

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="p@55w0rD",
    database="fakedb"
)

cur = cnx.cursor()

# -----------------------------
# Load real users
# -----------------------------
cur.execute("SELECT id FROM users")
users = [u[0] for u in cur.fetchall()]

# -----------------------------
# Normal behavior model
# -----------------------------
country_weights = {
    "Canada": 0.6,
    "USA": 0.25,
    "UK": 0.1,
    "Germany": 0.03,
    "India": 0.01,
    "Nigeria": 0.01
}

devices = ["mobile", "desktop", "tablet"]
browsers = ["Chrome", "Firefox", "Safari", "Edge"]

# -----------------------------
# Error model (security relevant)
# -----------------------------
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
# Attack simulation flags
# -----------------------------
BRUTE_FORCE_USERS = random.sample(users, 10)
STUFFING_IP = fake.ipv4()

total_logs = 30000

for _ in range(total_logs):

    user_id = random.choice(users)

    # -----------------------------
    # Timestamp (last 30 days)
    # -----------------------------
    login_time = datetime.now() - timedelta(
        days=random.randint(0, 30),
        minutes=random.randint(0, 1440)
    )

    # -----------------------------
    # COUNTRY (weighted realism)
    # -----------------------------
    country = random.choices(
        list(country_weights.keys()),
        weights=list(country_weights.values())
    )[0]

    device = random.choice(devices)
    browser = random.choice(browsers)

    ip_address = fake.ipv4()

    # -----------------------------
    # DEFAULT BEHAVIOR
    # -----------------------------
    
    status = "SUCCESS"
    failure_reason = None
    error_code = None
    
    # -----------------------------
    # ATTACK 1: brute force
    # -----------------------------
    if user_id in BRUTE_FORCE_USERS and random.random() < 0.3:
        status = "FAILED"
        failure_reason = "wrong_password"
        error_code = "401 Unauthorized"
    
    # -----------------------------
    # ATTACK 2: credential stuffing
    # -----------------------------
    elif random.random() < 0.02:
        ip_address = STUFFING_IP
        status = "FAILED"
        failure_reason = "automated_attack"
        error_code = "429 Too Many Requests"
    
    # -----------------------------
    # NORMAL FAILURE CASE
    # -----------------------------
    elif random.random() < 0.1:
        status = "FAILED"
        failure_reason = "wrong_password"
        error_code = random.choices(
            list(error_weights.keys()),
            weights=list(error_weights.values())
        )[0]
    
    # -----------------------------
    # SUCCESS CASE (optional realism)
    # -----------------------------
    else:
        status = "SUCCESS"
        failure_reason = None
        error_code = None

    # -----------------------------
    # INSERT INTO DB
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
        device,
        browser,
        status,
        failure_reason,
        error_code
    ))

cnx.commit()
cnx.close()