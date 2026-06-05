"""Database models for EV SOH Platform."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# ==================== Enums ====================

class UserRole(str, enum.Enum):
    """User roles in the system."""
    PLATFORM_ADMIN = "platform_admin"
    DEALER = "dealer"
    FLEET_MANAGER = "fleet_manager"
    READ_ONLY = "read_only"

class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    """Alert status."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class ReportStatus(str, enum.Enum):
    """Report status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class HealthStatus(str, enum.Enum):
    """Battery health status."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"

# ==================== Customer & Users ====================

class Customer(Base):
    """Multi-tenant customer/organization."""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="customer", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="customer", cascade="all, delete-orphan")

class User(Base):
    """User account with role-based access."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.READ_ONLY, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="users")

# ==================== Vehicles & Batteries ====================

class Vehicle(Base):
    """Electric vehicle information."""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    vin = Column(String(17), unique=True, nullable=False, index=True)
    brand = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Float, default=0)
    color = Column(String(50))
    registration_number = Column(String(50), unique=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    battery_pack = relationship("BatteryPack", uselist=False, back_populates="vehicle", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="vehicle", cascade="all, delete-orphan")
    soh_records = relationship("SOHRecord", back_populates="vehicle", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="vehicle", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="vehicle", cascade="all, delete-orphan")

class BatteryPack(Base):
    """Battery pack specifications."""
    __tablename__ = "battery_packs"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    chemistry = Column(String(50), nullable=False)  # LFP, NCA, NCM, etc.
    nominal_capacity = Column(Float, nullable=False)  # kWh
    nominal_voltage = Column(Float, nullable=False)  # Volts
    num_cells = Column(Integer)
    num_modules = Column(Integer)
    manufacturer = Column(String(100))
    manufacturing_date = Column(DateTime)
    installation_date = Column(DateTime)
    warranty_end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="battery_pack")
    cell_measurements = relationship("CellMeasurement", back_populates="battery_pack", cascade="all, delete-orphan")

# ==================== Measurements ====================

class Measurement(Base):
    """Raw measurement data from OBD-II, CAN Bus, or API."""
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(50), nullable=False)  # obd2, canbus, csv, api
    
    # Battery metrics
    soc = Column(Float)  # State of Charge %
    voltage = Column(Float)  # Volts
    current = Column(Float)  # Amps
    temperature = Column(Float)  # Celsius
    available_capacity = Column(Float)  # kWh
    
    # Additional metrics
    internal_resistance = Column(Float)  # mOhms
    cycle_count = Column(Integer)
    power = Column(Float)  # Watts
    
    # Metadata
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    
    measured_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="measurements")

class CellMeasurement(Base):
    """Individual cell measurement data."""
    __tablename__ = "cell_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    battery_pack_id = Column(Integer, ForeignKey("battery_packs.id", ondelete="CASCADE"), nullable=False, index=True)
    cell_index = Column(Integer, nullable=False)  # Cell position
    voltage = Column(Float, nullable=False)  # Cell voltage
    temperature = Column(Float)
    measured_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    battery_pack = relationship("BatteryPack", back_populates="cell_measurements")

class SOHRecord(Base):
    """Calculated State of Health records."""
    __tablename__ = "soh_records"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    soh_percentage = Column(Float, nullable=False)  # 0-100%
    soc_percentage = Column(Float)  # State of Charge
    cycle_count = Column(Integer)
    available_capacity = Column(Float)  # kWh
    total_capacity = Column(Float)  # kWh (degradation)
    internal_resistance = Column(Float)  # mOhms
    health_status = Column(SQLEnum(HealthStatus), default=HealthStatus.PASS)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="soh_records")

# ==================== Alerts & Reports ====================

class Alert(Base):
    """System alerts for battery conditions."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(100), nullable=False)  # low_soh, overtemp, etc.
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING, index=True)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    metadata = Column(JSON)  # Additional alert data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="alerts")

class Report(Base):
    """Generated battery health reports."""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(50), default="pdf")  # pdf, csv, json
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, index=True)
    file_path = Column(String(500))  # S3 path or local path
    file_url = Column(String(500))  # Public URL
    soh_snapshot = Column(JSON)  # SOH data snapshot
    metadata = Column(JSON)  # Additional metadata
    qr_code = Column(String(500))  # QR code for verification
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    generated_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="reports")

# ==================== Audit Logs ====================

class AuditLog(Base):
    """System audit trail for compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False, index=True)  # create, read, update, delete
    resource_type = Column(String(50), nullable=False, index=True)  # Vehicle, Battery, etc.
    resource_id = Column(Integer)
    changes = Column(JSON)  # Before/after changes
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="audit_logs")
