from itsdangerous import URLSafeTimedSerializer
from timsystem import app


def gen_confirm_token(farm_name, email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    # Remember salt
    farm_email = farm_name+' '+email
    rst = serializer.dumps(farm_email)
    return rst


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    try:
        farm_email = serializer.loads(
            token, max_age=expiration
        )
    except Exception:
        return False
    farm_email_split = farm_email.split(' ')
    farm_name = farm_email_split[0]
    email = farm_email_split[1]
    return farm_name, email
