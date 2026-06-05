from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import User, Vehicle, Measurement
from app.schemas import (
    MeasurementCreate, MeasurementResponse, SOHRecordResponse
)
from app.services.soh import SOHCalculationService

router = APIRouter()

# Placeholder dependencies - update with your actual auth
async def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get current authenticated user."""
    return None

async def get_customer_id(current_user: User = Depends(get_current_user)) -> int:
    """Get customer ID from current user."""
    return current_user.customer_id if current_user else None

@router.post("/measurements", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: MeasurementCreate,
    current_user: User = Depends(get_current_user),
    customer_id: int = Depends(get_customer_id),
    db: Session = Depends(get_db),
):
    """Create measurement record.
    
    Records battery metrics from OBD-II, CAN Bus, CSV, or REST API.
    """
    # Verify vehicle belongs to customer
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == measurement.vehicle_id,
        Vehicle.customer_id == customer_id,
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    # Create measurement
    db_measurement = Measurement(
        **measurement.dict(),
        measured_at=datetime.utcnow(),
    )
    
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    
    # Calculate SOH from recent measurements
    recent_measurements = db.query(Measurement).filter(
        Measurement.vehicle_id == measurement.vehicle_id
    ).order_by(Measurement.measured_at.desc()).limit(100).all()
    
    # Create SOH record
    soh_record = SOHCalculationService.create_soh_record(
        db, vehicle.id, list(reversed(recent_measurements))
    )
    
    # Check for alerts
    if soh_record:
        SOHCalculationService.check_and_create_alerts(
            db, vehicle.id, db_measurement, soh_record
        )
    
    return MeasurementResponse.from_orm(db_measurement)

@router.get("/measurements/{vehicle_id}", response_model=List[MeasurementResponse])
async def list_measurements(
    vehicle_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    customer_id: int = Depends(get_customer_id),
    db: Session = Depends(get_db),
):
    """List measurements for a vehicle."""
    # Verify vehicle
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.customer_id == customer_id,
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    measurements = db.query(Measurement).filter(
        Measurement.vehicle_id == vehicle_id
    ).order_by(Measurement.measured_at.desc()).offset(skip).limit(limit).all()
    
    return [MeasurementResponse.from_orm(m) for m in measurements]

@router.get("/soh/{vehicle_id}", response_model=SOHRecordResponse)
async def get_latest_soh(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    customer_id: int = Depends(get_customer_id),
    db: Session = Depends(get_db),
):
    """Get latest SOH record for vehicle."""
    # Verify vehicle
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.customer_id == customer_id,
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    from app.models import SOHRecord
    soh_record = db.query(SOHRecord).filter(
        SOHRecord.vehicle_id == vehicle_id
    ).order_by(SOHRecord.calculated_at.desc()).first()
    
    if not soh_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No SOH records found",
        )
    
    return SOHRecordResponse.from_orm(soh_record)
