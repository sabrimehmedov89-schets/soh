from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import (
    Vehicle, BatteryPack, Measurement, SOHRecord, Alert,
    AlertSeverity, AlertStatus, HealthStatus
)
from app.schemas import MeasurementCreate
import statistics

class SOHCalculationService:
    """Service for SOH calculations and battery diagnostics."""
    
    @staticmethod
    def calculate_soh(
        db: Session,
        vehicle_id: int,
        measurements: List[Measurement]
    ) -> Optional[float]:
        """Calculate State of Health based on measurements.
        
        Uses capacity fade and resistance growth degradation model.
        SOH = (Available Capacity / Nominal Capacity) * 100
        """
        if not measurements:
            return None
        
        # Get battery pack info
        battery = db.query(BatteryPack).filter(
            BatteryPack.vehicle_id == vehicle_id
        ).first()
        
        if not battery:
            return None
        
        # Calculate average available capacity from recent measurements
        recent_measurements = measurements[-10:] if len(measurements) > 10 else measurements
        available_capacities = [
            m.available_capacity for m in recent_measurements
            if m.available_capacity
        ]
        
        if not available_capacities:
            return None
        
        avg_available = statistics.mean(available_capacities)
        soh = (avg_available / battery.nominal_capacity) * 100
        
        return min(100, max(0, soh))  # Clamp between 0-100
    
    @staticmethod
    def determine_health_status(soh_percentage: float) -> HealthStatus:
        """Determine health status based on SOH percentage."""
        if soh_percentage >= 80:
            return HealthStatus.PASS
        elif soh_percentage >= 60:
            return HealthStatus.WARNING
        else:
            return HealthStatus.FAIL
    
    @staticmethod
    def create_soh_record(
        db: Session,
        vehicle_id: int,
        measurements: List[Measurement]
    ) -> Optional[SOHRecord]:
        """Create SOH record from measurements."""
        if not measurements:
            return None
        
        # Calculate SOH
        soh = SOHCalculationService.calculate_soh(db, vehicle_id, measurements)
        if soh is None:
            return None
        
        # Get latest measurement for metrics
        latest = measurements[-1]
        
        # Get battery info
        battery = db.query(BatteryPack).filter(
            BatteryPack.vehicle_id == vehicle_id
        ).first()
        
        # Create record
        soh_record = SOHRecord(
            vehicle_id=vehicle_id,
            soh_percentage=soh,
            soc_percentage=latest.soc,
            cycle_count=latest.cycle_count,
            available_capacity=latest.available_capacity,
            total_capacity=battery.nominal_capacity if battery else None,
            internal_resistance=latest.internal_resistance,
            health_status=SOHCalculationService.determine_health_status(soh),
            calculated_at=datetime.utcnow(),
        )
        
        db.add(soh_record)
        db.commit()
        db.refresh(soh_record)
        
        return soh_record
    
    @staticmethod
    def check_and_create_alerts(
        db: Session,
        vehicle_id: int,
        measurement: Measurement,
        soh_record: SOHRecord
    ) -> List[Alert]:
        """Check measurement thresholds and create alerts."""
        alerts_created = []
        
        # Low SOH alert
        if soh_record.soh_percentage < 60:
            alert = Alert(
                vehicle_id=vehicle_id,
                alert_type="low_soh",
                severity=AlertSeverity.CRITICAL if soh_record.soh_percentage < 40 else AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                title="Low Battery State of Health",
                message=f"Battery SOH has degraded to {soh_record.soh_percentage:.1f}%",
                metadata={"soh": soh_record.soh_percentage}
            )
            db.add(alert)
            alerts_created.append(alert)
        
        # Overtemperature alert
        if measurement.temperature and measurement.temperature > 50:
            alert = Alert(
                vehicle_id=vehicle_id,
                alert_type="overtemperature",
                severity=AlertSeverity.CRITICAL if measurement.temperature > 60 else AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                title="Battery Overtemperature",
                message=f"Battery temperature: {measurement.temperature:.1f}°C",
                metadata={"temperature": measurement.temperature}
            )
            db.add(alert)
            alerts_created.append(alert)
        
        # Undervoltage alert
        if measurement.voltage and measurement.voltage < 200:
            alert = Alert(
                vehicle_id=vehicle_id,
                alert_type="undervoltage",
                severity=AlertSeverity.CRITICAL,
                status=AlertStatus.OPEN,
                title="Battery Undervoltage",
                message=f"Battery voltage: {measurement.voltage:.1f}V",
                metadata={"voltage": measurement.voltage}
            )
            db.add(alert)
            alerts_created.append(alert)
        
        # Overvoltage alert
        if measurement.voltage and measurement.voltage > 420:
            alert = Alert(
                vehicle_id=vehicle_id,
                alert_type="overvoltage",
                severity=AlertSeverity.WARNING,
                status=AlertStatus.OPEN,
                title="Battery Overvoltage",
                message=f"Battery voltage: {measurement.voltage:.1f}V",
                metadata={"voltage": measurement.voltage}
            )
            db.add(alert)
            alerts_created.append(alert)
        
        if alerts_created:
            db.commit()
        
        return alerts_created
    
    @staticmethod
    def get_historical_soh(
        db: Session,
        vehicle_id: int,
        days: int = 30
    ) -> List[SOHRecord]:
        """Get historical SOH records."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        records = db.query(SOHRecord).filter(
            SOHRecord.vehicle_id == vehicle_id,
            SOHRecord.calculated_at >= cutoff_date
        ).order_by(SOHRecord.calculated_at).all()
        
        return records
