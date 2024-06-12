import json

from flask import session
from sqlalchemy import text, exc
from sqlalchemy.orm import sessionmaker

from scripts.constants.queries_text import ADD_COMMUNITY_USER, COMMUNITY_INVITE, COMMUNITY_REQUEST, \
    ACCEPT_COMMUNITY_INVITE, ACCEPT_COMMUNITY_REQUEST, DENY_COMMUNITY_INVITE, DENY_COMMUNITY_REQUEST, \
    GET_COMMUNITY_INVITES, GET_COMMUNITY_REQUESTS, GET_COMMUNITY_REQUEST_BY_ID, REMOVE_COMMUNITY_USER, LEAVE_COMMUNITY, \
    PROMOTE_MODERATOR, DEMOTE_MODERATOR, CHANGE_OWNER
from scripts.handler.error_handler import SQLAlchemyError, UnexpectedError
from scripts.setup.db_setup import engine, dbsession

Session = sessionmaker(bind=engine)


def get_query_community_requests(community_id):
    """
    Retrieves the community invites with the given ID and returns them as a list of JSON objects.

    :param community_id: ID of the community to look up invites for
    :return: List of JSON objects with information about the community invites or an error message
    """
    try:
        sql = text(GET_COMMUNITY_REQUESTS)  # Ensure this is your correct SQL query
        result = dbsession.execute(sql, {"p_community_id": community_id}).fetchall()

        if not result:
            return []  # Return an empty list if no results are found

        # Process each row, ensuring that only non-None values are parsed
        request = [json.loads(row[0]) for row in result if row[0] is not None]
        return request
    except exc.SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def get_query_community_request_by_id(community_id, user_id):
    try:
        sql = text(GET_COMMUNITY_REQUEST_BY_ID)  # Ensure this is your correct SQL query
        result = dbsession.execute(sql, {"p_communityId": community_id, "p_userId": user_id}).fetchall()

        if not result:
            return []  # Return an empty list if no results are found

        # Process each row, ensuring that only non-None values are parsed
        request = [json.loads(row[0]) for row in result if row[0] is not None]
        return request
    except exc.SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def community_query_request(user_id: str, community_id):
    """
    Requests to join a community by calling the CommunityRequest stored procedure.

    :param user_id: The user ID of the person requesting to join.
    :param community_id: The ID of the community to join.
    :return: None, raises an exception if the database operation fails.
    """
    session = Session()
    try:
        # Call the stored procedure with the necessary parameters
        sql = text(COMMUNITY_REQUEST)
        session.execute(sql, {'p_userId': user_id, 'p_communityId': community_id})
        session.commit()  # Commit the transaction
        print("Request to join community has been processed.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise
    finally:
        session.close()


def accept_query_community_request(user_id, community_id):
    """
    Accepts a request for a user to join a community by updating their role.

    :param user_id: The user ID of the person whose request is being accepted.
    :param community_id: The ID of the community where the request is accepted.
    :return: None, raises an exception if the database operation fails.
    """
    session = Session()
    try:
        # Start a transaction
        session.begin()
        sql = text(ACCEPT_COMMUNITY_REQUEST)
        session.execute(sql, {'p_userId': user_id, 'p_communityId': community_id})
        session.commit()  # Commit the transaction
        print("Community request has been accepted.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    finally:
        session.close()  # Ensure the session is closed properly


def deny_query_community_request(community_id, user_id):
    """
        Deny a request for a user to join a community by updating their role.

        :param user_id: The user ID of the person whose request is being accepted.
        :param community_id: The ID of the community where the request is accepted.
        :return: None, raises an exception if the database operation fails.
        """
    session = Session()
    try:
        # Start a transaction
        session.begin()
        sql = text(DENY_COMMUNITY_REQUEST)
        session.execute(sql, {'p_community_id': community_id, 'p_userId': user_id})
        session.commit()  # Commit the transaction
        print("Community request has been denied.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    finally:
        session.close()  # Ensure the session is closed properly


def get_query_community_invites(user_id):
    """
    Retrieves the community invites for a given user ID and returns them as a list of JSON objects.

    :param user_id: User ID to look up invites for
    :return: List of JSON objects with information about the community invites or an error message
    """
    try:
        sql = text(GET_COMMUNITY_INVITES)  # Correctly reference the stored procedure
        result = dbsession.execute(sql, {'p_userId': user_id}).fetchall()

        if not result or result[0][0] is None:
            return []  # Return an empty list if no results or null results are found

        return json.loads(result[0][0])  # Convert JSON string to Python list
    except exc.SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database error occurred: {str(e)}")
    except Exception as e:
        raise UnexpectedError(f"An unexpected error occurred: {str(e)}")


def community_query_invite(user_id, community_id):
    """
        Invite a user to join a community by calling the CommunityRequest stored procedure.

        :param user_id: The user ID of the person requesting to join.
        :param community_id: The ID of the community to join.
        :return: None, raises an exception if the database operation fails.
        """
    session = Session()
    try:
        # Call the stored procedure with the necessary parameters
        sql = text(COMMUNITY_INVITE)
        session.execute(sql, {'p_userId': user_id, 'p_communityId': community_id})
        session.commit()  # Commit the transaction
        print("Invite to join community has been processed.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise
    finally:
        session.close()


def accept_query_community_invite(user_id, community_id):
    """
        Accepts a request for a user to join a community by updating their role.

        :param user_id: The user ID of the person whose request is being accepted.
        :param community_id: The ID of the community where the request is accepted.
        :return: None, raises an exception if the database operation fails.
        """
    session = Session()
    try:
        # Start a transaction
        session.begin()
        sql = text(ACCEPT_COMMUNITY_INVITE)
        session.execute(sql, {'p_userId': user_id, 'p_communityId': community_id})
        session.commit()  # Commit the transaction
        print("Community invite has been accepted.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    finally:
        session.close()  # Ensure the session is closed properly


def deny_query_community_invite(community_id, user_id):
    """
            Deny a request for a user to join a community by updating their role.

            :param user_id: The user ID of the person whose request is being accepted.
            :param community_id: The ID of the community where the request is accepted.
            :return: None, raises an exception if the database operation fails.
            """
    session = Session()
    try:
        # Start a transaction
        session.begin()
        sql = text(DENY_COMMUNITY_INVITE)
        session.execute(sql, {'p_community_id': community_id, 'p_userId': user_id})
        session.commit()  # Commit the transaction
        print("Community invite has been denied.")
    except SQLAlchemyError as e:
        session.rollback()  # Roll back the transaction on error
        print(f"SQLAlchemy Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
        raise  # Re-raise the exception to handle it further up the call stack if necessary
    finally:
        session.close()  # Ensure the session is closed properly


def query_add_community_user(user_id, community_id):
    session = Session()
    try:
        session.execute(text(ADD_COMMUNITY_USER), {'p_user_userId': user_id, 'p_community_id': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_remove_user_from_community(requester_user_id, user_id, community_id):
    session = Session()
    try:
        session.execute(text(REMOVE_COMMUNITY_USER),
                        {'p_requester_userId': requester_user_id, 'p_userId': user_id, 'p_communityId': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_leave_community(user_id, community_id):
    session = Session()
    try:
        session.execute(text(LEAVE_COMMUNITY), {'p_userId': user_id, 'p_communityId': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_community_user_promote(requester_id, user_id, community_id):
    session = Session()
    try:
        session.execute(text(PROMOTE_MODERATOR),
                        {'p_requester_user_id': requester_id, 'p_user_id': user_id, 'p_community_id': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def query_community_user_demote(requester_id, user_id, community_id):
    session = Session()
    try:
        session.execute(text(DEMOTE_MODERATOR),
                        {'p_requester_user_id': requester_id, 'p_moderator_user_id': user_id, 'p_community_id': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def query_community_user_change_owner(requester_id, user_id, community_id):
    session = Session()
    try:
        session.execute(text(CHANGE_OWNER),
                        {'p_old_owner_user_id': requester_id, 'p_new_owner_user_id': user_id, 'p_community_id': community_id})
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()