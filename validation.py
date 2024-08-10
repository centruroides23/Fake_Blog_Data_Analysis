from cerberus import Validator


class DataValidation:
    def __init__(self):
        self.current_validation = None
        self.user_schema = {
            'id': {'type': 'integer', 'min': 1},
            'firstName': {'type': 'string', 'minlength': 1},
            'lastName': {'type': 'string', 'minlength': 1},
            'email': {'type': 'string', 'regex': '^[\w\.-]+@[\w\.-]+\.\w+$'},
            'birthDate': {'type': 'string', 'regex': '^\d{4}-\d{1,2}-\d{1,2}$'},
            'city': {'type': 'string', 'minlength': 1},
            'state': {'type': 'string', 'minlength': 1},
            'stateCode': {'type': 'string', 'minlength': 2, 'maxlength': 2}
        }
        self.post_schema = {
            'id': {'type': 'integer', 'min': 1},
            'title': {'type': 'string', 'minlength': 1},
            'views': {'type': 'integer', 'min': 0},
            'likes': {'type': 'integer', 'min': 0},
            'dislikes': {'type': 'integer', 'min': 0},
        }
        self.comment_schema = {
            'id': {'type': 'integer', 'min': 1},
            'body': {'type': 'string', 'minlength': 1},
            'postId': {'type': 'integer', 'min': 1},
            'likes': {'type': 'integer', 'min': 0},
        }

    def perform_validation(self, data, schema):

        # Define the corresponding schema
        if schema == "users":
            self.current_validation = Validator(self.user_schema)
        elif schema == "posts":
            self.current_validation = Validator(self.post_schema)
        else:
            self.current_validation = Validator(self.comment_schema)

        # Perform validation on input data
        try:
            # Validate the data
            if not self.current_validation.validate(data):
                raise ValueError("Validation failed")
        except ValueError as e:
            # Handle validation error
            print(f"Validation error: {e}, Errors: {self.current_validation.errors}")

