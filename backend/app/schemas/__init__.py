from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ==================== Auth Schemas ====================

class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=2)
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    """User response."""
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Vehicle Schemas ====================

class VehicleCreate(BaseModel):
    """Vehicle creation request."""
    vin: str = Field(..., min_length=17, max_length=17)
    brand: str
    model: str
    year: int = Field(..., ge=2000, le=2100)
    color: Optional[str]
    registration_number: Optional[str]

class VehicleUpdate(BaseModel):
    """Vehicle update request."""
    mileage: Optional[float]
    color: Optional[str]
    is_active: Optional[bool]

class VehicleResponse(BaseModel):
    """Vehicle response."""
    id: int
    vin: str
    brand: str
    model: str
    year: int
    mileage: float
    color: Optional[str]
    registration_number: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Battery Schemas ====================

class BatteryPackCreate(BaseModel):
    """Battery pack creation request."""
    serial_number: str
    chemistry: str  # LFP, NCA, NCM
    nominal_capacity: float = Field(..., gt=0)  # kWh
    nominal_voltage: float = Field(..., gt=0)  # Volts
    num_cells: Optional[int]
    num_modules: Optional[int]
    manufacturer: Optional[str]

class BatteryPackResponse(BaseModel):
    """Battery pack response."""
    id: int
    vehicle_id: int
    serial_number: str
    chemistry: str
    nominal_capacity: float
    nominal_voltage: float
    num_cells: Optional[int]
    num_modules: Optional[int]
    manufacturer: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Measurement Schemas ====================

class MeasurementCreate(BaseModel):
    """Measurement creation request."""
    vehicle_id: int
    source: str  # obd2, canbus, csv, api
    soc: Optional[float] = Field(None, ge=0, le=100)  # %
    voltage: Optional[float] = Field(None, gt=0)  # Volts
    current: Optional[float]  # Amps
    temperature: Optional[float]  # Celsius
    available_capacity: Optional[float] = Field(None, ge=0)  # kWh
    internal_resistance: Optional[float] = Field(None, ge=0)  # mOhms
    cycle_count: Optional[int] = Field(None, ge=0)
    power: Optional[float]  # Watts
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]

class MeasurementResponse(BaseModel):
    """Measurement response."""
    id: int
    vehicle_id: int
    source: str
    soc: Optional[float]
    voltage: Optional[float]
    current: Optional[float]
    temperature: Optional[float]
    available_capacity: Optional[float]
    internal_resistance: Optional[float]
    cycle_count: Optional[int]
    measured_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== SOH Schemas ====================

class SOHRecordResponse(BaseModel):
    """SOH record response."""
    id: int
    vehicle_id: int
    soh_percentage: float
    soc_percentage: Optional[float]
    cycle_count: Optional[int]
    available_capacity: Optional[float]
    total_capacity: Optional[float]
    internal_resistance: Optional[float]
    health_status: str
    calculated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Report Schemas ====================

class ReportGenerateRequest(BaseModel):
    """Report generation request."""
    report_type: str = "pdf"  # pdf, csv, json
    include_historical: bool = True
    days: int = 30

class ReportResponse(BaseModel):
    """Report response."""
    id: int
    vehicle_id: int
    report_type: str
    status: str
    file_url: Optional[str]
    qr_code: Optional[str]
    created_at: datetime
    generated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== Alert Schemas ====================

class AlertResponse(BaseModel):
    """Alert response."""
    id: int
    vehicle_id: int
    alert_type: str
    severity: str
    status: str
    title: str
    message: str
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AlertUpdateRequest(BaseModel):
    """Alert update request."""
    status: str  # open, acknowledged, resolved
