from app import db, log


def dbInsert(items):
    """
    Inserts items into the database

    Args:
        items: A single model object or a list of objects

    Returns:
       Boolean: True if successful, otherwise False
    """
    if items is None:
        raise Exception("Cannot insert items of type None.")

    try:
        if isinstance(items, list):
            for item in items:
                db.session.add(item)
        else:
            result = db.session.add(items)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        raise Exception("Error inserting [{items}] into the database: {error}".format(items=items, error=e))


def dbSelect(statement):
    """
    Executes a select statement
    
    Args:
        statement (str): statement to execute
    
    Raises:
        Exception: On database exception
    
    Returns:
        List of Rows: On success, returns list of rows that are returned by the execution of statement 
        None: Returns None when the result returned 0 rows
    """
    if statement is None:
        raise TypeError("Cannot execute a statement of type None")

    try:
        result = db.session.execute(statement).fetchall()
        if len(result) is 0:
            return None
        else:
            return result
    except Exception as e:
        raise Exception("Error executing query [{stmt}]: {error}".format(stmt=statement, error=e))


def dbDelete(items):
    """
    Deletes items in the databse
    
    Args:
        items (List): List of database object items to delete
    
    Raises:
        TypeError: When items is None 
        Exception: When the database throws an error 
    
    Returns:
       Boolean: True on success 
    """
    if items is None:
        raise TypeError("Cannot insert items of type None.")

    try:
        if isinstance(items, list):
            for item in items:
                db.session.delete(item)
        else:
            db.session.delete(item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        db.session.flush()
        raise Exception("Error deleting [{items}] into the database: {error}".format(items=items, error=e))
