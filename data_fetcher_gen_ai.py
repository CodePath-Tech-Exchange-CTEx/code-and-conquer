from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel
import json
import uuid 

# gen-ai-recommendation data fetcher module 
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



