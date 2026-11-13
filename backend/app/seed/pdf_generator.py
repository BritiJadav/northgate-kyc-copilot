import os
import io
import math
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

def draw_header(c, title, doc_ref, jurisdiction="United Kingdom"):
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, title)
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#4B5563"))
    c.drawString(50, 735, f"Jurisdiction: {jurisdiction} | Document Reference: {doc_ref}")
    c.setStrokeColor(colors.HexColor("#D1D5DB"))
    c.setLineWidth(1)
    c.line(50, 725, 550, 725)
    c.setFillColor(colors.black)

def generate_pdf_with_lines(output_path: Path, title: str, doc_ref: str, pages_content: list, footer_template: str = "Page {page} of {total}"):
    """Generates a clean synthetic PDF with structured lines."""
    os.makedirs(output_path.parent, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter)
    total_pages = len(pages_content)

    for page_idx, lines in enumerate(pages_content, start=1):
        draw_header(c, title, doc_ref)
        c.setFont("Helvetica", 10)
        y = 700
        for line in lines:
            c.drawString(50, y, line)
            y -= 20
            if y < 80:
                break
        
        # Footer
        footer_text = footer_template.format(page=page_idx, total=total_pages)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawRightString(550, 40, footer_text)
        c.drawString(50, 40, "CONFIDENTIAL - SYNTHETIC DATA FOR DEMONSTRATION ONLY")
        c.setFillColor(colors.black)
        c.showPage()

    c.save()

def generate_module_a_documents():
    """Generates synthetic documents for Priya Raman, Harbourline Logistics, Okafor Trust."""
    # 1. Priya Raman
    # Expired Passport
    p1 = DATA_DIR / "priya_raman_passport.pdf"
    generate_pdf_with_lines(
        p1,
        "PASSPORT DOCUMENT - UNITED KINGDOM",
        "GBR-99201481",
        [
            "Full Name: Priya Raman",
            "Nationality: British Citizen",
            "Date of Birth: 14 Jun 1985",
            "Place of Birth: London, UK",
            "Date of Issue: 15 Sep 2016",
            "Date of Expiry: 14 Sep 2026",
            "Authority: Her Majesty's Passport Office",
            "Holder Signature: [Signed: Priya Raman]",
            "Status Note: Document expired prior to current verification date (12 Nov 2026).",
        ]
    )

    # Stale Proof of Address
    p2 = DATA_DIR / "priya_raman_utility_bill.pdf"
    generate_pdf_with_lines(
        p2,
        "THAMES WATER UTILITIES - BILLING STATEMENT",
        "TW-8829104",
        [
            "Customer: Ms Priya Raman",
            "Address: 42 Clarendon Gardens, London, NW3 6EP",
            "Statement Issue Date: 30 Jun 2026",
            "Billing Period: 01 Mar 2026 to 30 Jun 2026",
            "Amount Due: £142.80",
            "Payment Status: Paid in Full",
            "Notice: Utility bills must be dated within 3 months to satisfy KYC guidelines.",
        ]
    )

    # 2. Harbourline Logistics Ltd
    # Incomplete Bank Statement (Pages 1-2 of 4)
    p3 = DATA_DIR / "harbourline_bank_statement.pdf"
    generate_pdf_with_lines(
        p3,
        "METROPOLITAN COMMERCIAL BANK - ACCOUNT STATEMENT",
        "MCB-STMT-7749",
        [
            [
                "Account Holder: Harbourline Logistics Ltd",
                "Account Number: 8820-1928-44",
                "Sort Code: 20-40-71",
                "Statement Period: 01 Oct 2026 - 31 Oct 2026",
                "Opening Balance: £250,420.00",
                "Total Credits: £84,100.00",
                "Total Debits: £62,310.00",
                "Closing Balance: £272,210.00",
                "Continued on subsequent pages...",
            ],
            [
                "Account Holder: Harbourline Logistics Ltd",
                "Transaction Summary (continued)",
                "2026-10-05 BACS Transfer Port Fees -£12,400.00",
                "2026-10-12 Customer Payment Ocean Freight +£34,000.00",
                "2026-10-19 Fuel Surcharge -£8,250.00",
                "2026-10-26 Logistics Handling Fee +£22,100.00",
                "End of section 2. Please turn to page 3 for detailed audit schedule.",
            ]
        ],
        footer_template="Page {page} of 4" # Deliberately only 2 pages generated of 4!
    )

    # Certificate of Incorporation for Harbourline
    p4 = DATA_DIR / "harbourline_incorp_cert.pdf"
    generate_pdf_with_lines(
        p4,
        "COMPANIES HOUSE - CERTIFICATE OF INCORPORATION",
        "CRN-11029384",
        [
            "Company Name: Harbourline Logistics Ltd",
            "Company Number: 11029384",
            "Incorporated On: 14 February 2017",
            "Company Type: Private Limited Company",
            "Registered Office: Unit 4 Dockside Business Park, Southampton, SO14 2AQ",
            "Director: Robert Cole (Appointed 14 Feb 2017)",
            "Authentication: Verified by Registrar of Companies for England and Wales",
        ]
    )

    # 3. Okafor Family Trust
    # Incomplete Trust Deed (Pages 1-11 of 12)
    p5 = DATA_DIR / "okafor_trust_deed.pdf"
    trust_pages = []
    for i in range(1, 12):
        if i == 1:
            trust_pages.append([
                "SETTLEMENT DEED OF THE OKAFOR FAMILY TRUST",
                "Dated: 15 November 2015",
                "Settlor: Amara Okafor",
                "Trustee: Emeka Okafor",
                "Governing Law: Laws of England and Wales",
                "Clause 1: Definition of the Trust Fund and Initial Property",
            ])
        else:
            trust_pages.append([
                f"OKAFOR FAMILY TRUST DEED - CLAUSE {i}",
                f"Section {i}.1 Powers of Investment and Administration",
                f"Section {i}.2 Remuneration and Indemnity of Trustees",
                f"Section {i}.3 Application of Capital and Income during Trust Period",
                "Document continues on following page...",
            ])
    generate_pdf_with_lines(
        p5,
        "OKAFOR FAMILY TRUST - DEED OF SETTLEMENT",
        "TR-2015-OKAFOR",
        trust_pages,
        footer_template="Page {page} of 12" # Deliberately ends at 11 of 12!
    )

