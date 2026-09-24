from pydantic import BaseModel, Field

class TokenUsage(BaseModel):
    input_tokens: int = Field(ge=0, default=0)
    cached_input_tokens: int = Field(ge=0, default=0)
    output_tokens: int = Field(ge=0, default=0)
    reasoning_tokens: int = Field(ge=0, default=0)

class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    tokens: TokenUsage

class TenantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class CheckoutRequest(BaseModel):
    tenant_id: str
