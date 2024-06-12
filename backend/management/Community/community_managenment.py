import json
import logging
import traceback
from sqlalchemy import text  # Correct import for text function to use in query
import cgitb;

cgitb.enable()  # Enables detailed traceback in web browser environments
from urllib.parse import urlparse
from flask import request
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError

from scripts.constants.http_response_msg import ERROR_UNEXPECTED, ERROR_SQL_DB, SUCCESSFUL_PROFILE_PIC_GET, \
    SUCCESSFUL_COMMUNITY_LOGO
from scripts.constants.http_status_codes import HTTP_400_BAD_REQUEST
from scripts.handler.error_handler import UnexpectedError
from scripts.modules.buckets.buckets import bucket_upload, bucket_upload_file, bucket_delete

from scripts.modules.firebase.firebase_buckets import firebase_bucket_delete_file, firebase_bucket_upload_file, \
    community_firebase_bucket_upload_file
from scripts.modules.mysql.Communities.community_queries import community_query_new_community, \
    community_query_get_community_by_id, community_query_get_all_communities, community_query_update_community, \
    community_query_delete_community, community_query_get_communities_by_user_id, \
    community_query_get_all_community_users, Session, community_query_add_banner, community_query_update_banner

from scripts.setup.db_setup import dbsession, Community, User
from scripts.utils import utils_check_file_in_form, utils_check_in_object, utils_check_if_int, utils_check_if_bool, \
    utils_parse_bool, utils_get_current_time, community_folder_bucket


def community_manage_get_communities_by_user_id(user_id):
    try:
        community_data = community_query_get_communities_by_user_id(user_id)
        if community_data is None:
            # No data found for the user ID provided
            return {"message": "No communities found for the provided user ID"}, 404

        # Data successfully retrieved and valid
        return community_data, 200

    except Exception as e:
        # Catch any unexpected errors during the database query or data processing
        return {"message": f"An error occurred while retrieving communities: {str(e)}"}, 500


def community_manage_get_community_by_id(community_id):
    """
    Retrieves the community with the given ID and returns it as a JSON object.

    :param community_id: ID of the community to look up
    :return: JSON object with information about the community or an error message
    """
    community = community_query_get_community_by_id(community_id)
    if community is None:
        return {"message": "No community found with the provided ID"}, 400  # HTTP 400 Bad Request

    return community, 200  # HTTP 200 OK


def community_manage_get_all_communities(user_id):
    """
    Retrieves all communities from the database and returns them as a JSON array.
    :return: JSON array with all communities, or error message
    """
    communities = community_query_get_all_communities(user_id)
    if communities is None or len(communities) == 0:
        return {"message": "No communities found"}, 400  # HTTP 400 Bad Request

    # Assuming each community data is already in the appropriate format
    # If you need to process links or other properties, you would do it here

    return communities, 200  # HTTP 200 OK


def community_manage_create_community(args):
    """
    Creates a new community using the provided details, then uploads an image and updates the community entry.
    The community creation is rolled back only if the logo upload fails.
    """
    session = Session()
    try:
        session.begin()  # Start transaction
        community_id = community_query_new_community(
            session,
            user_id=request.current_user,
            name=args['name'],
            imagePath=None,
            bannerPath=None,
            description=args['description'],
            street=args['street'],
            city=args['city'],
            country=args['country'],
            timezone=args['timezone'],
            longitude=args['longitude'],
            latitude=args['latitude'],
            is_private=args['is_private'],
            is_closed=args['is_closed']
        )

        # Call the function to handle image uploads and retrieve results
        upload_results = upload_community_assets(community_id, args)

        # Check specifically if the logo upload failed
        if 'imagePath' not in upload_results[0] or upload_results[1] != 200:
            session.rollback()  # Rollback the transaction if logo upload fails
            return {"message": "Failed to upload logo", "error": upload_results[0].get('message', 'Unknown error')}, 500

        # Proceed if logo upload succeeds; check banner upload separately
        imageUrl = upload_results[0].get('imagePath')
        bannerUrl = upload_results[0].get('bannerPath')

        # It's okay if the banner upload fails; we proceed with updating the community details for the logo only
        result = session.execute(
            text(
                "UPDATE community SET community_imagePath = :imageUrl, community_bannerPath = :bannerPath WHERE community_id = :community_id "),
            {'imageUrl': imageUrl, 'bannerPath': bannerUrl, 'community_id': community_id}
        )
        print(result)
        session.commit()  # Commit the transaction if logo is successfully uploaded

        return {"message": "Community created successfully", "imagePath": imageUrl, "bannerPath": bannerUrl}, 200

    except KeyError as e:
        session.rollback()
        return {"message": f"Missing key: {e}"}, 400
    except Exception as e:
        session.rollback()
        return {"message": str(e)}, 500
    finally:
        session.close()


