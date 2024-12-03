from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/collaborators",
    tags=['collaborators']
)

@router.post("/{user_id}/playlists/{playlist_id}/add")
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


@router.delete("/{user_id}/playlists/{playlist_id}/remove")
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
