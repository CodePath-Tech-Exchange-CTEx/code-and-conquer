from supabase import create_client

SUPABASE_URL = "https://yanpzvpggwhwygbxwond.supabase.co"
SUPABASE_KEY = "sb_publishable_k8QVgMpZzk8pysUfpXRm0Q_vGtaNqD7"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test insert
supabase.table("messages").insert({
    "group_id": "cs_genai",
    "sender_id": "user_123",
    "content": "Hello from Supabase!"
}).execute()

# Test fetch
res = supabase.table("messages").select("*").eq("group_id", "cs_genai").execute()
print(res.data)