from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, field_validator

from app.main import validation_exception_handler


class _Payload(BaseModel):
    value: int

    @field_validator("value")
    @classmethod
    def reject(cls, v: int) -> int:
        raise ValueError("value is not allowed")


def test_custom_validator_error_is_422_not_500():
    probe = FastAPI()
    probe.add_exception_handler(RequestValidationError, validation_exception_handler)

    @probe.post("/probe")
    def _endpoint(_: _Payload) -> dict:
        return {}

    r = TestClient(probe, raise_server_exceptions=False).post("/probe", json={"value": 1})

    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    assert "value is not allowed" in r.json()["error"]["details"][0]["msg"]