def generate_module_b_documents():
    """Generates synthetic incorporation documents for companies A, B, C, D, E."""
    # COMPANY A: Alder & Finch Ltd
    # Clean register: Nadia Finch 60%, Owen Alder 40%
    generate_pdf_with_lines(
        DATA_DIR / "alder_finch_register.pdf",
        "ALDER & FINCH LTD - REGISTER OF MEMBERS",
        "REG-AF-2021",
        [
            [
                "Company Name: Alder & Finch Ltd",
                "Company Number: 11892041 | Date: Current Register as at 01 September 2026",
                "Total Issued Share Capital: 100 Ordinary Shares of £1.00 each",
                "",
                "MEMBER REGISTER ENTRIES:",
                "1. Nadia Finch",
                "   Address: 14 Highbury Grove, London, N5 2EF",
                "   Shares Held: 60 Ordinary Shares (Certificate #AF-001)",
                "   Percentage of Issued Capital: 60.0%",
                "   Date Registered: 15 April 2021",
                "",
                "2. Owen Alder",
                "   Address: 8 Bishopgate Mews, Bristol, BS1 5RR",
                "   Shares Held: 40 Ordinary Shares (Certificate #AF-002)",
                "   Percentage of Issued Capital: 40.0%",
                "   Date Registered: 15 April 2021",
                "",
                "Officers of the Company:",
                "- Director: Nadia Finch (Appointed 15 April 2021)",
                "- Director: Owen Alder (Appointed 15 April 2021)",
                "Certified as a true and accurate register: [Signed: Nadia Finch, Director]",
            ]
        ]
    )

    # COMPANY B: Brightwave Software Ltd
    # Register + Articles with two classes: Class A (1 vote), Class B (10 votes)
    generate_pdf_with_lines(
        DATA_DIR / "brightwave_register.pdf",
        "BRIGHTWAVE SOFTWARE LTD - REGISTER OF MEMBERS",
        "REG-BW-2022",
        [
            [
                "Company Name: Brightwave Software Ltd",
                "Company Registration Number: 13948102",
                "Total Issued Shares: 1,500 Shares (1,000 Class A Ordinary, 500 Class B Ordinary)",
                "",
                "SHAREHOLDINGS AS AT 15 OCTOBER 2026:",
                "1. Ines Duarte",
                "   Share Class: Class A Ordinary Shares",
                "   Number of Shares: 600",
                "   Voting Power: 1 vote per share as defined in Articles of Association",
                "   Direct Shareholding: 40.0% of total issued share capital",
                "",
                "2. Lumen Growth LP",
                "   Share Class: Class B Ordinary Shares",
                "   Number of Shares: 500",
                "   Voting Power: 10 votes per share as defined in Articles of Association",
                "   Direct Shareholding: 33.33% of total issued share capital",
                "",
                "3. Kofi Mensah",
                "   Share Class: Class A Ordinary Shares",
                "   Number of Shares: 400",
                "   Voting Power: 1 vote per share as defined in Articles of Association",
                "   Direct Shareholding: 26.67% of total issued share capital",
            ]
        ]
    )

    generate_pdf_with_lines(
        DATA_DIR / "brightwave_articles.pdf",
        "BRIGHTWAVE SOFTWARE LTD - ARTICLES OF ASSOCIATION",
        "ART-BW-2022",
        [
            [
                "BRIGHTWAVE SOFTWARE LTD - ARTICLES OF ASSOCIATION",
                "Adopted by Special Resolution on 10 September 2022",
                "",
                "Article 4: Share Classes and Voting Rights",
                "4.1 The share capital of the Company consists of Class A Ordinary Shares and Class B Ordinary Shares.",
                "4.2 Every holder of Class A Ordinary Shares present in person or by proxy shall have one (1) vote for every Class A share held.",
                "4.3 Every holder of Class B Ordinary Shares present in person or by proxy shall have ten (10) votes for every Class B share held.",
                "4.4 Total voting rights on any poll shall be calculated as: (Class A Shares * 1) + (Class B Shares * 10).",
                "",
                "Article 5: Dividends and Liquidation",
                "5.1 Class A and Class B shares shall rank pari passu in respect of dividend distributions and capital returns upon winding up.",
            ]
        ]
    )

    # COMPANY C: Calder Marine Services Ltd
    # Stale 2023 Register + Skewed Scan of August 2025 Stock Transfer
    generate_pdf_with_lines(
        DATA_DIR / "calder_register_2023.pdf",
        "CALDER MARINE SERVICES LTD - REGISTER OF MEMBERS (2023)",
        "REG-CM-2023",
        [
            [
                "Company: Calder Marine Services Ltd | CRN: 09823145",
                "Register of Members - Historic Entry dated 10 May 2023",
                "Total Issued Capital: 200 Ordinary Shares of £1.00 each",
                "",
                "1. Lars Pedersen",
                "   Shares Held: 150 Ordinary Shares",
                "   Percentage: 75.0%",
                "   Registered: 01 March 2018",
                "",
                "2. Maya Iyer",
                "   Shares Held: 50 Ordinary Shares",
                "   Percentage: 25.0%",
                "   Registered: 01 March 2018",
                "",
                "Note: Certified historical record as at 10 May 2023. Subject to subsequent transfers.",
            ]
        ]
    )

    # Generate Skewed Scan Image for Calder Marine Stock Transfer Form
    generate_calder_scan_image()

    # COMPANY D: Rowan Bay Consulting Ltd
    # Memorandum + Articles only (NO Register of Members!)
    generate_pdf_with_lines(
        DATA_DIR / "rowan_bay_memorandum.pdf",
        "MEMORANDUM OF ASSOCIATION - ROWAN BAY CONSULTING LTD",
        "MEM-RB-2019",
        [
            [
                "MEMORANDUM OF ASSOCIATION",
                "Rowan Bay Consulting Ltd (Company No. 12034981)",
                "Incorporated under the Companies Act 2006 on 20 November 2019",
                "",
                "Each subscriber to this memorandum of association wishes to form a company",
                "and agrees to become a member and take at least one share.",
                "",
                "Subscriber Names and Share Allocation at Incorporation:",
                "1. Arthur Pendelton - 1 Ordinary Share of £1.00",
                "2. Beatrice Webb - 1 Ordinary Share of £1.00",
                "",
                "Dated this 20th day of November 2019.",
                "Note: Formation document subscriber list only. Does not reflect current shareholdings.",
            ]
        ]
    )

    generate_pdf_with_lines(
        DATA_DIR / "rowan_bay_articles.pdf",
        "ARTICLES OF ASSOCIATION - ROWAN BAY CONSULTING LTD",
        "ART-RB-2019",
        [
            [
                "ARTICLES OF ASSOCIATION OF ROWAN BAY CONSULTING LTD",
                "Adopted upon incorporation on 20 November 2019",
                "",
                "The Model Articles for Private Companies Limited by Shares apply to the Company.",
                "No bespoke share classes or special voting arrangements exist.",
                "Directors have power to allot shares subject to statutory pre-emption rights.",
                "[End of document]",
            ]
        ]
    )

    # COMPANY E: Kestrel Trading Ltd (The complex multi-tier group)
    # Tier 1: Kestrel Trading Ltd Register (UK)
    generate_pdf_with_lines(
        DATA_DIR / "kestrel_register.pdf",
        "KESTREL TRADING LTD - REGISTER OF MEMBERS",
        "REG-KT-2023",
        [
            [
                "Company Name: Kestrel Trading Ltd",
                "Company Number: 14829301 | Date of Register: 15 October 2026",
                "Total Issued Share Capital: 1,000 Ordinary Shares of £1.00 each",
                "",
                "REGISTERED SHAREHOLDERS:",
                "1. Halden Holdings B.V.",
                "   Registered Address: Keizersgracht 421, 1016 EK Amsterdam, Netherlands",
                "   Shares Held: 480 Ordinary Shares (48.0% of total issued equity)",
                "",
                "2. Pilar Investments Ltd",
                "   Registered Address: Wickhams Cay 1, Road Town, Tortola, British Virgin Islands",
                "   Shares Held: 270 Ordinary Shares (27.0% of total issued equity)",
                "",
                "3. Samira Qadri",
                "   Registered Address: 27 Kensington Gate, London, W8 5NA",
                "   Shares Held: 150 Ordinary Shares (15.0% of total issued equity)",
                "",
                "4. Meridian Nominees Ltd (as nominee)",
                "   Registered Address: 55 Bishopsgate, London, EC2N 3AS",
                "   Shares Held: 100 Ordinary Shares (10.0% of total issued equity)",
                "   Capacity Note: Meridian Nominees Ltd holds shares solely as nominee for an undisclosed principal.",
                "",
                "Officers: Director: Samira Qadri (Appointed 18 January 2023)",
            ]
        ]
    )

    # Tier 2: Halden Holdings B.V. Register (Netherlands)
    generate_pdf_with_lines(
        DATA_DIR / "halden_holdings_register.pdf",
        "HALDEN HOLDINGS B.V. - AANDEELHOUDERSREGISTER",
        "REG-HH-NL-2022",
        [
            [
                "HALDEN HOLDINGS B.V.",
                "KvK-nummer: 84910283 | RSIN: 863492810",
                "Statutaire zetel: Amsterdam, Nederland",
                "Aandeelhoudersregister (Shareholder Register):",
                "",
                "1. Norvik Group S.A.",
                "   Zetel: 18 Boulevard Royal, L-2449 Luxembourg",
                "   Aandelenbezit: 60% van het geplaatste kapitaal (60.0% interest)",
                "",
                "2. Tomas Berg",
                "   Geboortedatum (DOB): 02/04/1968",
                "   Nationaliteit: Zweeds (Swedish)",
                "   Adres: Strandvägen 34, Stockholm, Zweden",
                "   Aandelenbezit: 40% van het geplaatste kapitaal (40.0% interest)",
                "",
                "Geregistreerd te Amsterdam. Bestuurder: Tomas Berg.",
            ]
        ]
    )

    # Tier 3: Norvik Group S.A. Register (French/Luxembourg)
    generate_pdf_with_lines(
        DATA_DIR / "norvik_group_register_fr.pdf",
        "NORVIK GROUP S.A. - REGISTRE DES ACTIONNAIRES",
        "REG-NG-LU-2021",
        [
            [
                "NORVIK GROUP S.A. - SOCIÉTÉ ANONYME",
                "RCS Luxembourg B 239.401 | Capital Social: 50.000 EUR",
                "Registre des actionnaires et bénéficiaires effectifs:",
                "",
                "Actionnaire 1: Elena Voss",
                "Date de naissance: 19/08/1974 | Nationalité: Allemande",
                "Adresse: 12 Rue de la Reine, L-2418 Luxembourg",
                "Actions détenues: 50 actions ordinaires (50.0% du capital social)",
                "",
                "Actionnaire 2: Thomas Berg",
                "Date de naissance: 02/04/1968 | Nationalité: Suédoise",
                "Adresse: Strandvägen 34, Stockholm, Suède",
                "Actions détenues: 50 actions ordinaires (50.0% du capital social)",
                "",
                "Certifié conforme par le Conseil d'Administration de Norvik Group S.A.",
            ]
        ]
    )

    # Pilar Investments Ltd - BVI Certificate of Incumbency
    generate_pdf_with_lines(
        DATA_DIR / "pilar_investments_incumbency.pdf",
        "PILAR INVESTMENTS LTD - CERTIFICATE OF INCUMBENCY",
        "BVI-INCUMB-2023",
        [
            [
                "BRITISH VIRGIN ISLANDS - CERTIFICATE OF INCUMBENCY",
                "Company Name: Pilar Investments Ltd | BVI Company Number: 2049182",
                "Registered Agent: Trident Trust Company (BVI) Limited",
                "",
                "SHARE CAPITAL AND REGISTERED MEMBERS:",
                "Authorized Share Capital: 50,000 USD divided into 50,000 shares of 1.00 USD each.",
                "Issued Shares: 10,000 shares issued as fully paid.",
                "",
                "Registered Shareholder:",
                "Wren Fiduciary Ltd, as trustee",
                "Address: P.O. Box 146, Road Town, Tortola, British Virgin Islands",
                "Number of Shares: 10,000 Shares (100.0%)",
                "Beneficiary Status: No underlying beneficiaries are declared or named on the register.",
                "",
                "Issued by Registered Agent on 14 March 2023. [Seal: Trident Trust Company]",
            ]
        ]
    )

