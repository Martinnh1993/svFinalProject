import json
from sqlalchemy import exc, text
from sqlalchemy.orm import sessionmaker

from scripts.constants.queries_text import GET_ALL_COMMUNITY_POSTS, GET_ALL_COMMUNITY_USER_POSTS, \
    GET_COMMUNITY_POST_BY_ID, CREATE_COMMUNITY_POST, UPDATE_COMMUNITY_POST, DELETE_COMMUNITY_POST, HIDE_COMMUNITY_POST, \
    SHOW_COMMUNITY_POST
from scripts.handler.error_handler import SQLAlchemyError, UnexpectedError
from scripts.setup.db_setup import engine

Session = sessionmaker(bind=engine)


def query_get_all_community_user_posts(user_id):
    session = Session()
    try:
        sql = text(GET_ALL_COMMUNITY_USER_POSTS)
        result = session.execute(sql, {'p_user_id': user_id})
        # Fetch all results if expecting multiple results or the query is formatted to do so
        results = result.fetchall()
        if not results:
            return None

        # Convert results assuming each row contains a JSON string at the first index
        posts = [json.loads(row[0]) for row in results]
        return posts
    except SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
    finally:
        session.close()


def query_get_community_post_by_id(post_id):
    with Session() as session:
        try:
            # Execute the stored procedure with the provided post_id
            sql = text(GET_COMMUNITY_POST_BY_ID)
            result = session.execute(sql, {'p_postId': post_id})

            # Attempt to fetch the first row of the result
            first_result = result.fetchone()

            # Ensure all additional result sets are consumed
            while True:
                if not result.cursor.nextset():
                    break

            # If data is found, return it as a JSON object, otherwise return None
            return json.loads(first_result[0]) if first_result else None
        except SQLAlchemyError as e:
            # Rollback the session in the event of an error to avoid any database inconsistencies
            session.rollback()
            raise SQLAlchemyError(f"Database error occurred: {str(e)}")
        except Exception as e:
            # General exception handling to catch any other unexpected errors
            raise Exception(f"An unexpected error occurred: {str(e)}")


def query_get_all_community_posts(community_id):
    session = Session()
    try:
        # Ensure you're calling the stored procedure correctly
        sql = text(GET_ALL_COMMUNITY_POSTS)
        result = session.execute(sql, {'p_community_id': community_id})

        # Fetch all results
        results = result.fetchall()
        if not results:
            return None

        # Assuming each row in results contains a JSON string at the first index
        posts = [json.loads(row[0]) for row in results]

        return posts
    except SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")
    finally:
        session.close()


def query_create_community_post(session, user_id, community_id, description):
    try:
        session.execute(text(CREATE_COMMUNITY_POST),
                        {
                            'p_user_id': user_id,
                            'p_community_id': community_id,
                            'p_description': description,
                        }
                        )

        post_id = session.execute(text("SELECT @p_post_id")).scalar()
        return post_id

    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def query_update_community_post(post_id, updates):
    updates_json = json.dumps(updates)
    try:
        with Session() as session:
            sql = text(UPDATE_COMMUNITY_POST)
            session.execute(
                sql, {'p_postId': post_id, 'p_updates': updates_json}
            )
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def query_delete_community_post(post_id):
    try:
        with Session() as session:
            sql = text(DELETE_COMMUNITY_POST)
            session.execute(
                sql, {'p_post_id': post_id}
            )
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def query_hide_community_post(post_id):
    try:
        with Session() as session:
            sql = text(HIDE_COMMUNITY_POST)
            session.execute(sql, {'p_post_id': post_id})
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def query_show_community_post(post_id):
    try:
        with Session() as session:
            sql = text(SHOW_COMMUNITY_POST)
            session.execute(sql, {'p_post_id': post_id})
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")
