"""
Reports API endpoints.
Provides PDF report generation and download.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.services.report_service import get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/types")
async def get_report_types():
    """
    Get available report types.
    
    Returns a list of report types with descriptions.
    """
    service = get_report_service()
    return {
        "report_types": service.get_available_reports()
    }


@router.get("/generate/{report_type}")
async def generate_report(
    report_type: str,
    hospital_id: str = Query(default="hosp-001", description="Hospital ID"),
):
    """
    Generate a PDF report.
    
    Returns the generated PDF as a downloadable file.
    """
    service = get_report_service()
    
    # Validate report type
    available_types = [r["id"] for r in service.get_available_reports()]
    if report_type not in available_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Available types: {available_types}"
        )
    
    try:
        pdf_bytes = service.generate_report(hospital_id, report_type)
        
        # Create filename
        filename = f"ha-cie-{report_type.replace('_', '-')}-{hospital_id}.pdf"
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/preview/{report_type}")
async def preview_report(
    report_type: str,
    hospital_id: str = Query(default="hosp-001", description="Hospital ID"),
):
    """
    Get report preview (inline PDF).
    
    Returns the PDF for inline viewing in browser.
    """
    service = get_report_service()
    
    # Validate report type
    available_types = [r["id"] for r in service.get_available_reports()]
    if report_type not in available_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Available types: {available_types}"
        )
    
    try:
        pdf_bytes = service.generate_report(hospital_id, report_type)
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )

