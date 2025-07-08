import http.client
import requests
import json
import pandas as pd

# ==== Import parameters' Values ====
df_param = pd.DataFrame(_arg1)

host = 'jooble.org'
key = 'JOOBLE_API_KEY'  # Replace with your Jooble API key
headers = {"Content-type": "application/json"}

all_jobs = []
page = 1
keyword = df_param['keyword'][0]
location = df_param['location'][0]

while len(all_jobs) < 120:
    # Create connection inside the loop to ensure fresh connection if needed
    connection = http.client.HTTPConnection(host)

    # Construct request body
    body_dict = {
        "keywords": keyword,
        "location": location,
        "page": str(page)
    }
    body = json.dumps(body_dict)

    # Send request
    connection.request('POST', '/api/' + key, body, headers)
    response = connection.getresponse()
    data = response.read().decode('utf-8')
    data_json = json.loads(data)
    
    jobs = data_json.get("jobs", [])
    
    # Stop if no jobs returned (API limit or end of results)
    if not jobs:
        print(f"No jobs found on page {page}, stopping early.")
        break

    all_jobs.extend(jobs)
    print(f"Retrieved {len(jobs)} jobs from page {page}. Total so far: {len(all_jobs)}")
    
    page += 1
    connection.close()

# Slice to keep only the first 120
all_jobs = all_jobs[:120]

# Convert to DataFrame
df = pd.DataFrame(all_jobs)

# --- Extract City and State from 'location' ---
# Assumes format: "City, ST" or "City, State"
# Will extract:
# - City as everything before the last comma
# - State as everything after the last comma
df[['City', 'State']] = df['location'].str.extract(r'^(.*?),\s*([A-Z]{2,})$', expand=True)

return df.astype(str).to_dict(orient="list")