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
import uuid 

import vertexai
from vertexai.generative_models import GenerativeModel
import json

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

def _get_group_schedule(groups):
    for i in range(len(groups)):
        group_id = group.get("id")
        query = """
        SELECT
        day_of_week,
        start_time
        FROM `daniel-reyes-uprm.iseGroupFour.GroupSchedules`
        Where group_id = @group_id
        """
        params = [
            bigquery.ScalarQueryParameter("group_id", "STRING", group_id)
        ]
        groups[i]["schedule"] = _run_query(query, params)

def get_nearby_groups(user_id, search, filter, lon, lat):
    query = """
    SELECT
      id,
      name,
      subject,
      location_text,
      description,
      capacity,
      ST_DISTANCE(
        location_geog,
        ST_GEOGPOINT(@lon, @lat)
      ) AS distance_meters
    FROM `daniel-reyes-uprm.iseGroupFour.Groups`
    WHERE location_geog IS NOT NULL
        -- 1. Bulletproof Search Logic
        AND (
            @search IS NULL OR 
            @search = '' OR
            LOWER(name) LIKE LOWER(CONCAT('%', @search, '%')) OR
            LOWER(subject) LIKE LOWER(CONCAT('%', @search, '%')) OR
            LOWER(description) LIKE LOWER(CONCAT('%', @search, '%'))
        )
        
        -- 2. Bulletproof Filter Logic
        AND (
            @filter IS NULL OR 
            ARRAY_LENGTH(@filter) = 0 OR
            EXISTS (
                SELECT 1 
                FROM UNNEST(@filter) AS f 
                WHERE LOWER(subject) = LOWER(f)
            )
        )
        ORDER BY distance_meters ASC
        LIMIT 20
    """

    params=[
            bigquery.ScalarQueryParameter("lat", "FLOAT64", lat),
            bigquery.ScalarQueryParameter("lon", "FLOAT64", lon),
            bigquery.ScalarQueryParameter("search", "STRING", search),
            bigquery.ArrayQueryParameter("filter", "STRING", filter)
        ]

    query_job = _run_query(query, params)
    _get_group_schedule(query_job)

    return query_job


# -------------------------------------------------------------------------
# GEN-AI-RECOMMENDATION MODULE
# -------------------------------------------------------------------------

project="daniel-reyes-uprm"
table = "iseGroupFour"

dataset_id = f"{project}.{table}"

# Initialize vertex AI model
vertexai.init(project=project, location="us-central1")
model = GenerativeModel("gemini-2.5-flash")

def generate_recommended_groups_data(user_interests: str):
    prompt = f"""
    The user is interested in: {user_interests}.
    Generate 3 realistic study group recommendations.
    Return ONLY a JSON list of objects with these exact keys: 
    "major", "title", "match_pct", "keywords", "day_of_week", "start_time", "location".
    
    Example format:
    [
      {{
        "major": "CS", 
        "title": "Data Structures & Algorithms Hackers", 
        "match_pct": 95, 
        "keywords": ["Python", "Heaps", "LeetCode"], 
        "day_of_week": "Wednesday", 
        "start_time": "4:00 PM", 
        "location": "Jubilee Hall Study Room"
      }}
    ]
    """

    response = model.generate_content(
        prompt, 
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Convert the AI's string response into an actual Python list
    return json.loads(response.text)

def save_ai_generated_groups(user_id, ai_groups, dataset_id=dataset_id, default_capacity=5):
    """
    Takes the JSON list from Vertex AI and inserts it into BigQuery securely.

    Arg(s): user_id -> int representing who the recommendation is for
            ai_groups -> a list of groups recommended by AI 
    """
    client = bigquery.Client()
    
    # Generate ONE unique ID for this entire batch of recommendations
    recommendation_id = f"rec_{uuid.uuid4().hex[:12]}"
    
    # Insert the Parent Record into AIRecommendations
    parent_query = f"""
    INSERT INTO `{dataset_id}.AIRecommendations` 
    (id, user_id, generated_at, model_version)
    VALUES (@rec_id, @user_id, CURRENT_TIMESTAMP(), 'gemini-1.5-flash')
    """
    client.query(parent_query, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("rec_id", "STRING", recommendation_id),
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )).result()

    # Loop through each group and insert into the respective child tables
    for group in ai_groups:
        
        # Generate unique IDs for the child tables
        group_id = f"group_{uuid.uuid4().hex[:12]}"
        schedule_id = f"sch_{uuid.uuid4().hex[:12]}"
        detail_id = f"det_{uuid.uuid4().hex[:12]}"
        
        # --- Insert into Groups ---
        group_query = f"""
        INSERT INTO `{dataset_id}.Groups` 
        (id, name, subject, capacity, location_text)
        VALUES (@id, @name, @subject, @capacity, @location)
        """
        client.query(group_query, job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("id", "STRING", group_id),
                bigquery.ScalarQueryParameter("name", "STRING", group.get('title', 'Untitled')),
                bigquery.ScalarQueryParameter("subject", "STRING", group.get('major', 'General')),
                bigquery.ScalarQueryParameter("capacity", "INTEGER", default_capacity),
                bigquery.ScalarQueryParameter("location", "STRING", group.get('location', 'TBD'))
            ]
        )).result()

        # Insert into GroupSchedules
        schedule_query = f"""
        INSERT INTO `{dataset_id}.GroupSchedules`
        (id, group_id, day_of_week, start_time)
        VALUES (@sch_id, @group_id, @day, @start)
        """
        client.query(schedule_query, job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("sch_id", "STRING", schedule_id),
                bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
                bigquery.ScalarQueryParameter("day", "STRING", group.get('day_of_week', 'TBD')),
                bigquery.ScalarQueryParameter("start", "STRING", group.get('start_time', 'TBD'))
            ]
        )).result()

        # Insert into AIRecommendationDetails
        # Convert the python list into a JSON string for BigQuery
        features_json = json.dumps(group.get('keywords', []))
        
        rec_detail_query = f"""
        INSERT INTO `{dataset_id}.AIRecommendationDetails`
        (id, recommendation_id, group_id, match_pct, features)
        VALUES (@det_id, @rec_id, @group_id, @match, PARSE_JSON(@features))
        """
        client.query(rec_detail_query, job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("det_id", "STRING", detail_id),
                bigquery.ScalarQueryParameter("rec_id", "STRING", recommendation_id), # Links to parent!
                bigquery.ScalarQueryParameter("group_id", "STRING", group_id),
                bigquery.ScalarQueryParameter("match", "NUMERIC", group.get('match_pct', 0) / 100.0),
                bigquery.ScalarQueryParameter("features", "STRING", features_json)
            ]
        )).result()
        
    return True

