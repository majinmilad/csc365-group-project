from fastapi import APIRouter, Depends, Request 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List

router = APIRouter(
    prefix="/collaborators",
    tags=['collaborators']
)

@router.post("/{user_id}/playlists/{playlist_id}/collaborators/add")
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

        # add the collaborator
        sql_to_execute = """
            INSERT INTO playlist_collaborator (playlist_id, user_id)
            VALUES (:playlist_id, :collaborator_id)
        """
        connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'playlist_id': playlist_id, 'collaborator_id': collaborator_id}
        )

    return {"message": "Collaborator added successfully"}


@router.delete("/{user_id}/playlists/{playlist_id}/collaborators/remove")
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
