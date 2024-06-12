from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.engine.row import RowProxy

from scripts.handler.error_handler import catch_unexpected_error, catch_sql_errors, authenticate_firebase_id_token
from scripts.management.Community.member.community_member_managenment import manage_get_community_requests, \
    manage_create_community_request, manage_accept_community_request, manage_deny_community_request, \
    manage_deny_community_invite, manage_send_community_invite, \
    manage_get_community_request_by_id, manage_accept_community_invite, manage_add_community_user, \
    manage_remove_user_from_community, manage_leave_community, manage_community_promote_moderator, \
    manage_community_demote_moderator, manage_community_change_owner, manage_get_community_invitations


class CommunityRequests(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, community_id, user_id=None):
        if user_id:
            return manage_get_community_request_by_id(community_id, user_id)
        else:
            return manage_get_community_requests(community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self, community_id):
        return manage_create_community_request(community_id, request.current_user)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id, user_id=None):
        return manage_accept_community_request(user_id, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id, user_id=None):
        return manage_deny_community_request(user_id, community_id)


class CommunityInvites(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, user_id=None):
        if user_id:
            return manage_get_community_invitations(user_id)
        else:
            return manage_get_community_invitations(request.current_user)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self, community_id, user_id=None):
        return manage_send_community_invite(user_id, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id):
        return manage_accept_community_invite(request.current_user, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id):
        return manage_deny_community_invite(request.current_user, community_id)


class CommunityMembershipResource(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self, community_id, user_id=None):
        if user_id:
            return manage_add_community_user(request.current_user, community_id)
        else:
            return manage_add_community_user(user_id, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id):
        return manage_leave_community(request.current_user, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id, user_id=None):
        return manage_remove_user_from_community(request.current_user, user_id, community_id)


class CommunityMembershipRole(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self, community_id, user_id=None):
        if not user_id:
            return {"message": "User ID is required"}, 400

        return manage_community_promote_moderator(request.current_user, user_id, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id, user_id=None):
        return manage_community_demote_moderator(request.current_user, user_id, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id, user_id=None):
        return manage_community_change_owner(request.current_user, user_id, community_id)
