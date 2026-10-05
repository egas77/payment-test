from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from internal.modules.payment.exceptions import PaymentNotFound
from internal.modules.payment.router import router as payment_router

app = FastAPI(title="Payments")

app.include_router(payment_router)


@app.exception_handler(PaymentNotFound)
async def payment_not_found_handler(request: Request, exc: PaymentNotFound) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Payment {exc.payment_id} not found"},
    )
