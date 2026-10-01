from decimal import Decimal
from unittest.mock import patch

from fastapi.testclient import TestClient # type: ignore

from app.main import app
from app.database import SessionLocal
from app.models.payment import Payment


client = TestClient(app)


def clear_test_payments():
    db = SessionLocal()

    try:
        db.query(Payment).filter(
            Payment.transaction_id.like('TEST-%')
        ).delete(
            synchronize_session=False
        )

        db.commit()

    finally:
        db.close()


def test_payment_success():
    clear_test_payments()

    with patch(
        'app.routers.payments.random.choice',
        return_value='SUCCESS'
    ), patch(
        'app.routers.payments.requests.post'
    ) as mock_post:

        mock_post.return_value.status_code = 200

        response = client.post(
            '/api/payments/',
            json={
                'user_id': 1,
                'card_id': 1,
                'amount': 150.00
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data['status'] == 'SUCCESS'
    assert data['user_id'] == 1
    assert data['card_id'] == 1
    assert Decimal(str(data['amount'])) == Decimal('150.00')
    assert data['transaction_id'].startswith('TXN-')


def test_payment_failure():
    clear_test_payments()

    with patch(
        'app.routers.payments.random.choice',
        return_value='FAILED'
    ), patch(
        'app.routers.payments.requests.post'
    ) as mock_post:

        mock_post.return_value.status_code = 200

        response = client.post(
            '/api/payments/',
            json={
                'user_id': 1,
                'card_id': 1,
                'amount': 500.00
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data['status'] == 'FAILED'
    assert data['user_id'] == 1
    assert data['card_id'] == 1
    assert Decimal(str(data['amount'])) == Decimal('500.00')
    assert data['transaction_id'].startswith('TXN-')


def test_payment_amount_must_be_positive():
    response = client.post(
        '/api/payments/',
        json={
            'user_id': 1,
            'card_id': 1,
            'amount': 0
        }
    )

    assert response.status_code == 422


def test_payment_missing_amount():
    response = client.post(
        '/api/payments/',
        json={
            'user_id': 1,
            'card_id': 1
        }
    )

    assert response.status_code == 422


def test_get_payment_not_found():
    response = client.get(
        '/api/payments/999999'
    )

    assert response.status_code == 404

    assert response.json()['detail'] == 'Payment not found'

