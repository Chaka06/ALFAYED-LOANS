from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_num, total_pages):
        width, height = A4
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.grey)
        self.drawRightString(width - 2*cm, 1.5*cm, f"Page {page_num} sur {total_pages}")
        self.setStrokeColor(colors.HexColor('#008751'))
        self.setLineWidth(1)
        self.line(2*cm, 2*cm, width - 2*cm, 2*cm)

def create_logo_placeholder():
    """Crée le logo ECOBANK"""
    try:
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logos', 'ecobank_logo.png')
        
        if os.path.exists(logo_path):
            return Image(logo_path, width=3*cm, height=2*cm)
    except:
        pass
    
    # Fallback si pas d'image
    return Paragraph("""
        <b>ECOBANK</b><br/>
        <i>Logo à insérer</i>
    """, ParagraphStyle('LogoPlaceholder', 
        fontSize=10, 
        alignment=TA_CENTER,
        textColor=colors.HexColor('#008751'),
        borderWidth=1,
        borderColor=colors.HexColor('#008751'),
        borderPadding=5
    ))

def create_seal_placeholder():
    """Crée le cachet de la banque"""
    try:
        seal_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'seals', 'bank_seal.png')
        
        if os.path.exists(seal_path):
            return Image(seal_path, width=3*cm, height=3*cm)
    except:
        pass
    
    # Fallback si pas d'image
    return Paragraph("""
        
    """, ParagraphStyle('SealPlaceholder', 
        
    ))

def create_manager_signature_placeholder():
    """Crée la signature du gestionnaire"""
    try:
        signature_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signatures', 'manager_signature.png')
        
        if os.path.exists(signature_path):
            return Image(signature_path, width=4*cm, height=2*cm)
    except:
        pass
    
    # Fallback si pas d'image
    return Paragraph("""
        <b>M. KOUASSI Jean-Claude</b><br/>
        <i>Responsable des Prêts</i><br/>
        <i>+225 05 04 00 12 72</i><br/>
        
    """, ParagraphStyle('SignaturePlaceholder', 
        fontSize=9, 
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f4e79'),
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=8
    ))

