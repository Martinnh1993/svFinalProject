from sqlalchemy import text
from flask import request

from sqlalchemy.orm import sessionmaker

from scripts.management.Community.community_managenment import upload_community_assets
from scripts.modules.buckets.buckets import bucket_upload_file
from scripts.modules.firebase.firebase_buckets import community_firebase_bucket_upload_file
from scripts.modules.mysql.Communities.post.community_post_queries import query_get_community_post_by_id, \
    query_get_all_community_user_posts, query_get_all_community_posts, query_create_community_post, \
    query_update_community_post, query_delete_community_post, query_hide_community_post, query_show_community_post
from scripts.setup.db_setup import engine

Session = sessionmaker(bind=engine)


def manage_get_all_community_user_posts(user_id):
    try:
        posts = query_get_all_community_user_posts(user_id)
        if posts:
            return posts, 200
        else:
            return {"message": "No posts found for this user"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


def manage_get_community_post_by_id(community_id, post_id):
    try:
        post = query_get_community_post_by_id(post_id)
        if post:
            return post, 200
        else:
            return {"message": "Post not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


def manage_get_all_community_posts(community_id):
    try:
        posts = query_get_all_community_posts(community_id)
        if posts:
            return posts, 200
        else:
            return {"message": "No posts found in this community"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


def manage_create_community_post(args, community_id):
    """
    Creates a new community post using the provided details.
    Optionally handles image uploads if an image is provided.

    Parameters:
        args (dict): Dictionary containing 'description' and optionally 'image_path'.
        community_id (int): The ID of the community to which the post belongs.
    """
    session = Session()
    try:
        session.begin()
        # Fetch the current user's ID from request context or args
        user_id = args.get('user_id', request.current_user)

        post_id = query_create_community_post(
            session,
            user_id=user_id,
            community_id=community_id,
            description=args['description']
        )

        # Check if an image was provided and upload it
        if 'image_path' in args and args['image_path']:
            upload_results = upload_community_post_image(community_id, args['image_path'], post_id)

            if 'imagePath' not in upload_results[0] or upload_results[1] != 200:
                session.rollback()  # Rollback the transaction if the image upload fails
                return {"message": "Failed to upload image", "error": upload_results[0].get('message', 'Unknown error')}, 500

            imageUrl = upload_results[0].get('imagePath')

            # Update the community post record with the image URL
            session.execute(
                text("UPDATE communityPost SET communityPost_imagePath = :imageUrl WHERE communityPost_postId = :post_id"),
                {'imageUrl': imageUrl, 'post_id': post_id}
            )
        else:
            imageUrl = None

        session.commit()  # Commit the transaction if all operations succeed
        return {"message": "Post created successfully", "imagePath": imageUrl}, 201

    except Exception as e:
        session.rollback()
        return {"message": str(e)}, 500


def manage_update_community_post(post_id, updates):
    """
    Update a community post's attributes based on the provided updates json.
    """
    if not post_id:
        return {"message": "Post ID is required for updates."}, 400

    try:
        query_update_community_post(post_id, updates)
        return {"message": "Post updated successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500


def manage_delete_community_post(post_id):
    """
    Manages the deletion of a community post.
    """
    try:
        query_delete_community_post(post_id)
        return {"message": "Post deleted successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500


def manage_hide_community_post(post_id):
    """
    Manages the hiding of a community post.
    """
    try:
        query_hide_community_post(post_id)
        return {"message": "Post hidden successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500


def manage_show_community_post(post_id):
    """
    Manages the showing of a previously hidden community post.
    """
    try:
        query_show_community_post(post_id)
        return {"message": "Post shown successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500


def upload_community_post_image(community_id, image, post_id):
    """
    Uploads community logo and banner images to Firebase and another storage bucket, and updates community details with new image URLs.

    Parameters:
        community_id (int): The ID of the community to update.
        args (dict): Dictionary containing 'image_path' and 'banner_path' keys with file storage objects as values.

    Returns:
        dict: Result message indicating success or failure, including HTTP status codes.
        :param image:
        :param community_id:
        :param post_id:
    """
    try:
        # Construct new paths for storing the images using the community ID
        image_bucket_filename = f"communities/{community_id}/posts/communityPost{post_id}.jpg"

        # Upload the logo to Firebase and another bucket, and retrieve the URL
        image_url = community_firebase_bucket_upload_file(image, image_bucket_filename)
        bucket_upload_file(image, image_bucket_filename)

        # Check if either URL failed to be retrieved (assuming None as failure)
        if image_url is None:
            failure_message = "Failed to upload " + ("logo." if image_url is None else "banner.")
            return {"message": failure_message}, 500

        # Successful upload response
        return {
            "message": "Assets uploaded successfully.",
            "imagePath": image_url,
        }, 200

    except KeyError as e:
        # Handle missing keys in the args dictionary
        return {"message": f"Missing key: {e.args[0]} - required image path or banner path not provided."}, 400
    except Exception as e:
        # General exception handling for any other unforeseen errors
        return {"message": f"An error occurred: {str(e)}"}, 500
