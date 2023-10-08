import os
from modules.config import oauth
os.system(r'curl -d "{\"yandexPassportOauthToken\":\"' + oauth + r'\"}" "https://iam.api.cloud.yandex.net/iam/v1/tokens"')