def generate_loan_certificate(loan_request):
    """Génère une attestation de prêt professionnelle"""
    
    # Vérifications préalables
    if loan_request.status != 'paye':
        raise ValueError("Le prêt doit être payé pour générer l'attestation")
    
    if not hasattr(loan_request.user, 'userprofile'):
        raise ValueError("Profil utilisateur manquant")
    
    profile = loan_request.user.userprofile
    if not profile.nom or not profile.prenom:
        raise ValueError("Nom et prénom requis dans le profil")
    
    # Créer le buffer PDF
    buffer = BytesIO()
    
    # Document PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5*cm,
        leftMargin=2.5*cm,
        topMargin=3*cm,
        bottomMargin=3*cm,
        title=f"Attestation de Prêt ECO-{loan_request.id:06d}",
        author="ECOBANK",
        subject="Attestation de Prêt Bancaire"
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style titre principal
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontSize=22,
        spaceAfter=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f4e79'),
        fontName='Helvetica-Bold'
    )
    
    # Style sous-titre
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#008751'),
        fontName='Helvetica-Bold'
    )
    
    # Style section
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=13,
        spaceAfter=10,
        spaceBefore=20,
        textColor=colors.HexColor('#1f4e79'),
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    # Style texte normal
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14
    )
    
    # Style important
    important_style = ParagraphStyle(
        'ImportantText',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1f4e79'),
        backColor=colors.HexColor('#f8f9fa'),
        borderWidth=1,
        borderColor=colors.HexColor('#008751'),
        borderPadding=10
    )
    
    # Style déclaration
    declaration_style = ParagraphStyle(
        'Declaration',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=16,
        backColor=colors.HexColor('#f0f8f0'),
        borderWidth=2,
        borderColor=colors.HexColor('#008751'),
        borderPadding=15
    )
    
    # Contenu du document
    story = []
    
    # === EN-TÊTE OFFICIEL ===
    header_data = [
        [
            create_logo_placeholder(),
            
            Paragraph("""
                <b>ECOBANK CÔTE D'IVOIRE</b><br/>
                Société Anonyme au capital de 25 000 000 000 FCFA<br/>
                Siège Social : Boulevard de la République, Plateau, Abidjan<br/>
                RCCM : CI-ABJ-1995-B-12345 | N° Contribuable : 1234567890123<br/>
                Tél : +225 27 20 10 20 00 | Fax : +225 27 20 22 01 00<br/>
                Email : info@ecobank.ci | www.ecobank.com
            """, ParagraphStyle('BankInfo', fontSize=9, alignment=TA_CENTER, leading=11)),
            
            create_seal_placeholder()
        ]
    ]
    
    header_table = Table(header_data, colWidths=[4*cm, 9*cm, 4*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(header_table)
    
    # Ligne de séparation
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#008751')))
    story.append(Spacer(1, 20))
    
    # === TITRE PRINCIPAL ===
    story.append(Paragraph("ATTESTATION DE PRÊT BANCAIRE", title_style))
    story.append(Paragraph("CERTIFICAT D'OCTROI DE CRÉDIT", subtitle_style))
    
    # === RÉFÉRENCE ===
    ref_text = f"<b>RÉFÉRENCE DU DOSSIER : ECO-{loan_request.id:06d}</b>"
    story.append(Paragraph(ref_text, important_style))
    story.append(Spacer(1, 20))
    
    # === PRÉAMBULE ===
    preambule = """
    La présente attestation est délivrée à la demande de l'intéressé(e) pour servir et valoir ce que de droit.
    Nous, ECOBANK CÔTE D'IVOIRE, établissement de crédit agréé par la Banque Centrale des États de l'Afrique 
    de l'Ouest (BCEAO) sous le numéro d'agrément 001-CI-2023, certifions par les présentes avoir accordé 
    un prêt dans les conditions ci-après détaillées.
    """
    story.append(Paragraph(preambule, normal_style))
    story.append(Spacer(1, 20))
    
    # === IDENTIFICATION DU BÉNÉFICIAIRE ===
    story.append(Paragraph("I. IDENTIFICATION DU BÉNÉFICIAIRE", section_style))
    
    beneficiary_data = [
        ['Nom et Prénom :', f"{profile.nom} {profile.prenom}"],
        ['Date de naissance :', profile.date_naissance.strftime('%d/%m/%Y') if profile.date_naissance else 'Non renseignée'],
        ['Lieu de naissance :', getattr(profile, 'lieu_naissance', 'Non renseigné') or 'Non renseigné'],
        ['Profession :', profile.profession or 'Non renseignée'],
        ['Situation matrimoniale :', profile.get_situation_matrimoniale_display() if profile.situation_matrimoniale else 'Non renseignée'],
        ['Adresse complète :', profile.adresse or 'Non renseignée'],
        ['Contact :', getattr(profile, 'telephone', 'Non renseigné') or 'Non renseigné'],
    ]
    
    beneficiary_table = Table(beneficiary_data, colWidths=[4.5*cm, 12.5*cm])
    beneficiary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(beneficiary_table)
    story.append(Spacer(1, 20))
    
    # === CARACTÉRISTIQUES DU PRÊT ===
    story.append(Paragraph("II. CARACTÉRISTIQUES DU PRÊT ACCORDÉ", section_style))
    
    # Calculs et formatage
    date_demande = loan_request.date_demande.strftime('%d/%m/%Y') if loan_request.date_demande else 'Non renseignée'
    date_validation = loan_request.date_validation.strftime('%d/%m/%Y') if loan_request.date_validation else 'Non renseignée'
    date_octroi = loan_request.date_paiement.strftime('%d/%m/%Y') if loan_request.date_paiement else 'Non renseignée'
    date_echeance = loan_request.date_fin_remboursement.strftime('%d/%m/%Y') if loan_request.date_fin_remboursement else 'Non calculée'
    
    duree_annees = loan_request.duree_remboursement_mois // 12
    duree_mois_restants = loan_request.duree_remboursement_mois % 12
    duree_text = f"{duree_annees} an(s)" + (f" et {duree_mois_restants} mois" if duree_mois_restants > 0 else "")
    
    montant_lettres = number_to_words(int(loan_request.montant))
    
    loan_data = [
        ['Date de la demande :', date_demande],
        ['Date de validation :', date_validation],
        ['Date d\'octroi du prêt :', date_octroi],
        ['Montant du prêt accordé :', f"{loan_request.montant:,.0f} FCFA"],
        ['Montant en lettres :', montant_lettres],
        ['Montant de l\'apport (15%) :', f"{loan_request.montant_avance:,.0f} FCFA"],
        ['Durée de remboursement :', f"{loan_request.duree_remboursement_mois} mois ({duree_text})"],
        ['Date limite de remboursement :', date_echeance],
        ['Objet du financement :', loan_request.motif[:200] + "..." if len(loan_request.motif) > 200 else loan_request.motif],
        ['Clé de référence unique :', loan_request.payment_key or 'Non générée'],
    ]
    
    loan_table = Table(loan_data, colWidths=[5*cm, 12*cm])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e8')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#008751')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        # Mise en évidence du montant
        ('BACKGROUND', (1, 3), (1, 3), colors.HexColor('#fff3cd')),
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 3), (1, 3), 11),
        ('TEXTCOLOR', (1, 3), (1, 3), colors.HexColor('#856404')),
    ]))
    
    story.append(loan_table)
    story.append(Spacer(1, 20))
    
    # === CONDITIONS DE REMBOURSEMENT ===
    story.append(Paragraph("III. CONDITIONS ET MODALITÉS DE REMBOURSEMENT", section_style))
    
    conditions = f"""
    <b>A. CONDITIONS GÉNÉRALES :</b><br/>
    • Le présent prêt a été accordé après étude approfondie du dossier de crédit du demandeur selon nos procédures internes.<br/>
    • L'emprunteur s'engage à rembourser le capital selon l'échéancier convenu d'un commun accord.<br/>
    • Le remboursement s'effectue exclusivement auprès de nos services agréés et habilités.<br/>
    • Tout retard de paiement sera soumis aux pénalités prévues par nos conditions générales de crédit.<br/>
    • Le prêt est soumis aux dispositions du Code monétaire et financier de l'UMOA.<br/><br/>
    
    <b>B. MODALITÉS PRATIQUES DE REMBOURSEMENT :</b><br/>
    • Durée maximale autorisée : Sept (7) ans soit quatre-vingt-quatre (84) mois<br/>
    • Mode de remboursement : Paiements effectués auprès du gestionnaire de compte désigné<br/>
    • Identification obligatoire : Présentation systématique de la clé de référence unique<br/>
    • Gestionnaire responsable : Service des Prêts ECOBANK<br/>
    • Contact direct gestionnaire : +225 05 04 00 12 72<br/>
    • Service d'assistance WhatsApp : https://wa.me/2250504001272<br/>
    • Horaires de service : Lundi au Vendredi de 08h00 à 17h00<br/><br/>
    
    <b>C. DISPOSITIONS PARTICULIÈRES :</b><br/>
    • La clé de référence est strictement personnelle et confidentielle<br/>
    • Toute perte ou vol de clé doit être immédiatement signalé à nos services<br/>
    • Les remboursements anticipés partiels ou totaux sont autorisés sans pénalité<br/>
    • Un échéancier de remboursement détaillé peut être fourni sur simple demande<br/>
    • Possibilité de report d'échéance en cas de difficultés temporaires (sous conditions)
    """
    
    story.append(Paragraph(conditions, normal_style))
    story.append(Spacer(1, 20))
    
    # === CONTACT ET ASSISTANCE ===
    story.append(Paragraph("IV. INFORMATIONS DE CONTACT ET ASSISTANCE", section_style))
    
    contact_data = [
        ['Service clientèle :', '+225 27 20 10 20 00'],
        ['Gestionnaire prêts :', '+225 05 04 00 12 72'],
        ['Assistance WhatsApp :', 'https://wa.me/2250504001272'],
        ['Email :', 'prets@ecobank.ci'],
        ['Horaires d\'ouverture :', 'Lundi au Vendredi : 08h00 - 17h00, Samedi : 08h00 - 12h00'],
        ['Agence de référence :', 'ECOBANK Plateau - Boulevard de la République'],
        ['Code SWIFT :', 'ECOCCIAC'],
    ]
    
    contact_table = Table(contact_data, colWidths=[4.5*cm, 12.5*cm])
    contact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f3f4')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(contact_table)
    story.append(Spacer(1, 25))
    
    # === DÉCLARATION OFFICIELLE ===
    story.append(Paragraph("V. DÉCLARATION OFFICIELLE ET CERTIFICATION", section_style))
    
    declaration_text = f"""
    Nous, ECOBANK CÔTE D'IVOIRE, établissement bancaire de droit ivoirien, société anonyme au capital 
    de vingt-cinq milliards (25 000 000 000) de francs CFA, dont le siège social est sis Boulevard de la République, 
    Plateau, Abidjan, immatriculée au Registre du Commerce et du Crédit Mobilier d'Abidjan sous le numéro CI-ABJ-1995-B-12345, 
    agréée en qualité d'établissement de crédit par la Banque Centrale des États de l'Afrique de l'Ouest (BCEAO) 
    et soumise à sa supervision prudentielle,
    
    <b>CERTIFIONS ET ATTESTONS PAR LES PRÉSENTES QUE :</b>
    
    Le prêt d'un montant de <b>{loan_request.montant:,.0f} FCFA (en toutes lettres : {montant_lettres})</b> 
    a été officiellement accordé, approuvé et débloqué au profit de <b>Monsieur/Madame {profile.nom} {profile.prenom}</b>, 
    en date du <b>{date_octroi}</b>, conformément à nos procédures internes de crédit et aux réglementations 
    en vigueur de l'Union Monétaire Ouest Africaine (UMOA).
    
    Cette attestation est délivrée pour servir et valoir ce que de droit devant toute autorité administrative, 
    judiciaire, notariale ou tout organisme public ou privé qui en ferait la demande. Elle peut être utilisée 
    comme justificatif officiel et authentique dans le cadre des démarches légitimes du bénéficiaire.
    
    La présente attestation est établie en un exemplaire original et ne peut faire l'objet d'aucune reproduction, 
    copie ou duplication sans l'autorisation expresse et écrite de notre direction générale.
    
    EN FOI DE QUOI, nous avons établi la présente attestation.
    """
    
    story.append(Paragraph(declaration_text, declaration_style))
    story.append(Spacer(1, 25))
    
    # === MENTIONS LÉGALES ===
    legal_mentions = """
    <b>MENTIONS LÉGALES OBLIGATOIRES :</b> ECOBANK Côte d'Ivoire - Société Anonyme au capital de 25 000 000 000 FCFA - 
    Siège social : Boulevard de la République, Plateau, BP V 003 Abidjan 01 - RCCM CI-ABJ-1995-B-12345 - 
    Agrément BCEAO n° 001-CI-2023 - Code SWIFT : ECOCCIAC - Membre du Système de Paiement Régional de l'UMOA - 
    Membre du Fonds de Garantie des Dépôts de l'UMOA - Soumis au contrôle de la BCEAO et de la Commission Bancaire de l'UMOA.
    """
    
    story.append(Paragraph(legal_mentions, ParagraphStyle(
        'Legal',
        parent=normal_style,
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_JUSTIFY,
        leading=10
    )))
    story.append(Spacer(1, 25))
    
    # === SECTION SIGNATURES ===
    lieu_date = f"Fait à Abidjan, le {datetime.now().strftime('%d %B %Y')}"
    
    signature_data = [
        [lieu_date, '', ''],
        ['', '', ''],
        ['LE BÉNÉFICIAIRE', '', 'LA BANQUE'],
        ['', '', ''],
        [f'{profile.nom} {profile.prenom}', '', 'ECOBANK CÔTE D\'IVOIRE'],
        ['', '', ''],
        ['', '', 'Le Gestionnaire des Prêts'],
        ['', '', ''],
        ['(Signature précédée de la mention', '', create_manager_signature_placeholder()],
        ['"Lu et approuvé")', '', ''],
        ['', '', '+ Cachet officiel de la banque'],
    ]
    
    signature_table = Table(signature_data, colWidths=[5.5*cm, 6*cm, 5.5*cm])
    signature_table.setStyle(TableStyle([
        # Lieu et date
        ('SPAN', (0, 0), (2, 0)),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 12),
        
        # Titres
        ('ALIGN', (0, 2), (0, 2), 'CENTER'),
        ('ALIGN', (2, 2), (2, 2), 'CENTER'),
        ('FONTNAME', (0, 2), (0, 2), 'Helvetica-Bold'),
        ('FONTNAME', (2, 2), (2, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (2, 2), 11),
        ('TEXTCOLOR', (0, 2), (2, 2), colors.HexColor('#1f4e79')),
        
        # Noms
        ('ALIGN', (0, 4), (0, 4), 'CENTER'),
        ('ALIGN', (2, 4), (2, 4), 'CENTER'),
        ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
        ('FONTNAME', (2, 4), (2, 4), 'Helvetica-Bold'),
        
        # Fonction
        ('ALIGN', (2, 6), (2, 6), 'CENTER'),
        ('FONTNAME', (2, 6), (2, 6), 'Helvetica'),
        ('FONTSIZE', (2, 6), (2, 6), 10),
        
        # Signature gestionnaire
        ('ALIGN', (2, 8), (2, 8), 'CENTER'),
        
        # Instructions et cachet
        ('ALIGN', (0, 8), (0, 9), 'CENTER'),
        ('ALIGN', (2, 10), (2, 10), 'CENTER'),
        ('FONTSIZE', (0, 8), (0, 9), 9),
        ('FONTSIZE', (2, 10), (2, 10), 9),
        ('FONTNAME', (0, 8), (0, 9), 'Helvetica-Oblique'),
        ('FONTNAME', (2, 10), (2, 10), 'Helvetica-Oblique'),
        ('TEXTCOLOR', (2, 10), (2, 10), colors.HexColor('#6c757d')),
        
        # Espacement
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        
        # Lignes pour signatures
        ('LINEBELOW', (0, 5), (0, 5), 1, colors.black),
        ('LINEBELOW', (2, 7), (2, 7), 1, colors.black),
    ]))
    
    story.append(signature_table)
    story.append(Spacer(1, 20))
    
    # === PIED DE PAGE FINAL ===
    footer_info = f"""
    <i>Document authentique généré automatiquement par le Système de Gestion des Prêts ECOBANK 
    le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')} - Référence système : ECO-{loan_request.id:06d} - 
    Empreinte numérique : {hash(f"{loan_request.id}{loan_request.payment_key}")}</i><br/>
    <b>VALIDITÉ :</b> Ce document est authentique et sa véracité peut être vérifiée auprès de nos services 
    en présentant la référence système ci-dessus.
    """
    
    story.append(Paragraph(footer_info, ParagraphStyle(
        'FooterInfo',
        parent=normal_style,
        fontSize=8,
        textColor=colors.HexColor('#6c757d'),
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique',
        leading=10
    )))
    
    # Construction du PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Récupération du contenu
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def number_to_words(number):
    """Convertit un nombre en lettres françaises"""
    if number == 0:
        return "zéro"
    
    # Nombres de base
    ones = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    teens = ["dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf"]
    tens = ["", "", "vingt", "trente", "quarante", "cinquante", "soixante", "soixante-dix", "quatre-vingt", "quatre-vingt-dix"]
    
    def convert_hundreds(n):
        result = ""
        
        if n >= 100:
            if n // 100 == 1:
                result += "cent"
            else:
                result += ones[n // 100] + " cent"
            if n % 100 != 0:
                result += " "
            n %= 100
        
        if n >= 20:
            if n >= 80:
                if n == 80:
                    result += "quatre-vingts"
                else:
                    result += "quatre-vingt"
                    if n % 10 != 0:
                        result += "-" + ones[n % 10]
            elif n >= 70:
                result += "soixante"
                if n % 10 == 1:
                    result += " et onze"
                else:
                    result += "-" + teens[(n % 10)]
            else:
                result += tens[n // 10]
                if n % 10 != 0:
                    if n // 10 == 2 and n % 10 == 1:
                        result += " et un"
                    else:
                        result += "-" + ones[n % 10]
        elif n >= 10:
            result += teens[n - 10]
        elif n > 0:
            result += ones[n]
        
        return result
    
    if number < 1000:
        return convert_hundreds(number)
    elif number < 1000000:
        thousands = number // 1000
        remainder = number % 1000
        result = ""
        if thousands == 1:
            result = "mille"
        else:
            result = convert_hundreds(thousands) + " mille"
        if remainder > 0:
            result += " " + convert_hundreds(remainder)
        return result
    elif number < 1000000000:
        millions = number // 1000000
        remainder = number % 1000000
        result = convert_hundreds(millions) + " million"
        if millions > 1:
            result += "s"
        if remainder > 0:
            if remainder < 1000:
                result += " " + convert_hundreds(remainder)
            else:
                result += " " + convert_hundreds(remainder // 1000) + " mille"
                if remainder % 1000 > 0:
                    result += " " + convert_hundreds(remainder % 1000)
        return result
    else:
        return "nombre trop grand"