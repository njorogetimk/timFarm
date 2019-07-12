from itsdangerous import URLSafeTimedSerializer
from timsystem import app


def gen_confirm_token(in1, in2):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    # Remember salt
    valUnion = in1+'/n'+in2
    rst = serializer.dumps(valUnion)
    return rst


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    try:
        result = serializer.loads(
            token, max_age=expiration
        )
    except Exception:
        return False
    result_split = result.split('/n')
    rs1 = result_split[0]
    rs2 = result_split[1]
    return rs1, rs2