def generate_calder_scan_image():
    """Generates a realistic skewed scan PNG image of the 2025 stock transfer form."""
    img = Image.new("RGB", (800, 1000), color=(250, 248, 245))
    draw = ImageDraw.Draw(img)

    # Simulate document borders and text
    draw.rectangle([(40, 40), (760, 960)], outline=(120, 120, 120), width=2)
    draw.rectangle([(45, 45), (755, 955)], outline=(180, 180, 180), width=1)

    title = "STOCK TRANSFER FORM - CALDER MARINE SERVICES LTD"
    draw.text((80, 70), title, fill=(20, 20, 20))
    draw.line([(80, 95), (720, 95)], fill=(80, 80, 80), width=2)

    fields = [
        ("Company Name:", "Calder Marine Services Ltd (CRN: 09823145)"),
        ("Date of Transfer:", "02 August 2025"),
        ("Transferor (Seller):", "Lars Pedersen"),
        ("Address of Transferor:", "19 Quayside Walk, Hull, HU1 2TB"),
        ("Transferee (Buyer):", "Maya Iyer"),
        ("Address of Transferee:", "7 Marine Crescent, Hull, HU3 4PT"),
        ("Number of Shares:", "60 (Sixty) Ordinary Shares of £1.00 each"),
        ("Consideration Paid:", "£75,000.00"),
        ("Transferor Signature:", "[Signed: Lars Pedersen]"),
        ("Transferee Signature:", "[Signed: Maya Iyer]"),
        ("Witness:", "Arthur Campbell, Solicitor, Hull"),
        ("Status Stamp:", "STAMP DUTY PAID - HM REVENUE & CUSTOMS 10 AUG 2025"),
    ]

    y = 130
    for label, val in fields:
        draw.text((80, y), label, fill=(50, 50, 50))
        draw.text((280, y), val, fill=(10, 10, 10))
        y += 45

    draw.text((80, 750), "NOTE: Following this transfer, holdings are: Maya Iyer 110 shares (55%),", fill=(40, 40, 40))
    draw.text((80, 780), "Lars Pedersen 90 shares (45%) of total 200 issued shares.", fill=(40, 40, 40))

    # Skew and rotate slightly for realistic scanned appearance
    rotated = img.rotate(1.8, resample=Image.BICUBIC, expand=True, fillcolor=(235, 233, 230))
    
    # Save image
    out_path = DATA_DIR / "calder_stock_transfer_scan.png"
    rotated.save(out_path)

