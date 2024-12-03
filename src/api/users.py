from fastapi import APIRouter
import sqlalchemy
from src import database as db
from fastapi.responses import JSONResponse
router = APIRouter(
    prefix="/users",
    tags=['users']
)

@router.post("/create")
def create_user(first_name: str, last_name: str, ssn: int):
    with db.engine.begin() as connection:
        sql_dict = {
            'first_name': first_name,
            'last_name': last_name
        }
        sql_query_check = sqlalchemy.text("""
            SELECT 1
            FROM user_account
            WHERE first_name = :first_name AND last_name = :last_name
            """)
        exists = connection.execute(sql_query_check, sql_dict).fetchone()
        if(exists):
            response = {"Error": "User already exists"}
            return JSONResponse(response, status_code=409)


        # insert new user into users table and retrieve user_id
        sql_to_execute = """
            INSERT INTO user_account (first_name, last_name, ssn) 
            VALUES (:first_name, :last_name, :ssn) 
            RETURNING user_id
            """
        result = connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'first_name': first_name, 'last_name': last_name, 'ssn': ssn}
        )

        user_id = result.scalar()

        response = {"message": "User successfully created", "user_id": user_id}
        return JSONResponse(response, status_code= 201)


@router.delete("/remove")
def remove_user(user_id: int):
    with db.engine.begin() as connection:

        # remove row containing user_id
        sql_to_execute = """
            DELETE FROM user_account
            WHERE user_id = :user_id
        """
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})

        if result.rowcount == 0:
            response = {"Error": "User not found"}
            return JSONResponse(response, status_code= 400)

        response = {"message": "User removed successfully"}
        return JSONResponse(response, status_code= 200)

@router.post("/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id}")
def add_collaborator(playlist_id: int, current_user_id: int, collaborator_id: int):
    with db.engine.begin() as connection:

        # validate that playlist exists and belongs to current user
        sql_to_execute = """
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id AND user_id = :current_user_id
        """
        is_owner = connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'playlist_id': playlist_id, 'current_user_id': current_user_id}
        ).fetchone()

        # playlist does not belong to current user
        if not is_owner:
            return {"error": "Only the owner can add collaborators"}, 403

        # validate collaborator id
        collaborator_exists_query = """
                    SELECT 1
                    FROM user_account
                    WHERE user_id = :collaborator_id
                """
        collaborator_exists = connection.execute(
            sqlalchemy.text(collaborator_exists_query),
            {'collaborator_id': collaborator_id}
        ).fetchone()

        # collaborator id does not exist
        if not collaborator_exists:
            return {"error": "Collaborator ID does not exist"}, 404

        # check if the collaborator is already added to the playlist
        already_collaborator_query = """
                    SELECT 1
                    FROM playlist_collaborator
                    WHERE playlist_id = :playlist_id AND user_id = :collaborator_id
                """
        already_collaborator = connection.execute(
            sqlalchemy.text(already_collaborator_query),
            {'playlist_id': playlist_id, 'collaborator_id': collaborator_id}
        ).fetchone()

        # collaborator is already a collaborator
        if already_collaborator:
            return {"message": "Collaborator already exists for this playlist"}, 200

        # Add the collaborator
        add_collaborator_query = """
                    INSERT INTO playlist_collaborator (playlist_id, user_id)
                    VALUES (:playlist_id, :collaborator_id)
                """
        connection.execute(
            sqlalchemy.text(add_collaborator_query),
            {'playlist_id': playlist_id, 'collaborator_id': collaborator_id}
        )

    return {"message": "Collaborator added successfully"}


@router.delete("/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id}")
def remove_collaborator(playlist_id: int, current_user_id: int, collaborator_id: int):
    with db.engine.begin() as connection:
        # verify that playlist belongs to current user
        is_owner_query = """
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id AND user_id = :current_user_id
        """
        is_owner = connection.execute(
            sqlalchemy.text(is_owner_query),
            {'playlist_id': playlist_id, 'current_user_id': current_user_id}
        ).fetchone()

        # check if current user is a collaborator of the playlist
        is_self_query = """
            SELECT 1
            FROM playlist_collaborator
            WHERE playlist_id = :playlist_id AND user_id = :current_user_id
        """
        is_self = connection.execute(
            sqlalchemy.text(is_self_query),
            {'playlist_id': playlist_id, 'current_user_id': current_user_id}
        ).fetchone()

        # user is not:
        # - owner of playlist
        # - a collaborator of the playlist
        if not is_owner and not is_self:
            return {"error": "Only the playlist owner or the collaborator themselves can remove collaborators"}, 403

        # allow removal only if the current user is the owner or removing themselves
        if is_owner or (is_self and current_user_id == collaborator_id):
            delete_query = """
                DELETE FROM playlist_collaborator
                WHERE playlist_id = :playlist_id AND user_id = :collaborator_id
            """
            result = connection.execute(
                sqlalchemy.text(delete_query),
                {'playlist_id': playlist_id, 'collaborator_id': collaborator_id}
            )

            # collaborator to remove is not a collaborator on the playlist
            if result.rowcount == 0:
                return {"error": "Collaborator not found in this playlist"}, 404

            # successful removal of collaborator
            return {"message": "Collaborator removed successfully"}

       # insufficient permissions
        return {"error": "You are not authorized to remove this collaborator"}, 403


# change playlist name (only creator is allowed)
@router.patch("/{user_id}/playlists/{playlist_id}")
def change_playlist_name(current_user_id: int, playlist_id: int, new_name: str):

    with db.engine.begin() as connection:

        # validate user has playlist name changing auth
        user_allowed = connection.execute(sqlalchemy.text(
        """SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id AND user_id = :user_id"""
        ), {'user_id': current_user_id, 'playlist_id': playlist_id}).fetchone()

        # check
        if not user_allowed:
            return {"ERROR": "Invalid user_id for specified playlist_id"}, 400

        # update playlist name
        sql_to_execute = """
                         UPDATE playlist SET playlist_name = :new_name 
                         WHERE playlist_id = :playlist_id AND user_id = :user_id
                         """
        result = connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'new_name': new_name, 'playlist_id': playlist_id, 'user_id': current_user_id}
        )

        # check if row was updated
        if result.rowcount == 0:
            return {"error": "Playlist not found or not owned by the user"}, 404

        return {"message": "Playlist updated"}