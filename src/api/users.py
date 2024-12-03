from fastapi import APIRouter, Depends, Request 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List

router = APIRouter(
    prefix="/users",
    tags=['users']
)

@router.post("/create")
def create_user(first_name: str, last_name: str, ssn: int):
    with db.engine.begin() as connection:

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

        return {"user_id": user_id}


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
            return {"error": "User not found"}, 404

        return {"message": "User removed successfully"}

