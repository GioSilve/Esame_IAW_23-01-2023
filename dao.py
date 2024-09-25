import sqlite3

def element_already_in_db(table, column, value):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} WHERE {column} = ?"
    cursor.execute(query, (value,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def add_user(new_user):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "INSERT INTO users(username,name,surname,password,type) VALUES(?,?,?,?,?)"
    try:
        cursor.execute(query, (str(new_user["username"]), str(new_user["name"]), str(new_user["surname"]), str(new_user["password"]), str(new_user["type"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in registering user into the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def add_series(new_series):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "INSERT INTO series(title,description,category,image,username) VALUES(?,?,?,?,?)"
    try:
        cursor.execute(query, (str(new_series["title"]), str(new_series["description"]), str(new_series["category"]), str(new_series["image"]), str(new_series["username"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in adding a series into the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def add_episode(new_episode):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "INSERT INTO episodes(title,description,date,audiofile,series_id) VALUES(?,?,?,?,?)"
    try:
        cursor.execute(query, (str(new_episode["title"]), str(new_episode["description"]), str(new_episode["date"]), str(new_episode["audiofile"]), int(new_episode["series_id"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in adding an episode into the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def get_latest_added_id():
    conn = sqlite3.connect("db\youtalk.db")
    cursor = conn.cursor()
    query = "SELECT MAX(series_id) FROM series"
    cursor.execute(query)
    latest_id = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return latest_id

def get_all_elements(table, column, order):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} ORDER BY {column} {order}"
    cursor.execute(query)
    elements = cursor.fetchall()
    cursor.close()
    conn.close()
    return elements

def user_follows_series(username, series_id):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM follows WHERE username = ? AND series_id = ?"
    cursor.execute(query, (username, series_id))
    follows = cursor.fetchone()
    cursor.close()
    conn.close()
    return follows

def follow_series(username, series_id):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "INSERT INTO follows(username,series_id) VALUES(?,?)"
    try:
        cursor.execute(query, (username, series_id))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in adding a followed series to the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def unfollow_series(username, series_id):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "DELETE FROM follows WHERE username = ? AND series_id = ?"
    try:
        cursor.execute(query, (username, series_id))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in deleting a followed series from the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def get_all_followed_ids(username):
    conn = sqlite3.connect("db\youtalk.db")
    cursor = conn.cursor()
    query = "SELECT series_id FROM follows WHERE username = ?"
    cursor.execute(query, (username,))
    followed_ids = [f[0] for f in cursor.fetchall()]
    cursor.close()
    conn.close()
    return followed_ids

def get_any_by_username(username, table):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} WHERE username = ?"
    cursor.execute(query, (username,))
    found = cursor.fetchone()
    cursor.close()
    conn.close()
    return found

def get_all_by_series_id(username, table, source, column, order):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} WHERE series_id IN (SELECT series_id FROM {source} WHERE username = ?) ORDER BY {column} {order}"
    cursor.execute(query, (username,))
    followed_series = cursor.fetchall()
    cursor.close()
    conn.close()
    return followed_series

def get_all_by_category(category, table, column, order):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM {table} WHERE series_id IN (SELECT series_id FROM series WHERE category = ?) ORDER BY {column} {order}"
    cursor.execute(query, (category,))
    of_category = cursor.fetchall()
    cursor.close()
    conn.close()
    return of_category

def get_series_by_episode_id(episode_id):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM series WHERE series_id IN (SELECT series_id FROM episodes WHERE episode_id = ?)"
    cursor.execute(query, (episode_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def user_follows_series_by_episode_id(episode_id, username):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM follows WHERE series_id IN (SELECT series_id FROM episodes WHERE episode_id = ?) AND username = ?"
    cursor.execute(query, (episode_id, username))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def add_comment(new_comment):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "INSERT INTO comments(text,episode_id,series_id,username) VALUES(?,?,?,?)"
    try:
        cursor.execute(query, (str(new_comment["text"]), str(new_comment["episode_id"]), str(new_comment["series_id"]), str(new_comment["username"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in adding a comment into the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def get_comments_by_episode_id(episode_id):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f"SELECT * FROM comments WHERE episode_id = ? ORDER BY comment_id DESC"
    cursor.execute(query, (episode_id,))
    comments = cursor.fetchall()
    cursor.close()
    conn.close()
    return comments

def delete_from_table_by_id(table, column, value):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = f"DELETE FROM {table} WHERE {column} = ?"
    try:
        cursor.execute(query, (value,))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in deleting comments from the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def get_audiofiles_by_series_id(series_id):
    conn = sqlite3.connect("db\youtalk.db")
    cursor = conn.cursor()
    query = "SELECT audiofile FROM episodes WHERE series_id = ?"
    cursor.execute(query, (series_id,))
    audiofiles = [f[0] for f in cursor.fetchall()]
    cursor.close()
    conn.close()
    return audiofiles

def edit_comment(comment_id, input_text):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "UPDATE comments SET text = ? WHERE comment_id = ?"
    try:
        cursor.execute(query, (input_text, comment_id))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in editing a comment from the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def edit_episode(new_episode):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "UPDATE episodes SET title = ?, description = ?, date = ?, audiofile = ? WHERE episode_id = ?"
    try:
        cursor.execute(query, (str(new_episode["title"]), str(new_episode["description"]), str(new_episode["date"]), str(new_episode["audiofile"]), int(new_episode["episode_id"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in editing an episode from the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success

def edit_series(new_series):
    conn = sqlite3.connect("db\youtalk.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False
    query = "UPDATE series SET title = ?, description = ?, category = ?, image = ? WHERE series_id = ?"
    try:
        cursor.execute(query, (str(new_series["title"]), str(new_series["description"]), str(new_series["category"]), str(new_series["image"]), int(new_series["series_id"])))
        conn.commit()
        success = True
    except Exception as e:
        print('Error in editing a series from the database!', str(e))
        conn.rollback()
    cursor.close()
    conn.close()
    return success
