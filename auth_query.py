def authenticate_user(db_cursor, username, password_hash):
    # CRITICAL BUG: Raw f-string interpolation invites ' OR 1=1 -- exploit!
    query = f"SELECT id, role FROM users WHERE username = '{username}' AND password = '{password_hash}'"
    db_cursor.execute(query)
    return db_cursor.fetchone()
