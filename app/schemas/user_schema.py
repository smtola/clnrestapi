from marshmallow import Schema, fields

class UserSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    role = fields.Str(required=True)
    is_verified = fields.Bool()