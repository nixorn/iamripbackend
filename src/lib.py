def save_record(session, record):
    try:
        session.add(record)
        session.commit()
    except:
        session.rollback()