def extract_and_index_documents():
    """
    Uses pdfplumber to extract page-numbered, line-numbered text from all generated PDFs.
    Saves text indices to backend/data/{doc_name}.txt and a master text_layers.json.
    """
    import pdfplumber
    import json

    master_text_layers = {}

    for pdf_file in DATA_DIR.glob("*.pdf"):
        doc_lines = []
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                for line_num, line_text in enumerate(lines, start=1):
                    doc_lines.append({
                        "doc": pdf_file.name,
                        "page": page_num,
                        "line": line_num,
                        "text": line_text,
                    })

        master_text_layers[pdf_file.name] = doc_lines

        # Write text version with bracket citations: [doc:file.pdf p1 L1] Text
        txt_path = DATA_DIR / f"{pdf_file.stem}_indexed.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            for item in doc_lines:
                f.write(f"[doc:{item['doc']} p{item['page']} L{item['line']}] {item['text']}\n")

    # Add text layer for Calder Marine stock transfer scan
    calder_scan_lines = [
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 1, "text": "STOCK TRANSFER FORM - CALDER MARINE SERVICES LTD"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 2, "text": "Company Name: Calder Marine Services Ltd (CRN: 09823145)"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 3, "text": "Date of Transfer: 02 August 2025"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 4, "text": "Transferor (Seller): Lars Pedersen"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 5, "text": "Address of Transferor: 19 Quayside Walk, Hull, HU1 2TB"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 6, "text": "Transferee (Buyer): Maya Iyer"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 7, "text": "Address of Transferee: 7 Marine Crescent, Hull, HU3 4PT"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 8, "text": "Number of Shares: 60 (Sixty) Ordinary Shares of £1.00 each"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 9, "text": "Consideration Paid: £75,000.00"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 10, "text": "Transferor Signature: [Signed: Lars Pedersen]"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 11, "text": "Transferee Signature: [Signed: Maya Iyer]"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 12, "text": "Witness: Arthur Campbell, Solicitor, Hull"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 13, "text": "Status Stamp: STAMP DUTY PAID - HM REVENUE & CUSTOMS 10 AUG 2025"},
        {"doc": "calder_stock_transfer_scan.png", "page": 1, "line": 14, "text": "NOTE: Following this transfer, holdings are: Maya Iyer 110 shares (55%), Lars Pedersen 90 shares (45%) of total 200 issued shares."},
    ]
    master_text_layers["calder_stock_transfer_scan.png"] = calder_scan_lines
    txt_path = DATA_DIR / "calder_stock_transfer_scan_indexed.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        for item in calder_scan_lines:
            f.write(f"[doc:{item['doc']} p{item['page']} L{item['line']}] {item['text']}\n")

    with open(DATA_DIR / "master_text_layers.json", "w", encoding="utf-8") as f:
        json.dump(master_text_layers, f, indent=2)

def generate_all_seed_files():
    """Generates all synthetic PDF/PNG documents and their line-numbered text representations."""
    os.makedirs(DATA_DIR, exist_ok=True)
    generate_module_a_documents()
    generate_module_b_documents()
    extract_and_index_documents()
    print(f"Synthetic seed documents generated successfully in {DATA_DIR}")

if __name__ == "__main__":
    generate_all_seed_files()
