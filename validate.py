from email_validator import validate_email, EmailNotValidError
from validate_email import validate_email as validate_email1


def validate(email):
    try:
        v = validate_email(email)
        email = v['email']
    except EmailNotValidError:
        return False
    return email if validate_email1(email, verify=True) else False


def main():
    email = input('[*] Email address: ')
    ret = validate(email)
    if ret:
        print(f'[*] Valid: {ret}')
    else:
        print('[*] Invalid')


if __name__ == '__main__':
    main()
