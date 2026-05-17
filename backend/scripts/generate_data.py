import pandas as pd
import numpy as np
import random
import uuid
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# =========================
# CONFIG
# =========================
NUM_EVENTS = 15000
NUM_ENDPOINTS = 600
NUM_CUSTOMERS = 250
NUM_REPLAYS = 3500
OUTPUT_DIR = './'

# =========================
# ENUMS
# =========================
EVENT_TYPES = [
    'invoice.created',
    'invoice.validated',
    'invoice.rejected',
    'invoice.paid',
    'compliance.submitted',
    'compliance.failed'
]

EVENT_WEIGHTS = [0.25, 0.20, 0.10, 0.20, 0.15, 0.10]

PRIORITIES = ['low', 'medium', 'high', 'critical']

RESPONSE_CATEGORIES = [
    'success',
    'invalid_signature',
    'endpoint_not_found',
    'rate_limited',
    'server_error',
    'timeout',
    'payload_too_large',
    'malformed_response'
]

DELIVERY_STATES = [
    'delivered',
    'retrying',
    'failed',
    'expired',
    'duplicate',
    'recovered',
    'unsafe_to_replay'
]

FAILURE_REASONS = [
    'none',
    'customer_endpoint_down',
    'invalid_signature',
    'endpoint_deleted',
    'rate_limited',
    'payload_too_large',
    'timeout',
    'duplicate_event',
    'replay_without_fix',
    'malformed_response'
]

HTTP_STATUS_MAP = {
    'success': [200, 201],
    'invalid_signature': [401, 403],
    'endpoint_not_found': [404],
    'rate_limited': [429],
    'server_error': [500, 502, 503],
    'timeout': [504],
    'payload_too_large': [413],
    'malformed_response': [520]
}

ENDPOINT_TYPES = [
    'production',
    'staging',
    'sandbox',
    'internal'
]

# =========================
# HELPERS
# =========================
def random_datetime(start_days_ago=120):
    now = datetime.now()
    start = now - timedelta(days=start_days_ago)
    return start + timedelta(
        seconds=random.randint(0, int((now - start).total_seconds()))
    )


def generate_uuid():
    return str(uuid.uuid4())


# =========================
# GENERATE ENDPOINTS
# =========================
endpoints = []
endpoint_map = {}

for i in range(NUM_ENDPOINTS):
    endpoint_id = f'ep_{i+1:05d}'
    customer_id = f'cust_{random.randint(1, NUM_CUSTOMERS):04d}'

    success_rate = round(np.clip(np.random.normal(0.88, 0.12), 0.15, 0.999), 3)

    active = random.random() > 0.08

    config_change_at = random_datetime()

    endpoint = {
        'endpoint_id': endpoint_id,
        'customer_id': customer_id,
        'endpoint_url_type': random.choice(ENDPOINT_TYPES),
        'expected_signature_version': random.choice(['v1', 'v2', 'v3']),
        'avg_success_rate': success_rate,
        'rate_limit_per_minute': random.choice([30, 60, 100, 200, 500]),
        'active': active,
        'last_config_change_at': config_change_at
    }

    endpoints.append(endpoint)
    endpoint_map[endpoint_id] = endpoint

endpoints_df = pd.DataFrame(endpoints)

# =========================
# GENERATE EVENTS
# =========================
webhook_events = []

for i in range(NUM_EVENTS):
    event_id = f'evt_{i+1:06d}'

    event_type = random.choices(EVENT_TYPES, weights=EVENT_WEIGHTS)[0]

    customer_id = f'cust_{random.randint(1, NUM_CUSTOMERS):04d}'

    payload_size = max(5, int(np.random.gamma(2.5, 120)))

    event = {
        'event_id': event_id,
        'event_type': event_type,
        'customer_id': customer_id,
        'invoice_id': f'inv_{random.randint(100000,999999)}',
        'created_at': random_datetime(),
        'payload_size_kb': payload_size,
        'idempotency_key': generate_uuid(),
        'priority': random.choices(
            PRIORITIES,
            weights=[0.40, 0.35, 0.20, 0.05]
        )[0]
    }

    webhook_events.append(event)

