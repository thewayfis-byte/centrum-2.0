from design_database import c, db

c.execute("DROP TABLE staff, staff_perms, users")
db.commit()