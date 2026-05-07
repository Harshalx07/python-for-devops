import json
import requests


API_URL = "https://jsonplaceholder.typicode.com/posts"
OUTPUT_FILE = "output.json"
POST_LIMIT = 10


def fetch_posts(url):
    """
    Fetch posts from the given URL.
    Raises RuntimeError on network failure or a non-200 HTTP response.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()         # raises HTTPError for 4xx / 5xx
        return response.json()
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No internet connection or the server is unreachable.")
    except requests.exceptions.Timeout:
        raise RuntimeError("The request timed out after 10 seconds.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"API returned an error: {e}") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Unexpected request error: {e}") from e


def extract_data(posts, limit=POST_LIMIT):
    """Return the first `limit` posts, keeping only the fields we care about."""
    return [
        {
            "id":     post["id"],
            "userId": post["userId"],
            "title":  post["title"],
            "body":   post["body"],
        }
        for post in posts[:limit]
    ]


def print_data(posts):
    """Pretty-print a list of post dicts to the terminal."""
    print("\n  Fetched Posts from JSONPlaceholder API")
    print("  " + "=" * 48)
    for post in posts:
        print(f"  Post ID   : {post['id']}")
        print(f"  User ID   : {post['userId']}")
        print(f"  Title     : {post['title']}")
        print(f"  Body      : {post['body'][:60]}...")
        print("  " + "-" * 48)


def save_to_json(data, filename=OUTPUT_FILE):
    """
    Write `data` to a JSON file.
    Handles permission errors and OS-level failures gracefully.
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"\n  ✓  Data saved to '{filename}'")
    except PermissionError:
        print(f"\n  ✗  Permission denied — could not write to '{filename}'.")
    except OSError as e:
        print(f"\n  ✗  File error: {e}")


def main():
    print("=" * 50)
    print("        API Data Fetcher — Day 03")
    print("=" * 50)
    print(f"\n  Fetching data from:\n  {API_URL}\n")

    try:
        raw_data = fetch_posts(API_URL)
    except RuntimeError as e:
        print(f"  ✗  ERROR: {e}")
        print("  Could not fetch data. Exiting.")
        return  # clean exit — no crash, no traceback

    processed_data = extract_data(raw_data)
    print_data(processed_data)
    save_to_json(processed_data)

    print("\n" + "=" * 50)
    print("  Done.")
    print("=" * 50)


if __name__ == "__main__":
    main()