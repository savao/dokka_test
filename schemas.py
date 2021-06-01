from json import loads
from marshmallow import Schema, fields


class GetFileSchema(Schema):
    file = fields.Raw(type='file')


class TaskSchema(Schema):
    task_id = fields.String()
    status = fields.Function(lambda obj: 'running' if obj.data is None else 'done')
    data = fields.Function(lambda obj: '' if obj.data is None else loads(obj.data))
