import requests

USERS_SELECTION = ["id", "firstName", "lastName", "email", "birthDate", "address"]
POSTS_SELECTION = ["id", "title", "reactions", "views"]
COMMENTS_SELECTION = ["id", "body", "postId", "likes", "user"]

OUTER_FIELDS = {
    "users": "address",
    "comments": "user",
    "posts": "reactions"
    }

INNER_FIELDS = {
    "users": ["city", "state", "stateCode"],
    "comments": ["id"],
    "posts": ["likes", "dislikes"]
    }


class ApiData:
    def __init__(self):
        # ---- FETCH THE DATA FROM A MOCK API ---- #
        self.USERS_JSON = self.fetch_data(source="users", fields=USERS_SELECTION, limit=150)
        self.POSTS_JSON = self.fetch_data(source="posts", fields=POSTS_SELECTION, limit=247)
        self.COMMENTS_JSON = self.fetch_data(source="comments", fields=COMMENTS_SELECTION, limit=300)

    def fetch_data(self, source, fields, limit):
        response = requests.get(f"https://dummyjson.com/{source}?limit={limit}")
        json_data = response.json()
        json_data_refined = self.refine_data(json_data, fields, source)
        json_data_refined = self.extract_fields(data=json_data_refined,
                                                outer=OUTER_FIELDS[source],
                                                inner=INNER_FIELDS[source])
        return json_data_refined

    def refine_data(self, data, fields, source):
        refined_json = []

        # Filter specific values from the API JSON response
        for i in data[source]:
            filtered_dict = {key: value for key, value in i.items() if key in fields}
            refined_json.append(filtered_dict)

        return refined_json

    def extract_fields(self, data, outer, inner):
        inner_dictionaries = []
        inner_values = []
        updated_data = []

        # Get selected inner dictionaries from each record and erase them
        for i in data:
            inner_dict = {key: value for key, value in i.items() if key in outer}
            inner_dictionaries.append(inner_dict)
        for i in data:
            del i[outer]

        # Get key-values from the inner dictionaries
        for i in inner_dictionaries:
            for key in i:
                a = i[key]
                inner_val = {key: value for key, value in a.items() if key in inner}
                inner_values.append(inner_val)

        # Merge current data with extracted key-values
        for idx, ele in enumerate(data):
            merged_dict = ele | inner_values[idx]
            updated_data.append(merged_dict)

        return updated_data