def community_manage_update_community(community_id, updates):
    logging.debug(f"Managing update for community ID: {community_id} with updates: {updates}")

    # Initialize optional variables with default values
    image_url = None
    banner_url = None

    # Handle image upload if 'image_path' is provided in the updates
    if 'image_path' in updates:
        logo_bucket_file = updates['image_path']
        logo_bucket_filename = f"communities/{community_id}/logo/{community_id}_logo.jpg"
        image_url = community_firebase_bucket_upload_file(logo_bucket_file, logo_bucket_filename)
        bucket_upload_file(logo_bucket_file, logo_bucket_filename)  # Assuming this is also necessary

        if image_url is None:
            logging.error("Failed to upload new logo.")
            return {"message": "Failed to upload new logo"}, 500
        updates['imagePath'] = image_url  # Update the imagePath in the updates dictionary
        updates.pop('image_path')  # Remove the original key after processing

    # Handle banner upload if 'banner_path' is provided in the updates
    if 'banner_path' in updates:
        banner_bucket_file = updates['banner_path']
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"
        banner_url = community_firebase_bucket_upload_file(banner_bucket_file, banner_bucket_filename)
        bucket_upload_file(banner_bucket_file, banner_bucket_filename)  # Assuming this is also necessary

        if banner_url is None:
            logging.error("Failed to upload new banner.")
            return {"message": "Failed to upload new banner"}, 500
        updates['bannerPath'] = banner_url  # Update the bannerPath in the updates dictionary
        updates.pop('banner_path')  # Remove the original key after processing

    # Proceed with the community update in the database
    try:
        community_query_update_community(community_id, updates)
        logging.debug("Community update successful.")

        # Prepare the response dictionary
        response = {"message": "Community updated successfully"}
        if image_url is not None:
            response["imagePath"] = image_url
        if banner_url is not None:
            response["bannerPath"] = banner_url

        return response, 200

    except Exception as e:
        logging.error(f"Error in community_manage_update_community: {e}")
        return {"message": str(e)}, 500


def community_manage_delete_community(community_id, id_token: str):
    """
    Manages the deletion of a community and its associated assets, including images and banners.
    """
    try:
        # Construct the paths for the logo and banner files
        logo_bucket_filename = f"communities/{community_id}/logo/{community_id}_logo.jpg"
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"

        bucket_delete(logo_bucket_filename)
        bucket_delete(banner_bucket_filename)

        # Attempt to delete the logo and banner from Firebase
        firebase_bucket_delete_file(logo_bucket_filename)
        firebase_bucket_delete_file(banner_bucket_filename)

        # Invoke your community deletion query function
        community_query_delete_community(community_id, id_token)

        # Any additional logic to handle further asset deletion or cleanup post-deletion
        # (if applicable and not handled by the stored procedure)

        return {"message": "Community deleted successfully"}, 200
    except Exception as e:
        return {"message": str(e)}, 500


def community_manage_get_all_community_users(community_id):
    """
    Retrieves the community users with the given ID and returns it as a JSON object.

    :param community_id: ID of the community to look up
    :return: JSON object with information about the community users or an error message
    """
    community_users = community_query_get_all_community_users(community_id)
    if community_users is None:
        return {"message": "No community found with the provided ID"}, 400  # HTTP 400 Bad Request

    return community_users, 200  # HTTP 200 OK


import logging


def community_manage_add_banner(community_id, banner_file):
    """
    Handles the uploading of a new banner image to a community.
    """
    if not banner_file:
        return {"message": "No banner file provided"}, 400

    # Construct a unique filename for the banner
    banner_filename = f"communities/{community_id}/banner/{banner_file.filename}"

    try:
        # Extract the original filename from the uploaded file
        banner_bucket_file = banner_file

        # Construct the new path in the desired directory structure using community ID
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"

        # Upload the banner to Firebase and get the URL
        bannerUrl = community_firebase_bucket_upload_file(banner_bucket_file, banner_bucket_filename)
        bucket_upload_file(banner_bucket_file, banner_bucket_filename)

        if bannerUrl is None:
            logging.error("Failed to upload new banner.")
            return {"message": "Failed to upload new banner"}, 500

        # Update the community entry with the new banner URL
        community_query_add_banner(community_id, bannerUrl)
        logging.debug(f"Community update successful with new banner URL: {bannerUrl}")
        return {"message": "Community updated successfully", "bannerPath": bannerUrl}, 200

    except Exception as e:
        logging.error(f"Error in community_manage_add_banner: {e}")
        return {"message": str(e)}, 500


def community_manage_update_banner(community_id, banner_file):
    """
        Handles the uploading of a new banner image to a community.
        """
    if not banner_file:
        return {"message": "No banner file provided"}, 400

    # Construct a unique filename for the banner
    banner_filename = f"communities/{community_id}/banner/{banner_file.filename}"

    try:
        # Extract the original filename from the uploaded file
        banner_bucket_file = banner_file

        # Construct the new path in the desired directory structure using community ID
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"

        # Upload the banner to Firebase and get the URL
        bannerUrl = community_firebase_bucket_upload_file(banner_bucket_file, banner_bucket_filename)
        bucket_upload_file(banner_bucket_file, banner_bucket_filename)

        if bannerUrl is None:
            logging.error("Failed to upload new banner.")
            return {"message": "Failed to upload new banner"}, 500

        # Update the community entry with the new banner URL
        community_query_update_banner(community_id, bannerUrl)
        logging.debug(f"Community update successful with new banner URL: {bannerUrl}")
        return {"message": "Community updated successfully", "bannerPath": bannerUrl}, 200

    except Exception as e:
        logging.error(f"Error in community_manage_add_banner: {e}")
        return {"message": str(e)}, 500


