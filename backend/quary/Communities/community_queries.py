import json
import logging

from sqlalchemy import exc, text
from scripts.constants.queries_text import SINGLE_COMMUNITY, GET_COMMUNITIES, UPDATE_COMMUNITY, GET_USER_COMMUNITIES, \
    GET_COMMUNITY_USERS
from scripts.modules.buckets.buckets import bucket_delete, bucket_upload_file
from scripts.constants.http_response_msg import ERROR_SQL_DB, ERROR_UNEXPECTED
from scripts.handler.error_handler import UnexpectedError, SQLAlchemyError
from scripts.setup.db_setup import Community, dbsession, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


def community_query_get_communities_by_user_id(user_id):
    with Session() as session:
        try:
            sql = text(GET_USER_COMMUNITIES)
            result = session.execute(sql, {'p_userId': user_id})
            first_result = result.fetchone()
            # Ensure all additional result sets are consumed
            while True:
                if not result.cursor.nextset():
                    break
            # Parse the JSON string into a Python object
            if first_result:
                return json.loads(first_result[0])  # Parse the JSON string from the first column
            else:
                return None
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error occurred: {str(e)}")
        finally:
            session.close()


def community_query_get_community_by_id(id_community):
    with Session() as session:
        try:
            sql = text(SINGLE_COMMUNITY)
            result = session.execute(sql, {'p_id': id_community})
            first_result = result.fetchone()
            # Ensure all additional result sets are consumed
            while True:
                if not result.cursor.nextset():
                    break
            # Parse the JSON string into a Python object
            if first_result:
                return json.loads(first_result[0])  # Parse the JSON string from the first column
            else:
                return None
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error occurred: {str(e)}")
        finally:
            session.close()


def community_query_get_all_communities(user_id):
    """
    Fetches all communities from the database using a stored procedure.
    :return: A list of all communities in JSON format, or None if no communities are found.
    """
    session = Session()
    try:
        sql = text(GET_COMMUNITIES)
        result = session.execute(sql, {'userId': user_id}).fetchall()

        if not result:
            return None

        return [json.loads(row[0]) for row in result]
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()


def community_query_new_community(session, user_id, name, imagePath, bannerPath, description, street, city, country, timezone,
                                  latitude, longitude, is_private, is_closed):
    """
    Inserts a new community within an existing session and returns the ID of the newly created community.
    """
    result = session.execute(
        text("CALL CreateCommunityAndATA(:p_user_id, :p_community_name , :p_community_imagePath , "
             ":p_community_bannerPath, :p_community_description, :p_community_street, :p_community_city, "
             ":p_community_country, :p_community_timezone, :p_community_latitude, :p_community_longitude, "
             ":p_community_IsPrivate, :p_community_IsClosed,  @p_community_id)"),
        {
            'p_user_id': user_id,
            'p_community_name': name,
            'p_community_imagePath': imagePath,
            'p_community_bannerPath': bannerPath,
            'p_community_description': description,
            'p_community_street': street,
            'p_community_city': city,
            'p_community_country': country,
            'p_community_timezone': timezone,
            'p_community_latitude': latitude,
            'p_community_longitude': longitude,
            'p_community_IsPrivate': is_private,
            'p_community_IsClosed': is_closed
        }
    )
    community_id = session.execute(text("SELECT @p_community_id")).scalar()
    return community_id


def community_query_update_community(community_id, updates):
    logging.debug("first line in community Query")
    updates_json = json.dumps(updates)
    logging.debug(f"Query Updating community with ID: {community_id} using updates: {updates_json}")

    update_sql = text(UPDATE_COMMUNITY)

    try:
        with Session() as session:
            session.execute(update_sql, {
                'p_community_id': community_id,
                'p_updates': updates_json
            })
            session.commit()
            logging.debug("Community update committed successfully.")
    except exc.SQLAlchemyError as e:
        logging.error(f"SQLAlchemyError: {e}")
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        logging.error(f"UnexpectedError: {e}")
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def community_query_delete_community(community_id, id_token: str):
    """
    Deletes a community based on the provided community ID and requester user ID.
    Checks if the requester is the owner of the community before deletion.
    """
    delete_sql = text("""
        CALL DeleteCommunity(:p_community_id, :p_requester_userId)
    """)

    try:
        with Session() as session:
            session.execute(delete_sql, {
                'p_community_id': community_id,
                'p_requester_userId': id_token
            })
            session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def community_query_get_all_community_users(community_id):
    """
    Fetches all community users from the database using a stored procedure.
    :return: A list of all community users in dictionary format, or None if no communities are found.
    """
    session = Session()
    try:
        sql = text(GET_COMMUNITY_USERS)
        result = session.execute(sql, {"p_community_id": community_id}).fetchall()

        if not result:
            return None

        return [json.loads(row[0]) for row in result]
    except exc.SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()


def community_query_add_banner(community_id, banner_path):
    """
    Adds a banner path to the specified community in the database.
    :param community_id: The ID of the community to update.
    :param banner_path: The path to the banner image after it has been uploaded to storage.
    :return: Updates the database with the new banner path or raises an error.
    """
    try:
        community = dbsession.query(Community).filter_by(community_id=community_id).one()
        community.banner_path = banner_path
        dbsession.commit()
        return {"message": "Banner added successfully", "banner_path": banner_path}
    except exc.NoResultFound:
        raise ValueError("Community not found")
    except exc.SQLAlchemyError as e:
        dbsession.rollback()
        raise SQLAlchemyError(f"Failed to add banner: {str(e)}")


def community_query_update_banner(community_id, banner_path):
    """
    Updates the banner path for the specified community in the database.
    :param community_id: The ID of the community to update.
    :param new_banner_path: The new path to the banner image after it has been uploaded to storage.
    :return: Updates the database with the new banner path or raises an error.
    """
    try:
        community = dbsession.query(Community).filter_by(community_id=community_id).one()
        community.banner_path = banner_path
        dbsession.commit()
        return {"message": "Banner added successfully", "banner_path": banner_path}
    except exc.NoResultFound:
        raise ValueError("Community not found")
    except exc.SQLAlchemyError as e:
        dbsession.rollback()
        raise SQLAlchemyError(f"Failed to add banner: {str(e)}")
