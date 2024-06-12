import logging

from flask import jsonify

from scripts.handler.error_handler import SQLAlchemyError
from scripts.modules.mysql.Communities.member.community_member_queries import \
    community_query_invite, accept_query_community_request, deny_query_community_request, \
    deny_query_community_invite, accept_query_community_invite, community_query_request, get_query_community_requests, \
    get_query_community_request_by_id, get_query_community_invites, query_add_community_user, \
    query_remove_user_from_community, query_leave_community, query_community_user_promote, query_community_user_demote, \
    query_community_user_change_owner


def manage_get_community_requests(community_id):
    """
    Retrieves the community with the given ID and returns it as a JSON object.

    :param community_id: ID of the community to look up
    :return: JSON object with information about the community or an error message
    """
    request = get_query_community_requests(community_id)
    if request is None:
        return {"message": "No community found with the provided ID"}, 400  # HTTP 400 Bad Request

    return request, 200  # HTTP 200 OK


def manage_get_community_request_by_id(community_id, user_id: str):
    """
        Retrieves the community with the given ID and returns it as a JSON object.

        :param user_id:
        :param community_id: ID of the community to look up
        :return: JSON object with information about the community or an error message
        """
    request = get_query_community_request_by_id(community_id, user_id)
    if request is None:
        return {"message": "No community found with the provided ID"}, 400  # HTTP 400 Bad Request

    return request, 200  # HTTP 200 OK


def manage_create_community_request(community_id, user_id: str):
    """
    Creates a request for a user to join a community.

    :param community_id: ID of the community the user wants to join
    :param user_id: ID of the user making the request
    :return: JSON response indicating the outcome
    """
    try:
        community_query_request(user_id, community_id)  # Assuming this function exists and calls the stored procedure
        return {"message": "Request to join community submitted successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500


def manage_accept_community_request(user_id, community_id):
    """
        Manages the acceptance of a community join request.

        :param user_id: ID of the user whose request is to be accepted.
        :param community_id: ID of the community where the request is accepted.
        :return: A tuple containing a message dictionary and a status code.
        """
    try:
        accept_query_community_request(user_id, community_id)
        return {"message": "Community request accepted successfully"}, 200
    except SQLAlchemyError as e:
        # Log the error or handle it according to your error management strategy
        print(f"Database operation failed: {e}")
        return {"error": "Database operation failed, unable to accept request"}, 500
    except Exception as e:
        # Log unexpected errors and handle them accordingly
        print(f"Unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred"}, 500


def manage_deny_community_request(community_id, user_id):
    """
        Manages the acceptance of a community join request.

        :param user_id: ID of the user whose request is to be accepted.
        :param community_id: ID of the community where the request is accepted.
        :return: A tuple containing a message dictionary and a status code.
        """
    try:
        deny_query_community_request(user_id, community_id)
        return {"message": "Community request denied successfully"}, 200
    except SQLAlchemyError:
        return {"error": "Database operation failed, unable to accept request"}, 500
    except Exception:
        return {"error": "An unexpected error occurred"}, 500


def manage_get_community_invitations(user_id):
    """
    Retrieves all community invitations for the authenticated user and returns them as a JSON array.
    :return: JSON array with all invitations or an error message
    """

    invites = get_query_community_invites(user_id)
    if invites is None or len(invites) == 0:
        return {"message": "No invites found"}, 404  # HTTP 404 Not Found might be more appropriate

    return {"invites": invites}, 200  # HTTP 200 OK


def manage_send_community_invite(user_id, community_id):
    """
        Creates a request for a user to join a community.

        :param community_id: ID of the community the user wants to join
        :param user_id: ID of the user making the request
        :return: JSON response indicating the outcome
        """
    try:
        community_query_invite(user_id, community_id)
        return {"message": "invite has been successfully send"}, 201
    except Exception as e:
        return {"error": str(e)}, 500


def manage_accept_community_invite(user_id, community_id):
    """
            Manages the acceptance of a community join request.

            :param user_id: ID of the user whose request is to be accepted.
            :param community_id: ID of the community where the request is accepted.
            :return: A tuple containing a message dictionary and a status code.
            """
    try:
        accept_query_community_invite(user_id, community_id)
        return {"message": "Community invite has been accepted"}, 200
    except SQLAlchemyError as e:
        # Log the error or handle it according to your error management strategy
        print(f"Database operation failed: {e}")
        return {"error": "Database operation failed, unable to accept request"}, 500
    except Exception as e:
        # Log unexpected errors and handle them accordingly
        print(f"Unexpected error occurred: {e}")
        return {"error": "An unexpected error occurred"}, 500


def manage_deny_community_invite(community_id, user_id):
    """
            Manages denying of a community invite.

            :param user_id: ID of the user whose request is to be accepted.
            :param community_id: ID of the community where the request is accepted.
            :return: A tuple containing a message dictionary and a status code.
            """
    try:
        deny_query_community_invite(user_id, community_id)
        return {"message": "Community invite has been denied"}, 200
    except SQLAlchemyError:
        return {"error": "Database operation failed, unable to accept request"}, 500
    except Exception:
        return {"error": "An unexpected error occurred"}, 500


def manage_add_community_user(user_id, community_id):
    try:
        query_add_community_user(user_id, community_id)
        return {"message": "User successfully added to the community"}, 201
    except Exception as e:
        return {"error": str(e)}, 500


def manage_remove_user_from_community(requester_user_id, user_id, community_id):
    try:
        query_remove_user_from_community(requester_user_id, user_id, community_id)
        return {"message": "User successfully removed from the community"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def manage_leave_community(user_id, community_id):
    try:
        query_leave_community(user_id, community_id)
        return {"message": "User successfully left the community"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def manage_community_promote_moderator(requester_id, user_id, community_id):
    try:
        query_community_user_promote(requester_id, user_id, community_id)
        return {"message": "User has been promoted to moderator"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def manage_community_demote_moderator(requester_id, user_id, community_id):
    try:
        query_community_user_demote(requester_id, user_id, community_id)
        return {"message": "User has been demoted from moderator"}, 200
    except Exception as e:
        return {"error": str(e)}, 500


def manage_community_change_owner(requester_id, user_id, community_id):
    try:
        query_community_user_change_owner(requester_id, user_id, community_id)
        return {"message": "User has been promoted to owner"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
