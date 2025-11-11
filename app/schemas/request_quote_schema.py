from marshmallow import Schema, fields

class RequestQuoteSchema(Schema):
      company_name = fields.Str(required=True)
      full_name = fields.Str(required=True)
      email = fields.Email(required=True)
      address = fields.Str(required=True)
      tel = fields.Str(required=True)
      job = fields.Str(required=True)
      origin_destination = fields.Str(required=True)
      product_name = fields.Str(required=True)
      weight_dimensions = fields.Str(required=True)
      container_size = fields.Str(required=True)