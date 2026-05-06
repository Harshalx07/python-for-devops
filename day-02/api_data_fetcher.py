import requests
import json


# 1. Call the API
def fetch_posts():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    return response.json()


# 2. Extract meaningful information
def extract_data(posts):
    extracted = []
    for post in posts[:10]:  # take first 10 posts
        extracted.append({
            "id": post["id"],
            "userId": post["userId"],
            "title": post["title"],
            "body": post["body"]
        })
    return extracted


# 3. Print the processed output to terminal
def print_data(posts):
    print("Fetched Posts from JSONPlaceholder API")
    print("=" * 50)
    for post in posts:
        print(f"Post ID   : {post['id']}")
        print(f"User ID   : {post['userId']}")
        print(f"Title     : {post['title']}")
        print(f"Body      : {post['body'][:60]}...")
        print("-" * 50)


# 4. Save the processed data into a JSON file
def save_to_json(data, filename="output.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"\nData saved to {filename}")


# Main function
def main():
    raw_data = fetch_posts()
    processed_data = extract_data(raw_data)
    print_data(processed_data)
    save_to_json(processed_data)


if __name__ == "__main__":
    main()