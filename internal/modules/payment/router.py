import uuid

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from internal.api.auth import check_api_key
from internal.modules.db.db import get_session
from internal.modules.payment.schemas import CreatePayment, PaymentCreateSuccess, PaymentInfo
from internal.modules.payment.use_case.create_payment import CreatePaymentUseCase
from internal.modules.payment.use_case.get_payment import GetPaymentUseCase

router = APIRouter(prefix="/api/v1/payments", tags=["payments"], dependencies=[Depends(check_api_key)])


def get_create_payment_use_case(session: AsyncSession = Depends(get_session)) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(session)


def get_get_payment_use_case(session: AsyncSession = Depends(get_session)) -> GetPaymentUseCase:
    return GetPaymentUseCase(session)


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=PaymentCreateSuccess)
async def create_payment(
        data: CreatePayment,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=255),
        use_case: CreatePaymentUseCase = Depends(get_create_payment_use_case),
):
    return await use_case.execute(data, idempotency_key)


@router.get("/{payment_id}", response_model=PaymentInfo)
async def get_payment(
        payment_id: uuid.UUID,
        use_case: GetPaymentUseCase = Depends(get_get_payment_use_case),
):
    return await use_case.execute(payment_id)