# Inject duplicate events
for _ in range(int(NUM_EVENTS * 0.06)):
    original = random.choice(webhook_events)

    duplicate = original.copy()
    duplicate['event_id'] = f'evt_dup_{generate_uuid()[:8]}'
    duplicate['created_at'] = original['created_at'] + timedelta(minutes=random.randint(1, 120))

    webhook_events.append(duplicate)

webhook_events_df = pd.DataFrame(webhook_events)

# =========================
# DELIVERY SIMULATION
# =========================
delivery_attempts = []
labels = []
replay_actions = []

attempt_counter = 1

for _, event in webhook_events_df.iterrows():

    customer_endpoints = endpoints_df[
        endpoints_df['customer_id'] == event['customer_id']
    ]

    if customer_endpoints.empty:
        customer_endpoints = endpoints_df.sample(1)

    endpoint = customer_endpoints.sample(1).iloc[0]

    endpoint_id = endpoint['endpoint_id']

    scenario = random.choices(
        [
            'success_immediate',
            'transient_timeout',
            'endpoint_recovery',
            'invalid_signature_fixed',
            'rate_limited_then_success',
            'payload_too_large',
            'endpoint_deleted',
            'duplicate_processed',
            'malformed_response_then_success',
            'permanent_failure'
        ],
        weights=[
            0.38,
            0.12,
            0.08,
            0.08,
            0.10,
            0.06,
            0.04,
            0.06,
            0.04,
            0.04
        ]
    )[0]

    created_at = pd.to_datetime(event['created_at'])

    successful = False
    duplicate_detected = False
    safe_to_replay = True
    failure_reason = 'none'
    delivery_state = 'delivered'
    recommended_action = 'none'

    max_attempts = random.randint(2, 6)

    if scenario == 'success_immediate':
        categories = ['success']

    elif scenario == 'transient_timeout':
        categories = ['timeout', 'server_error', 'success']
        delivery_state = 'recovered'
        safe_to_replay = False
        recommended_action = 'monitor_endpoint'

    elif scenario == 'endpoint_recovery':
        categories = ['server_error', 'server_error', 'success']
        delivery_state = 'recovered'
        failure_reason = 'customer_endpoint_down'
        safe_to_replay = False
        recommended_action = 'retry_later'

    elif scenario == 'invalid_signature_fixed':
        categories = ['invalid_signature', 'invalid_signature', 'success']
        delivery_state = 'recovered'
        failure_reason = 'invalid_signature'
        recommended_action = 'rotate_signature'
        safe_to_replay = False

    elif scenario == 'rate_limited_then_success':
        categories = ['rate_limited', 'rate_limited', 'success']
        delivery_state = 'recovered'
        failure_reason = 'rate_limited'
        recommended_action = 'exponential_backoff'
        safe_to_replay = False

    elif scenario == 'payload_too_large':
        categories = ['payload_too_large'] * max_attempts
        delivery_state = 'failed'
        failure_reason = 'payload_too_large'
        recommended_action = 'reduce_payload'
        safe_to_replay = True

    elif scenario == 'endpoint_deleted':
        categories = ['endpoint_not_found'] * max_attempts
        delivery_state = 'expired'
        failure_reason = 'endpoint_deleted'
        recommended_action = 'contact_customer'
        safe_to_replay = False

    elif scenario == 'duplicate_processed':
        categories = ['success']
        delivery_state = 'duplicate'
        failure_reason = 'duplicate_event'
        safe_to_replay = False
        duplicate_detected = True
        recommended_action = 'avoid_replay'

    elif scenario == 'malformed_response_then_success':
        categories = ['malformed_response', 'success']
        delivery_state = 'recovered'
        failure_reason = 'malformed_response'
        safe_to_replay = False
        recommended_action = 'inspect_endpoint'

    else:
        categories = ['server_error'] * max_attempts
        delivery_state = 'failed'
        failure_reason = 'customer_endpoint_down'
        recommended_action = 'investigate_endpoint'
        safe_to_replay = True

    for attempt_num, category in enumerate(categories, start=1):

        attempt_time = created_at + timedelta(
            minutes=attempt_num * random.randint(1, 20)
        )

        http_status = random.choice(HTTP_STATUS_MAP[category])

        response_time = int(np.clip(np.random.normal(600, 300), 50, 12000))

        timeout = category == 'timeout'

        signature_valid = category != 'invalid_signature'

        retry_scheduled = category != 'success' and attempt_num != len(categories)

        if category == 'success':
            successful = True

        delivery_attempts.append({
            'attempt_id': f'att_{attempt_counter:08d}',
            'event_id': event['event_id'],
            'endpoint_id': endpoint_id,
            'attempt_number': attempt_num,
            'attempted_at': attempt_time,
            'http_status': http_status,
            'response_time_ms': response_time,
            'response_body_category': category,
            'timeout': timeout,
            'signature_valid': signature_valid,
            'retry_scheduled': retry_scheduled
        })

        attempt_counter += 1

    # Replay simulation
    if random.random() < 0.22:

        replay_time = attempt_time + timedelta(
            hours=random.randint(1, 48)
        )

        if safe_to_replay:
            replay_result = random.choice([
                'success',
                'failed',
                'recovered'
            ])
        else:
            replay_result = random.choice([
                'duplicate_processed',
                'unsafe'
            ])

        replay_actions.append({
            'event_id': event['event_id'],
            'replayed_at': replay_time,
            'replay_result': replay_result,
            'duplicate_detected': duplicate_detected,
            'manually_triggered': random.random() < 0.45
        })

    labels.append({
        'event_id': event['event_id'],
        'delivery_state': delivery_state,
        'failure_reason': failure_reason,
        'safe_to_replay': safe_to_replay,
        'recommended_action': recommended_action
    })

