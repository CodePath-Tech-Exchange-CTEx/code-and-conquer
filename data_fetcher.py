#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

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

def get_nearby_groups(user_id, search, lon, lat):
    query = """
    SELECT
      id,
      name,
      subject,
      location_text,
      ST_DISTANCE(
        location_geog,
        ST_GEOGPOINT(@lon, @lat)
      ) AS distance_meters
    FROM `daniel-reyes-uprm.iseGroupFour.Groups`
    WHERE location_geog IS NOT NULL
        AND (
        @search = "" OR
        LOWER(name) LIKE LOWER(CONCAT('%', @search, '%')) OR
        LOWER(subject) LIKE LOWER(CONCAT('%', @search, '%'))
        )
    ORDER BY distance_meters ASC
    LIMIT 20
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("lat", "FLOAT64", lat),
            bigquery.ScalarQueryParameter("lon", "FLOAT64", lon),
            bigquery.ScalarQueryParameter("search", "STRING", search)

        ]
    )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    return [dict(row) for row in results]