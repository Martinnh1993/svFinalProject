import logging

import werkzeug
from flask import request, jsonify
from flask_restful import Resource, reqparse
from scripts.handler.error_handler import catch_unexpected_error, catch_sql_errors, authenticate_firebase_id_token, \
    cache_decorator
from scripts.management.Community.community_managenment import community_manage_get_all_communities, \
    community_manage_create_community, community_manage_get_community_by_id, community_manage_update_community, \
    community_manage_delete_community, community_manage_add_banner, community_manage_update_banner, \
    community_manage_get_communities_by_user_id, community_manage_get_all_community_users


class CommunityUser(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, user_id=None):

        if user_id:
            return community_manage_get_communities_by_user_id(user_id)

        return community_manage_get_communities_by_user_id(request.current_user)



class Community(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, community_id=None):

        if community_id:
            return community_manage_get_community_by_id(community_id)
        else:
            return community_manage_get_all_communities(request.current_user)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='form', required=True, help='Name cannot be blank')
        parser.add_argument('image_path', type=werkzeug.datastructures.FileStorage, location='files', required=True,
                            help='Logo path cannot be blank')
        parser.add_argument('banner_path', type=werkzeug.datastructures.FileStorage, location='files', required=False)
        parser.add_argument('description', type=str, location='form', required=True, help='Description cannot be blank')
        parser.add_argument('street', type=str, location='form')
        parser.add_argument('city', type=str, location='form')
        parser.add_argument('country', type=str, location='form')
        parser.add_argument('timezone', type=str, location='form')
        parser.add_argument('longitude', type=float, location='form', required=True, help='Longitude cannot be blank')
        parser.add_argument('latitude', type=float, location='form', required=True, help='Latitude cannot be blank')
        parser.add_argument('is_private', type=bool, location='form', required=True,
                            help='isPrivate flag cannot be blank')
        parser.add_argument('is_closed', type=bool, location='form', required=True,
                            help='isClosed flag cannot be blank')
        args = parser.parse_args()

        logging.debug(f"Parsed arguments: {args}")

        return community_manage_create_community(args)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id):
        if not community_id:
            logging.error("Community ID is required for update.")
            return {"message": "Community ID is required for update."}, 400

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, location='form', required=False)
        parser.add_argument('image_path', type=werkzeug.datastructures.FileStorage, location='files', required=False)
        parser.add_argument('banner_path', type=werkzeug.datastructures.FileStorage, location='files', required=False)
        parser.add_argument('description', type=str, location='form', required=False)
        parser.add_argument('street', type=str, location='form', required=False)
        parser.add_argument('city', type=str, location='form', required=False)
        parser.add_argument('country', type=str, location='form', required=False)
        parser.add_argument('timezone', type=str, location='form', required=False)
        parser.add_argument('longitude', type=float, location='form', required=False)
        parser.add_argument('latitude', type=float, location='form', required=False)
        parser.add_argument('is_private', type=bool, location='form', required=False)
        parser.add_argument('is_closed', type=bool, location='form', required=False)
        args = parser.parse_args()

        updates = {key: value for key, value in args.items() if value is not None}
        logging.debug(f"Updates to be applied: {updates}")

        if not updates:
            logging.error("No updates provided")
            return {"message": "No updates provided"}, 400  # Add this return to stop further processing

        return community_manage_update_community(community_id, updates)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id):
        if not community_id:
            return jsonify({"message": "Community ID is required for deletion."}), 400

        return community_manage_delete_community(community_id, request.current_user)


class CommunityUsers(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, community_id):
        if not community_id:
            return jsonify({"message": "Community ID is required."}), 400

        return community_manage_get_all_community_users(community_id)


class CommunityBanner(Resource):
    @authenticate_firebase_id_token
    @catch_unexpected_error
    @catch_sql_errors
    def post(self, community_id):
        """
        Handles the initial upload of a banner.
        Requires authentication and handles exceptions.
        """
        if 'banner' not in request.files:
            return {"message": "No banner file provided"}, 400

        banner_file = request.files['banner']
        return community_manage_add_banner(community_id, banner_file)

    @authenticate_firebase_id_token
    @catch_unexpected_error
    @catch_sql_errors
    def put(self, community_id):
        """
        Handles updating an existing banner.
        Requires authentication and handles exceptions.
        """
        if 'banner' not in request.files:
            return {"message": "No banner file provided"}, 400

        banner_file = request.files['banner']
        return community_manage_update_banner(community_id, banner_file)