# =========================
# DATAFRAMES
# =========================
delivery_attempts_df = pd.DataFrame(delivery_attempts)
labels_df = pd.DataFrame(labels)
replay_actions_df = pd.DataFrame(replay_actions)

# =========================
# TRAIN / TEST SPLIT
# =========================
webhook_events_df = webhook_events_df.sample(frac=1, random_state=42).reset_index(drop=True)

split_idx = int(len(webhook_events_df) * 0.8)

train_events = webhook_events_df.iloc[:split_idx]
test_events = webhook_events_df.iloc[split_idx:]

labels_train_df = labels_df[
    labels_df['event_id'].isin(train_events['event_id'])
]

events_test_df = test_events.copy()

# =========================
# EXPORT CSVs
# =========================
train_events.to_csv(f'{OUTPUT_DIR}/webhook_events.csv', index=False)
delivery_attempts_df.to_csv(f'{OUTPUT_DIR}/delivery_attempts.csv', index=False)
endpoints_df.to_csv(f'{OUTPUT_DIR}/endpoints.csv', index=False)
replay_actions_df.to_csv(f'{OUTPUT_DIR}/replay_actions.csv', index=False)
labels_train_df.to_csv(f'{OUTPUT_DIR}/labels_train.csv', index=False)
events_test_df.to_csv(f'{OUTPUT_DIR}/events_test.csv', index=False)

# =========================
# SUMMARY
# =========================
print('\nDataset generation completed.\n')

print(f'Webhook Events: {len(train_events)}')
print(f'Delivery Attempts: {len(delivery_attempts_df)}')
print(f'Endpoints: {len(endpoints_df)}')
print(f'Replay Actions: {len(replay_actions_df)}')
print(f'Train Labels: {len(labels_train_df)}')
print(f'Test Events: {len(events_test_df)}')

print('\nGenerated files:')
print('- webhook_events.csv')
print('- delivery_attempts.csv')
print('- endpoints.csv')
print('- replay_actions.csv')
print('- labels_train.csv')
print('- events_test.csv')
