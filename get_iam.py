import os
from modules.config import oauth
req = r'curl -d "{\"yandexPassportOauthToken\":\"' + oauth + r'\"}" "https://iam.api.cloud.yandex.net/iam/v1/tokens"'
print(req)
os.system(req)