def format_ai_data_for_frontend(ai_groups):
    formatted = []
    for group in ai_groups:
       
        day = group.get('day_of_week', 'TBD')
        start = group.get('start_time', 'TBD')
        time_str = f"{day}s {start}" if day != 'TBD' else "Time TBD"
        
        formatted.append({
            "major": group.get("major", "General"),
            "title": group.get("title", "New Study Group"),
            "match_pct": group.get("match_pct", 0),
            "keywords": group.get("keywords", []),
            "time": time_str,
            "location": group.get("location", "TBD"),
            "members": "0/5" 
        })
    return formatted

def get_final_recommendations(user_id, interests):
    # 1. Try to get existing recommendations from the DB
    db_results = get_study_group_recommendations(user_id)
    
    if db_results:
        print("DEBUG: Found existing matches in Database.")
        return db_results
    
    # 2. If DB is empty, generate with AI
    print("DEBUG: Database empty. Calling Vertex AI...")
    try:
        ai_generated_data = generate_recommended_groups_data(interests)
        
        # 3. Save that AI response into the database (for next time)
        save_ai_generated_groups(user_id, ai_generated_data)
        
        # 4. FIX: Instead of calling the DB again, format the AI data and return it now!
        print(f"DEBUG: Success! Displaying {len(ai_generated_data)} AI matches immediately.")
        return format_ai_data_for_frontend(ai_generated_data)

    except Exception as e:
        print(f"ERROR during AI flow: {e}")
        return []


def get_study_group_recommendations(user_id: str):

    # Initialize the BigQuery client
    client = bigquery.Client()

    query = f"""
    -- creates temporary mini-table that holds on data/information for a split second; the userid 
    WITH LatestRec AS(
        SELECT id 
        FROM `{dataset_id}.AIRecommendations`
        WHERE user_id = @user_id
        ORDER BY generated_at DESC
        LIMIT 1
    ),

    -- count people in every group to show (number of available positions in a group in recommendation card)
    MemberCounts AS (
        SELECT 
            group_id, 
            COUNT(user_id) AS current_member_count
        FROM `{dataset_id}.GroupMemberships`
        GROUP BY group_id
    )

    -- final query
    SELECT 
        g.id AS group_id,
        g.subject,
        g.name AS group_name,
        ard.match_pct,
        ard.features,
        gs.day_of_week,
        gs.start_time,
        g.location_text,
        COALESCE(mc.current_member_count, 0) AS current_members, -- If the answer is unknown, just make it a 0.
        g.capacity
        
    FROM LatestRec lr
    JOIN `{dataset_id}.AIRecommendationDetails` ard 
        ON lr.id = ard.recommendation_id
    JOIN `{dataset_id}.Groups` g 
        ON ard.group_id = g.id
    LEFT JOIN `{dataset_id}.GroupSchedules` gs 
        ON g.id = gs.group_id
    LEFT JOIN MemberCounts mc 
        ON g.id = mc.group_id
        
    ORDER BY ard.match_pct DESC;
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id) # prevents SQL injection
        ]
    )

    # executes the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    # format the outputs for our frontend
    formatted_recommendations = []
    
    for row in results:
        # Calculate the raw number for match percentage (e.g., 98)
        # Because the frontend adds the "% match" text
        raw_match_pct = int(row.match_pct * 100) if row.match_pct <= 1 else int(row.match_pct)
        
        # Combine day and time safely
        if row.day_of_week and row.start_time:
            time_str = f"{row.day_of_week}s {row.start_time}"
        else:
            time_str = "Time TBD"

        # These keys now PERFECTLY match: create_match_card(major, title, match_pct, keywords, time, location, members)
        formatted_recommendations.append({
            "major": row.subject,             
            "title": row.group_name,            
            "match_pct": raw_match_pct,       
            "keywords": row.features,               
            "time": time_str,             
            "location": row.location_text,      
            "members": f"{row.current_members}/{row.capacity}" 
        })

    return formatted_recommendations #(generated by Gemini)

# ACCOUNT SETTINGS MODULE
def get_user_identity_data(user_id: str):
    """
    Fetches only public-facing identity data and displays in the account settings
    """
    client = bigquery.Client(project="daniel-reyes-uprm")
    
    # We select only the ID and Email
    query = """
        SELECT id, email
        FROM `daniel-reyes-uprm.iseGroupFour.Users`
        WHERE id = @user_id
        LIMIT 1
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.to_dataframe()
        
        if not results.empty:
            return results.iloc[0].to_dict()
        return None
        
    except Exception as e:
        print(f"Fetch Error: {e}")
        return None

