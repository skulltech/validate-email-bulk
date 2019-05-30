from validate import validate


def handler(event, context):
    email = event.get('email')
    ret = validate(email)
    if ret:
        response = {
            'email': ret,
            'valid': True
        }
    else:
        response = {
            'email': email,
            'valid': False
        }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': response
    }
