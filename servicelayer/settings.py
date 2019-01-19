from servicelayer import env

# Redis cache
REDIS_DEFAULT_URL = 'redis://redis:6379/0'
REDIS_URL = env.get('ALEPH_REDIS_URL')
REDIS_URL = env.get('REDIS_URL', REDIS_URL)

# General gRPC settings
GRPC_LB_POLICY = env.get('ALEPH_GRPC_LB_POLICY', 'round_robin')
GRPC_LB_POLICY = env.get('GRPC_LB_POLICY', GRPC_LB_POLICY)
GRPC_CONN_AGE = env.to_int('ALEPH_GRPC_CONN_AGE', 500)  # ms
GRPC_CONN_AGE = env.to_int('GRPC_CONN_AGE', GRPC_CONN_AGE)

# Microservice for OCR
OCR_SERVICE = env.get('ALEPH_OCR_SERVICE')  # legacy env name
OCR_SERVICE = env.get('OCR_SERVICE', OCR_SERVICE)

# Entity extraction service
NER_SERVICE = env.get('ALEPH_NER_SERVICE')  # legacy env name
NER_SERVICE = env.get('NER_SERVICE', NER_SERVICE)

# Aleph client API settings
ALEPH_HOST = env.get('ALEPH_HOST')
ALEPH_API_KEY = env.get('ALEPH_API_KEY')

# Amazon client credentials
AWS_KEY_ID = env.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = env.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = env.get('AWS_REGION', 'eu-west-1')

# Storage type (either 's3', 'gs', or 'file', i.e. local file system):
ARCHIVE_TYPE = env('ARCHIVE_TYPE', 'file')
ARCHIVE_BUCKET = env('ARCHIVE_BUCKET')
ARCHIVE_PATH = env('ARCHIVE_PATH')