def get_community_image_path(community_id):
    """
    Retrieves the current image path for the specified community ID.
    :param community_id: ID of the community.
    :return: A dictionary with the message and the image path, or raises an error if not found.
    """
    try:
        # Construct the query to retrieve the image path from the community table
        query = dbsession.query(Community.community_imagePath).filter_by(community_id=community_id)

        # Execute the query and fetch one result
        imageUrl = dbsession.execute(query).fetchone()
        print('p pic', imageUrl)

        # Check if the query returned a result
        if imageUrl is None:
            return {"message": "Community not found", "imageUrl": None}

        # profile_pic is a tuple, so access the first element to get the image path
        image_path = imageUrl[0] if imageUrl else None

        # Return the result in a dictionary
        return {
            "message": "Successful community logo retrieval",
            "imageUrl": image_path
        }
    except exc.SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        raise SQLAlchemyError("Error occurred in SQL Database")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        raise UnexpectedError("An unexpected error occurred")


def extract_path_from_url(url):
    """
    Extracts and returns the path from a full GCS URL, stripping the domain and bucket name.
    """
    parsed = urlparse(url)
    # Extract the path component from the URL
    path = parsed.path

    # Strip the leading '/' and the bucket name if present
    if path.startswith('/social-vibes-user-content/'):
        # Remove the leading '/' and the bucket name
        return path[len('/social-vibes-user-content/'):]  # This removes the bucket name part
    return None


def upload_community_assets(community_id, args):
    """
    Uploads community logo and banner images to Firebase and another storage bucket, and updates community details with new image URLs.

    Parameters:
        community_id (int): The ID of the community to update.
        args (dict): Dictionary containing 'image_path' and 'banner_path' keys with file storage objects as values.

    Returns:
        dict: Result message indicating success or failure, including HTTP status codes.
    """
    try:
        # Extract the file storage objects from the provided arguments
        logo_bucket_file = args['image_path']
        banner_bucket_file = args['banner_path']

        # Construct new paths for storing the images using the community ID
        logo_bucket_filename = f"communities/{community_id}/logo/{community_id}_logo.jpg"
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"

        # Upload the logo to Firebase and another bucket, and retrieve the URL
        image_url = community_firebase_bucket_upload_file(logo_bucket_file, logo_bucket_filename)
        bucket_upload_file(logo_bucket_file, logo_bucket_filename)

        # Upload the banner to Firebase and another bucket, and retrieve the URL
        banner_url = community_firebase_bucket_upload_file(banner_bucket_file, banner_bucket_filename)
        bucket_upload_file(banner_bucket_file, banner_bucket_filename)

        # Check if either URL failed to be retrieved (assuming None as failure)
        if image_url is None or banner_url is None:
            failure_message = "Failed to upload " + ("logo." if image_url is None else "banner.")
            return {"message": failure_message}, 500

        # Successful upload response
        return {
            "message": "Assets uploaded successfully.",
            "imagePath": image_url,
            "bannerPath": banner_url
        }, 200

    except KeyError as e:
        # Handle missing keys in the args dictionary
        return {"message": f"Missing key: {e.args[0]} - required image path or banner path not provided."}, 400
    except Exception as e:
        # General exception handling for any other unforeseen errors
        return {"message": f"An error occurred: {str(e)}"}, 500


def delete_community_assets(community_id):
    """
    Deletes community logo and banner images from Firebase and another storage bucket.

    Parameters:
        community_id (int): The ID of the community whose assets are to be deleted.

    Returns:
        dict: Result message indicating success or failure, including HTTP status codes.
    """
    try:
        # Construct paths for the stored images using the community ID
        logo_bucket_filename = f"communities/{community_id}/logo/{community_id}_logo.jpg"
        banner_bucket_filename = f"communities/{community_id}/banner/{community_id}_banner.jpg"

        # Delete the logo from Firebase and another bucket
        firebase_bucket_delete_file(logo_bucket_filename)
        bucket_delete(logo_bucket_filename)

        # Delete the banner from Firebase and another bucket
        firebase_bucket_delete_file(banner_bucket_filename)
        bucket_delete(banner_bucket_filename)

        # Successful deletion response
        return {"message": "Assets deleted successfully."}, 200

    except KeyError as e:
        # Handle missing keys in the args dictionary
        return {"message": f"Missing key: {e.args[0]} - required image path or banner path not provided."}, 400
    except Exception as e:
        # General exception handling for any other unforeseen errors
        return {"message": f"An error occurred: {str(e)}"}, 500
