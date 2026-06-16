from datetime import date


def get_tags_by_wifi(cursor, wifi_ip):
    """Return list of tag names associated with a WiFi IP."""
    cursor.execute("SELECT tagname FROM tags WHERE wifi=%s", (wifi_ip,))
    return [row[0] for row in cursor.fetchall()]


def get_all_tag_locations(cursor):
    """Return list of non-empty location strings from tags."""
    cursor.execute("SELECT location FROM tags")
    return [row[0] for row in cursor.fetchall() if row[0] is not None and row[0] != ""]


def get_tags_by_location(cursor, location):
    """Return list of tag names associated with a location."""
    cursor.execute("SELECT tagname FROM tags WHERE location=%s", (location,))
    return [row[0] for row in cursor.fetchall()]


def get_incomplete_tasks_by_tag(cursor, tag_name):
    """Return list of task names with taskStatus=0 for a given tag."""
    cursor.execute(
        "SELECT taskName FROM taskinfo WHERE taskStatus=0 AND tag=%s",
        (tag_name,)
    )
    return [row[0] for row in cursor.fetchall()]


def get_all_tag_names(cursor):
    """Return list of all tag names."""
    cursor.execute("SELECT tagName FROM tags")
    return [row[0] for row in cursor.fetchall()]


def get_all_tags_with_ids(cursor):
    """Return list of (tagName, tagID) tuples."""
    cursor.execute("SELECT tagName, tagID FROM Tags")
    return cursor.fetchall()


def get_all_tags_full(cursor):
    """Return list of (tagID, tagName, wifi, location) tuples."""
    cursor.execute("SELECT tagID, tagName, wifi, location FROM TAGS")
    return cursor.fetchall()


def delete_tag_by_id(cursor, connection, tag_id):
    """Delete a tag by its ID."""
    cursor.execute("DELETE FROM TAGS WHERE tagID=%s", (tag_id,))
    connection.commit()


def insert_wifi_tag(cursor, connection, tag_name, wifi_ip):
    """Insert a new WiFi-based tag."""
    cursor.execute(
        "INSERT INTO TAGS (tagname, wifi) VALUES (%s, %s)",
        (tag_name, wifi_ip)
    )
    connection.commit()


def insert_weather_tag(cursor, connection, tag_name, city):
    """Insert a new Weather-based tag."""
    cursor.execute(
        "INSERT INTO TAGS (tagname, location) VALUES (%s, %s)",
        (tag_name, city)
    )
    connection.commit()


def insert_task(cursor, connection, task_name, category, tag, deadline):
    """Insert a new task into taskinfo."""
    cursor.execute(
        "INSERT INTO TaskInfo (taskName, Category, Tag, taskStatus, deadline) VALUES (%s,%s,%s,%s,%s)",
        (task_name, category, tag, 0, deadline)
    )
    connection.commit()


def toggle_task_status(connection, task_name, current_status):
    """Toggle task status between 0 and 1."""
    new_status = 0 if current_status == 1 else 1
    with connection.cursor(buffered=True) as cur:
        cur.execute(
            "UPDATE taskinfo SET taskStatus=%s WHERE taskName=%s",
            (new_status, task_name)
        )
    connection.commit()
    print(f"✅ {task_name} → {new_status}")


def delete_task(connection, cursor, task_name):
    """Delete a task by name."""
    with connection.cursor(buffered=True) as cur:
        cur.execute("DELETE FROM taskinfo WHERE taskName=%s", (task_name,))
    connection.commit()
    print(f"🗑️ Deleted task → {task_name}")


def get_tasks_all(cursor, category):
    """Get all incomplete tasks for a category, ordered by deadline."""
    cursor.execute(
        "SELECT taskName, taskStatus, deadline FROM taskinfo "
        "WHERE category=%s AND taskStatus=0 ORDER BY deadline ASC",
        (category,)
    )
    return cursor.fetchall()


def get_tasks_today(cursor, category):
    """Get incomplete tasks due today for a category."""
    cursor.execute(
        "SELECT taskName, taskStatus, deadline FROM taskinfo "
        "WHERE category=%s AND taskStatus=0 AND DATE(deadline)=%s ORDER BY deadline ASC",
        (category, date.today())
    )
    return cursor.fetchall()


def get_tasks_completed(cursor, category):
    """Get completed tasks for a category."""
    cursor.execute(
        "SELECT taskName, taskStatus, deadline FROM taskinfo "
        "WHERE category=%s AND taskStatus=1 ORDER BY deadline ASC",
        (category,)
    )
    return cursor.fetchall()


def get_tasks_by_tag(cursor, category, tag_name):
    """Get incomplete tasks for a category filtered by tag."""
    cursor.execute(
        "SELECT taskName, taskStatus FROM taskinfo "
        "WHERE category=%s AND taskStatus=0 AND tag=%s",
        (category, tag_name)
    )
    return cursor.fetchall()
