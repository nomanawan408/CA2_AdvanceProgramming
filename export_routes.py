"""
Export functionality for registered students data
Supports CSV and PDF formats
"""
from flask import Response, make_response
from models import Event, Registration, User
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import csv
from datetime import datetime


def export_registrations_csv(event_id):
    """Export event registrations as CSV"""
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    # Create CSV in memory
    output = []
    output.append(['Student Name', 'Email', 'Phone Number', 'Payment Method', 'Invoice Path', 'Registration Date'])
    
    for reg in registrations:
        student = User.query.get(reg.student_id)
        output.append([
            student.name,
            student.email,
            reg.phone_number or 'N/A',
            reg.payment_method or 'N/A',
            reg.invoice_path or 'N/A',
            reg.registration_date.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Convert to CSV string
    csv_output = []
    for row in output:
        csv_output.append(','.join([f'"{cell}"' for cell in row]))
    
    csv_string = '\n'.join(csv_output)
    
    # Create response
    response = Response(csv_string, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=event_{event_id}_registrations.csv'
    
    return response


def export_registrations_pdf(event_id):
    """Export event registrations as PDF"""
    event = Event.query.get_or_404(event_id)
    registrations = Registration.query.filter_by(event_id=event_id).all()
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Title
    title = Paragraph(f"Event Registrations Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Event details
    event_info = f"""
    <b>Event:</b> {event.title}<br/>
    <b>Date:</b> {event.event_date.strftime('%Y-%m-%d %H:%M')}<br/>
    <b>Location:</b> {event.location}<br/>
    <b>Capacity:</b> {event.capacity}<br/>
    <b>Registered:</b> {len(registrations)}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
    """
    elements.append(Paragraph(event_info, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Table data
    data = [['#', 'Student Name', 'Email', 'Phone', 'Payment', 'Invoice', 'Registration Date']]
    
    for idx, reg in enumerate(registrations, 1):
        student = User.query.get(reg.student_id)
        data.append([
            str(idx),
            student.name,
            student.email,
            reg.phone_number or 'N/A',
            reg.payment_method or 'N/A',
            reg.invoice_path or 'N/A',
            reg.registration_date.strftime('%Y-%m-%d %H:%M')
        ])
    
    # Create table
    table = Table(data, colWidths=[0.3*inch, 1.5*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=event_{event_id}_registrations.pdf'
    
    return response
