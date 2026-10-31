def fetch_with_retry(api_client, endpoint, max_attempts=5):
    attempt = 0
    while attempt < max_attempts:
        response = api_client.call(endpoint)
        if response.status_code == 200:
            return response.data
        attempt += 1  # Fixed: Increment counter each attempt
    return None
