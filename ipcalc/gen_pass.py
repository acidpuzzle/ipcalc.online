import logging
import string
import secrets


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def generate_passwords(**kwargs):
    """

    :param kwargs:
    :return: List of password
    """
    passwords = []
    keys = kwargs.keys()

    logger.debug(f"keys = {keys}")

    alphabet = ''
    if 'nums' in keys:
        alphabet += string.digits
    if 'lchar' in keys:
        alphabet += string.ascii_lowercase
    if 'uchar' in keys:
        alphabet += string.ascii_uppercase
    if 'special' in keys:
        alphabet += string.punctuation
    if 'exclude' in keys:
        alphabet = ''.join(set(alphabet) - set(kwargs.get('exclude', '')))
    try:
        pass_len = int(kwargs.get('length')) if kwargs.get('length') else 16
        pass_quant = int(kwargs.get('quantity')) if kwargs.get('quantity') else 8
        if pass_len < 4:
            return {"pass_error": "Password length cannot be less than 4 character"}
        if pass_len > 128:
            return {"pass_error": "Password length cannot be more than 128 characters"}
        if pass_quant < 1:
            return {"pass_error": "The number of passwords cannot be less than one"}
        if pass_quant > 512:
            return {"pass_error": "The number of passwords cannot be more than 512"}
        for i in range(pass_quant):
            while True:
                password = ''.join(secrets.choice(alphabet) for i in range(pass_len))
                if ('lstart' in keys) and ('lchar' in keys or 'uchar' in keys) and not password[0].isalpha():
                    continue
                elif 'nums' in keys and not any(c.isdigit() for c in password):
                    continue
                elif 'lchar' in keys and not any(c.islower() for c in password):
                    continue
                elif 'uchar' in keys and not any(c.isupper() for c in password):
                    continue
                elif 'special' in keys and not any(c in string.punctuation for c in password):
                    continue
                else:
                    break
            passwords.append(password)
        return {"passwords": passwords}
    except IndexError as error:
        return {"pass_error": error}



