import os

ENV_RUNTIME_ENV = os.getenv('ENV_RUNTIME_ENV', 'dev')


def is_dev_environment():
    return ENV_RUNTIME_ENV.lower() in ["dev", "development"]