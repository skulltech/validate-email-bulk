from email_validator import validate_email, EmailSyntaxError, EmailUndeliverableError
from validate_email import validate_email as validate_email1


def validate(email):
    ret = {
        'email': email,
        'syntax': None,
        'mx': None,
        'deliverable': None,
        'color': None,
        'normalized': None
    }
    try:
        v = validate_email(email)
    except EmailSyntaxError:
        ret['syntax'] = False
        ret['color'] = 'red'
        return ret
    except EmailUndeliverableError:
        ret['syntax'] = True
        ret['mx'] = False
        ret['color'] = 'red'
        return ret
    else:
        ret['syntax'] = True
        ret['mx'] = True
        ret['normalized'] = v['email']

    ret['deliverable'] = True if validate_email1(email, verify=True) else False
    ret['color'] = 'green' if ret['deliverable'] else 'gray'
    return ret


def main():
    import json

    email = input('[*] Email address: ')
    ret = validate(email)
    print(json.dumps(ret, indent=2))


if __name__ == '__main__':
    main()
