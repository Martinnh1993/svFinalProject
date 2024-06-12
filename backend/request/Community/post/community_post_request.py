import logging

import werkzeug
from flask import request, jsonify
from flask_restful import Resource, reqparse

from scripts.handler.error_handler import catch_unexpected_error, catch_sql_errors, authenticate_firebase_id_token
from scripts.management.Community.post.community_post_managenment import manage_get_community_post_by_id, \
    manage_get_all_community_user_posts, manage_get_all_community_posts, manage_create_community_post, \
    manage_update_community_post, manage_delete_community_post, manage_hide_community_post, manage_show_community_post


class CommunityPostsResource(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, community_id=None, user_id=None):
        if user_id:
            # Fetch all posts for a user across communities
            return manage_get_all_community_user_posts(user_id)
        else:
            # Fetch all posts within a community
            return manage_get_all_community_posts(community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, post_id, action):
        if action == 'hide':
            return manage_hide_community_post(post_id)
        elif action == 'show':
            return manage_show_community_post(post_id)
        else:
            return {"message": "Invalid action"}, 400


class CommunityPostResource(Resource):
    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def get(self, community_id=None, post_id=None):
        # Fetch a specific post by ID
        return manage_get_community_post_by_id(community_id,post_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def post(self, community_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str, location='form', required=True, help='Description cannot be blank')
        parser.add_argument('image_path', type=werkzeug.datastructures.FileStorage, location='files', required=False)
        args = parser.parse_args()

        logging.debug(f"Parsed arguments: {args}")
        return manage_create_community_post(args, community_id)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def put(self, community_id=None, post_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('description', help='Description of the post.')
        parser.add_argument('image_path', help='New image path for the post.')
        args = parser.parse_args()
        updates = {key: value for key, value in args.items() if value is not None}
        return manage_update_community_post(community_id, post_id, updates)

    @catch_unexpected_error
    @catch_sql_errors
    @authenticate_firebase_id_token
    def delete(self, community_id=None, post_id=None):
        return manage_delete_community_post(community_id, post_id)
