import sqlparse

BLOCKED_KEYWORDS = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "ATTACH", "PRAGMA"]

def is_safe_query(sql):
    if sql.strip().upper() == "SELECT 'UNSUPPORTED_QUERY';":
        return False, "Query not supported by current schema."

    parsed = sqlparse.parse(sql)
    if not parsed:
        return False, "Could not parse SQL."

    statement = parsed[0]
    if statement.get_type() != "SELECT":
        return False, "Only SELECT statements are allowed."

    upper_sql = sql.upper()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in upper_sql:
            return False, f"Blocked keyword detected: {keyword}"

    return True, "OK"