from faker import Faker

from faker.providers import internet

fake = Faker()
# print(fake.name())
# print(fake.email())
# print(fake.password())
# print(fake.ipv4())


import mysql.connector

# Connect to server
cnx = mysql.connector.connect(
    host="localhost",
    # port=3306,
    user="root",
    password="p@55w0rD", 
    database="fakedb")
    
# Get a cursor
cur = cnx.cursor()

total_record = 44863
for var in range(total_record):
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
    password = fake.password()
    ip_address = fake.ipv4()
    
    
    # Insert a record)
    cur.execute("INSERT INTO users (first_name, last_name, email, password, ip_address) VALUES (%s, %s, %s, %s, %s)", (first_name, last_name, email, password, ip_address)) 
    
# Execute a query
cur.execute("SELECT CURDATE()")

# Fetch one result
row = cur.fetchone()
print("Current date is: {0}".format(row[0]))

# Commit changes
cnx.commit()

# Close connection
cnx.close()