import json
import os
from google.cloud import bigquery
import uuid 
from backend.data_fetcher import PROJECT_ID, DATASET_ID

import vertexai
from vertexai.generative_models import GenerativeModel
import json

from datetime import datetime


def create_group(user_id: str, name: str, description: str, subject: str, capacity: int, mode: str, visibility: str, location_text: str) -> None:
    """
    Prepares the data and unique IDs before sending it to the database query function.
    """
    # 1. Generate unique identifiers for the new group and membership
    new_group_id = f"group-uuid-{uuid.uuid4()}"
    new_membership_id = f"gm-{uuid.uuid4()}"
    
    # 2. Get the current UTC timestamp matching BigQuery's expected format
    current_timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # 3. Pass the data to the SQL execution function
    insert_group_into_db(
        group_id=new_group_id,
        user_id=user_id,
        membership_id=new_membership_id,
        name=name,
        description=description,
        subject=subject,
        capacity=capacity,
        mode=mode,
        visibility=visibility,
        location_text=location_text,
        timestamp=current_timestamp
    )


def insert_group_into_db(group_id, user_id, membership_id, name, description, subject, capacity, mode, visibility, location_text, timestamp) -> None:
    """
    Constructs and executes the SQL query to insert a group and its owner into BigQuery.
    """
    client = bigquery.Client(project=f"{PROJECT_ID}")
    
    query = f"""
    BEGIN TRANSACTION;

    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.Groups` 
    (id, name, description, subject, created_by, capacity, location_text, mode, visibility, created_at, updated_at)
    VALUES (
        @group_id, 
        @name, 
        @description, 
        @subject, 
        @user_id, 
        @capacity, 
        @location_text, 
        @mode, 
        @visibility, 
        TIMESTAMP(@timestamp), 
        TIMESTAMP(@timestamp)
    );

    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.GroupMemberships` 
    (id, user_id, group_id, role, joined_at)
    VALUES (
        @membership_id, 
        @user_id, 
        @group_id, 
        'owner', 
        TIMESTAMP(@timestamp)
    );

    COMMIT TRANSACTION;
    """
    
    # Map the Python variables to the @parameters in the query
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
            bigquery.ScalarQueryParameter("name", "STRING", name),
            bigquery.ScalarQueryParameter("description", "STRING", description),
            bigquery.ScalarQueryParameter("subject", "STRING", subject),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("capacity", "INT64", capacity),
            bigquery.ScalarQueryParameter("location_text", "STRING", location_text),
            bigquery.ScalarQueryParameter("mode", "STRING", mode),
            bigquery.ScalarQueryParameter("visibility", "STRING", visibility),
            bigquery.ScalarQueryParameter("membership_id", "STRING", membership_id),
            bigquery.ScalarQueryParameter("timestamp", "STRING", timestamp),
        ]
    )

    # 2. Execute the query and wait for it to finish
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # .result() makes Python wait until the database confirms the insert
    except Exception as e:
        # It's highly recommended to print or log the error so you can see if BigQuery rejects the insert
        print(f"BigQuery Insert Failed: {e}")
        raise e

def join_group(user_id: str, group_id: str) -> None:

    if check_user_membership(user_id, group_id):
        return

    client = bigquery.Client(project=f"{PROJECT_ID}")
    membership_id = f"gm-{uuid.uuid4()}"
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    query = f"""
    BEGIN TRANSACTION;

    INSERT INTO `{PROJECT_ID}.{DATASET_ID}.GroupMemberships` 
    (id, user_id, group_id, role, joined_at)
    VALUES (
        @membership_id, 
        @user_id, 
        @group_id, 
        'member', 
        TIMESTAMP(@timestamp)
    );

    COMMIT TRANSACTION;
    """

    # Map the Python variables to the @parameters in the query
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("membership_id", "STRING", membership_id),
            bigquery.ScalarQueryParameter("timestamp", "STRING", timestamp),
        ]
    )

    # 2. Execute the query and wait for it to finish
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()  # .result() makes Python wait until the database confirms the insert
    except Exception as e:
        # It's highly recommended to print or log the error so you can see if BigQuery rejects the insert
        print(f"BigQuery Insert Failed: {e}")
        raise e

def check_user_membership(user_id: str, group_id: str) -> bool:
    """
    Checks if a user is currently an active member of a specific group.
    Returns True if they are in the group, False otherwise.
    """
    client = bigquery.Client(project=f"{PROJECT_ID}")
    
    query = f"""
        SELECT 1 
        FROM `{PROJECT_ID}.{DATASET_ID}.GroupMemberships`
        WHERE user_id = @user_id 
          AND group_id = @group_id 
          AND left_at IS NULL
        LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        # If the results list has at least one row, the user is an active member
        return len(results) > 0
        
    except Exception as e:
        print(f"BigQuery Membership Check Failed: {e}")
        raise e

def leave_group(user_id: str, group_id: str) -> None:
    pass