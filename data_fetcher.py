#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################
import json
import os
from google.cloud import bigquery

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "daniel-reyes-uprm")
DATASET_ID = os.getenv("BQ_DATASET_ID", "iseGroupFour")


def _get_bq_client():
    return bigquery.Client(project=PROJECT_ID)


def _run_query(query, params=None):
    client = _get_bq_client()
    job_config = bigquery.QueryJobConfig(query_parameters=params or [])
    rows = client.query(query, job_config=job_config).result()
    return [dict(row.items()) for row in rows]


def _subject_icon(subject):
    icons = {
        "Computer Science": "💻",
        "Mathematics": "📐",
        "Biology": "🧬",
        "Chemistry": "🧪",
        "Physics": "🔭",
    }
    return icons.get(str(subject), "📚")


def get_user_profile(user_id):
    """
    Fetches a single user's profile from the Users table and their active
    group count from GroupMemberships — in a single query to minimise load time.

    Args
        user_id : str – Primary key from the Users table.

    Returns
        dict shaped for display_user_profile(), or None if the user is not found.
        Keys: first_name, last_name, major, year, institution, email, about_me,
              focus_subjects, groups_joined, study_hours, day_streak,
              weekly_availability.
    """
    # Single query: LEFT JOIN membership count so we only make one round trip
    # instead of two, cutting BigQuery cold-start latency in half.
    query = f"""
        SELECT
            u.first_name,
            u.last_name,
            u.major,
            u.education_level,
            u.institution,
            u.email,
            ANY_VALUE(u.preferences) AS preferences,
            ANY_VALUE(u.availability) AS availability,
            COUNT(gm.id) AS groups_joined
        FROM `{PROJECT_ID}.{DATASET_ID}.Users` u
        LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.GroupMemberships` gm
            ON gm.user_id = u.id AND gm.left_at IS NULL
        WHERE u.id = @user_id
        GROUP BY
            u.first_name, u.last_name, u.major, u.education_level,
            u.institution, u.email
        LIMIT 1
    """
    params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    rows = _run_query(query, params)

    if not rows:
        return None

    row = rows[0]

    preferences = row.get("preferences") or {}
    if isinstance(preferences, str):
        preferences = json.loads(preferences)

    availability = row.get("availability") or []
    if isinstance(availability, str):
        availability = json.loads(availability)

    return {
        "first_name":          row.get("first_name", ""),
        "last_name":           row.get("last_name", ""),
        "major":               row.get("major", ""),
        "year":                row.get("education_level", ""),
        "institution":         row.get("institution", ""),
        "email":               row.get("email", ""),
        "about_me":            preferences.get("about_me", ""),
        "focus_subjects":      preferences.get("focus_subjects", []),
        "groups_joined":       row.get("groups_joined", 0),
        "study_hours":         preferences.get("study_hours", 0),
        "day_streak":          preferences.get("day_streak", 0),
        "weekly_availability": availability,
    }


def get_my_groups(user_id):
    query = f"""
        WITH member_counts AS (
            SELECT group_id, COUNT(*) AS active_members
            FROM `{PROJECT_ID}.{DATASET_ID}.GroupMemberships`
            WHERE left_at IS NULL
            GROUP BY group_id
        )
        SELECT
            g.id AS group_id,
            g.name AS title,
            g.subject AS subject,
            g.mode AS mode,
            g.location_text AS location,
            g.capacity AS capacity,
            gs.day_of_week AS day_of_week,
            gs.start_time AS start_time,
            gs.end_time AS end_time,
            COALESCE(mc.active_members, 0) AS active_members
        FROM `{PROJECT_ID}.{DATASET_ID}.GroupMemberships` gm
        JOIN `{PROJECT_ID}.{DATASET_ID}.Groups` g
          ON gm.group_id = g.id
        LEFT JOIN `{PROJECT_ID}.{DATASET_ID}.GroupSchedules` gs
          ON g.id = gs.group_id
        LEFT JOIN member_counts mc
          ON g.id = mc.group_id
        WHERE gm.user_id = @user_id
          AND gm.left_at IS NULL
        ORDER BY g.updated_at DESC, g.created_at DESC
    """

    params = [bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    rows = _run_query(query, params)

    results = []
    for row in rows:
        day = row.get("day_of_week") or "TBD"
        start = row.get("start_time") or ""
        end = row.get("end_time") or ""

        if start and end:
            days_text = f"{day} {start}-{end}"
        else:
            days_text = day

        results.append({
            "group_id": row.get("group_id"),
            "title": row.get("title", ""),
            "icon": _subject_icon(row.get("subject")),
            "days": days_text,
            "mode": row.get("mode", "Unknown"),
            "location": row.get("location", "TBD"),
            "members": f'{row.get("active_members", 0)}/{row.get("capacity", 0)}',
        })

    return results