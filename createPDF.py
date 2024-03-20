from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph


def create_dividend_summary_pdf(file_path,data,total_cad,total_usd):

    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading3']
    normal_style = styles['Normal']

    # Add title
    title = Paragraph("Dividend Summary", title_style)
    elements.append(title)
    elements.append(Paragraph("<br/>", normal_style))

    # Add table
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)
    elements.append(Paragraph("<br/>", normal_style))

    # Add total amounts
    total_cad = 322.39
    total_usd = 23.60
    elements.append(Paragraph(f"Total amount Dividends received in CAD: {total_cad:.2f}", normal_style))
    elements.append(Paragraph(f"Total amount Dividends received in USD: {total_usd:.2f}", normal_style))
    # Build PDF
    doc.build(elements)



def create_contributions_summary_pdf(file_path,tfsa_data, rrsp_data,fhsa_data, results):

    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading3']
    normal_style = styles['Normal']

    # Add title
    title = Paragraph("Contributions Summary", title_style)
    elements.append(title)
    elements.append(Paragraph("<br/>", normal_style))

    # Add TFSA contributions
    tfsa_title = Paragraph("Summary contributions this year TFSA", heading_style)
    elements.append(tfsa_title)
    tfsa_table = Table(tfsa_data)
    tfsa_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(tfsa_table)
    elements.append(Paragraph("<br/>", normal_style))

    # Add RRSP contributions
    rrsp_title = Paragraph("Summary contributions this year RRSP", heading_style)
    elements.append(rrsp_title)
    rrsp_table = Table(rrsp_data)
    rrsp_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(rrsp_table)
    elements.append(Paragraph("<br/>", normal_style))

    # Add FHSA contributions
    fhsa_title = Paragraph("Summary contributions this year FHSA", heading_style)
    elements.append(fhsa_title)
    fhsa_table = Table(fhsa_data)
    fhsa_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(fhsa_table)
    elements.append(Paragraph("<br/>", normal_style))

    elements.append(Paragraph(f"Total Amount from Wealth Simple (TFSA): {results['TFSA_contributions']:.2f}", normal_style))
    elements.append(Paragraph(f"Total Amount in TFSA Contributions: {results['TFSA_contributions']:.2f}", normal_style))
    elements.append(Paragraph(f"Total Amount in TFSA Room: {results['TFSA_contribution_room']:.2f}", normal_style))
    elements.append(Paragraph(f"Available TFSA contribution room to invest: {results['TFSA_contribution_room_left']:.2f} Goal: {results['TFSA_goal']:.2f}", normal_style))

    elements.append(Paragraph(f"Total Amount in FHSA Contributions: {results['FHSA_contributions']:.2f}", normal_style))
    elements.append(Paragraph(f"Total Amount in FHSA Room: {results['FHSA_contribution_room']:.2f}", normal_style))
    elements.append(Paragraph(f"Available FHSA contribution room to invest: {results['FHSA_contribution_room_left']:.2f} Goal: {results['FHSA_goal']:.2f}", normal_style))

    elements.append(Paragraph(f"Total Amount in RRSP Contributions: {results['RRSP_contributions']:.2f}", normal_style))
    elements.append(Paragraph(f"Total Amount in RRSP Room: {results['RRSP_contribution_room']:.2f}", normal_style))
    elements.append(Paragraph(f"Available RRSP contribution room to invest: {results['RRSP_contribution_room_left']:.2f} Goal: {results['RRSP_goal']:.2f}", normal_style)) 

            # Build PDF
    doc.build(elements)

def create_account_summary_pdf(file_path,tfsa_data ,rrsp_data,fhsa_data):


    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading3']
    normal_style = styles['Normal']

    # Add title
    title = Paragraph("Account Summary", title_style)
    elements.append(title)
    elements.append(Paragraph("<br/>", normal_style))

    # Add TFSA account summary
    tfsa_title = Paragraph("Account Summary for TFSA", heading_style)
    elements.append(tfsa_title)
    tfsa_table = Table(tfsa_data)
    tfsa_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(tfsa_table)
    elements.append(Paragraph("<br/>", normal_style))

    # Add RRSP account summary
    rrsp_title = Paragraph("Account Summary for RRSP", heading_style)
    elements.append(rrsp_title)
    rrsp_table = Table(rrsp_data)
    rrsp_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(rrsp_table)
    elements.append(Paragraph("<br/>", normal_style))

    # Add FHSA account summary
    fhsa_title = Paragraph("Account Summary for FHSA", heading_style)
    elements.append(fhsa_title)
    fhsa_table = Table(fhsa_data)
    fhsa_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(fhsa_table)
    elements.append(Paragraph("<br/>", normal_style))

    # Build PDF
    doc.build(elements)


if __name__ == "__main__":
    create_contributions_summary_pdf("contributions_summary.pdf")
    create_account_summary_pdf("account_summary.pdf")
    create_dividend_summary_pdf("dividend_summary.pdf")
