from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

# Import PIL pour le filigrane
try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self._logo_path = None
        # Chercher le logo pour le filigrane
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logos', 'investor_logo.png'),
        ]
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            for static_dir in settings.STATICFILES_DIRS:
                logo_paths.append(os.path.join(static_dir, 'images', 'logos', 'investor_logo.png'))
        
        for logo_path in logo_paths:
            if logo_path and os.path.exists(logo_path):
                self._logo_path = logo_path
                break

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_watermark()
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_watermark(self):
        """Dessine le logo en filigrane sur chaque page"""
        if not self._logo_path or not PILImage:
            return
        
        try:
            width, height = A4
            # Dessiner le logo en filigrane au centre de la page
            img = PILImage.open(self._logo_path)
            # Convertir en mode RGBA pour la transparence
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Créer une version transparente du logo
            watermark_size = 10 * cm  # Taille du filigrane
            img.thumbnail((int(watermark_size * 2.83), int(watermark_size * 2.83)), PILImage.Resampling.LANCZOS)
            
            # Créer une image transparente pour le filigrane
            watermark = PILImage.new('RGBA', img.size, (255, 255, 255, 0))
            # Ajouter le logo avec opacité réduite
            alpha = img.split()[3] if len(img.split()) > 3 else None
            if alpha:
                alpha = alpha.point(lambda p: int(p * 0.06))  # 6% d'opacité pour filigrane discret
                img.putalpha(alpha)
            
            watermark.paste(img, (0, 0), img)
            
            # Dessiner le filigrane au centre avec rotation
            self.saveState()
            self.translate(width / 2, height / 2)
            self.rotate(45)  # Rotation de 45 degrés pour effet filigrane classique
            self.drawImage(ImageReader(watermark), -watermark_size/2, -watermark_size/2, 
                          width=watermark_size, height=watermark_size, mask='auto')
            self.restoreState()
        except Exception:
            # Si erreur, on continue sans filigrane
            pass

    def draw_page_number(self, page_num, total_pages):
        width, height = A4
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#6c757d'))
        self.drawRightString(width - 2*cm, 1.5*cm, f"Page {page_num}/{total_pages}")
        self.setStrokeColor(colors.HexColor('#2C3E50'))
        self.setLineWidth(0.5)
        self.line(2*cm, 2*cm, width - 2*cm, 2*cm)

def create_logo_placeholder():
    """Crée le logo Investor Banque pour le PDF"""
    logo_paths = [
        # Chemin direct depuis BASE_DIR
        os.path.join(settings.BASE_DIR, 'static', 'images', 'logos', 'investor_logo.png'),
        # Chemin depuis STATIC_ROOT si défini
        os.path.join(settings.STATIC_ROOT, 'images', 'logos', 'investor_logo.png') if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT else None,
        # Chemin depuis STATICFILES_DIRS si défini
    ]
    
    # Ajouter les chemins depuis STATICFILES_DIRS
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        for static_dir in settings.STATICFILES_DIRS:
            logo_paths.append(os.path.join(static_dir, 'images', 'logos', 'investor_logo.png'))
    
    # Chercher le logo dans tous les chemins possibles
    for logo_path in logo_paths:
        if logo_path and os.path.exists(logo_path):
            try:
                # Tenter de charger l'image avec gestion des proportions
                img = Image(logo_path)
                # Calculer les dimensions en conservant les proportions
                img_width, img_height = img.imageWidth, img.imageHeight
                aspect_ratio = img_width / img_height if img_height > 0 else 1
                
                # Définir des dimensions fixes adaptées pour l'en-tête
                max_width = 4 * cm
                max_height = 2.5 * cm
                
                # Calculer les dimensions en conservant les proportions
                if aspect_ratio > 1:
                    # Image large
                    display_width = min(max_width, max_height * aspect_ratio)
                    display_height = display_width / aspect_ratio
                else:
                    # Image haute
                    display_height = min(max_height, max_width / aspect_ratio)
                    display_width = display_height * aspect_ratio
                
                return Image(logo_path, width=display_width, height=display_height)
            except Exception as e:
                # Si erreur de chargement, continuer à chercher ou utiliser le fallback
                continue
    
    # Fallback : texte si le logo n'est pas trouvé
    return Paragraph(
        "<b>INVESTOR BANQUE</b><br/>Banque européenne",
        ParagraphStyle('LogoPlaceholder', 
            fontSize=12, 
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold',
            leading=14
        )
    )

def create_seal_placeholder():
    """Crée le cachet de la banque"""
    try:
        seal_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'seals', 'bank_seal.png')
        if os.path.exists(seal_path):
            return Image(seal_path, width=3*cm, height=3*cm)
    except:
        pass
    return Paragraph("", ParagraphStyle('SealPlaceholder'))

def create_manager_signature_placeholder():
    """Crée la signature du gestionnaire"""
    try:
        signature_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'signatures', 'manager_signature.png')
        if os.path.exists(signature_path):
            return Image(signature_path, width=4.5*cm, height=2.5*cm)
    except:
        pass
    
    return Paragraph(
        "M. Damien Boudraux<br/>Gestionnaire des Prêts<br/>Investor Banque",
        ParagraphStyle('SignaturePlaceholder', 
            fontSize=10, 
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2C3E50'),
            fontName='Helvetica-Bold',
            leading=12
        )
    )

def format_currency(amount):
    """Formate un montant en EUR avec format français (espaces pour milliers, virgule pour décimales)"""
    # Convertir en entier pour les milliers
    amount_str = f"{amount:,.2f}"
    # Remplacer la virgule par un espace temporaire, puis le point par une virgule, puis l'espace par un espace
    parts = amount_str.split('.')
    integer_part = parts[0].replace(',', ' ')
    decimal_part = parts[1] if len(parts) > 1 else '00'
    return f"{integer_part},{decimal_part} EUR"

def generate_loan_certificate(loan_request):
    """Génère une attestation de prêt professionnelle et élégante"""
    
    if loan_request.status != 'paye':
        raise ValueError("Le prêt doit être payé pour générer l'attestation")
    
    if not hasattr(loan_request.user, 'userprofile'):
        raise ValueError("Profil utilisateur manquant")
    
    profile = loan_request.user.userprofile
    if not profile.nom or not profile.prenom:
        raise ValueError("Nom et prénom requis dans le profil")
    
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm,
        title=f"Attestation de Prêt INV-{loan_request.id:06d}",
        author="Investor Banque",
        subject="Attestation de Prêt Bancaire"
    )
    
    styles = getSampleStyleSheet()
    
    # Styles professionnels avec typographie améliorée
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=12,
        spaceBefore=0,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold',
        leading=30,
        letterSpacing=1.2
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading1'],
        fontSize=13,
        spaceAfter=22,
        spaceBefore=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#34495E'),
        fontName='Helvetica',
        leading=16,
        letterSpacing=0.5
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=11,
        spaceAfter=14,
        spaceBefore=22,
        textColor=colors.HexColor('#2C3E50'),
        fontName='Helvetica-Bold',
        leftIndent=0,
        firstLineIndent=0,
        leading=14
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=14,  # Interligne 1.4 pour meilleure lisibilité
        textColor=colors.HexColor('#2C2C2C'),
        firstLineIndent=0.5*cm,  # Alinéa de première ligne
        leftIndent=0,
        rightIndent=0,
        wordWrap='LTR'
    )
    
    ref_style = ParagraphStyle(
        'ReferenceStyle',
        parent=normal_style,
        fontSize=11,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2C3E50'),
        backColor=colors.HexColor('#ECF0F1'),
        borderWidth=1,
        borderColor=colors.HexColor('#2C3E50'),
        borderPadding=8,
        spaceAfter=12
    )
    
    declaration_style = ParagraphStyle(
        'Declaration',
        parent=normal_style,
        fontSize=10,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=15,
        backColor=colors.HexColor('#F8F9FA'),
        borderWidth=1.5,
        borderColor=colors.HexColor('#2C3E50'),
        borderPadding=15,
        firstLineIndent=0.5*cm,
        leftIndent=0.3*cm,
        rightIndent=0.3*cm
    )
    
    story = []
    
    # === EN-TÊTE ===
    header_data = [
        [
            Paragraph(
                "<b>INVESTOR BANQUE</b><br/>Banque européenne<br/>Siège Social : Europe<br/>Tél/WhatsApp : +49 157 50098219<br/>Email : damien.boudraux17@outlook.fr<br/>Gestionnaire : Damien Boudraux",
                ParagraphStyle('BankInfo', fontSize=9, alignment=TA_LEFT, leading=11, textColor=colors.HexColor('#2C3E50'))
            ),
            create_logo_placeholder()
        ]
    ]
    
    header_table = Table(header_data, colWidths=[12*cm, 5*cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2C3E50')))
    story.append(Spacer(1, 12))
    
    # === TITRE ===
    story.append(Paragraph("ATTESTATION DE PRÊT BANCAIRE", title_style))
    story.append(Paragraph("CERTIFICAT D'OCTROI DE CRÉDIT", subtitle_style))
    
    # === RÉFÉRENCE ===
    ref_text = f"RÉFÉRENCE : INV-{loan_request.id:06d}"
    story.append(Paragraph(ref_text, ref_style))
    story.append(Spacer(1, 12))
    
    # === PRÉAMBULE ===
    preambule = "La présente attestation est délivrée à la demande de l'intéressé(e) pour servir et valoir ce que de droit devant toute autorité compétente. Nous, <b>INVESTOR BANQUE</b>, banque européenne, certifions par les présentes avoir accordé un prêt dans les conditions ci-après détaillées."
    preambule_style = ParagraphStyle(
        'PreambuleStyle',
        parent=normal_style,
        fontSize=10.5,
        spaceAfter=15,
        alignment=TA_JUSTIFY,
        leading=15,
        firstLineIndent=0.5*cm
    )
    story.append(Paragraph(preambule, preambule_style))
    story.append(Spacer(1, 12))
    
    # === IDENTIFICATION DU BÉNÉFICIAIRE ===
    story.append(Paragraph("<u>I. IDENTIFICATION DU BÉNÉFICIAIRE</u>", section_style))
    
    # Créer les cellules avec Paragraph pour éviter les balises HTML
    beneficiary_data = [
        [
            Paragraph('<b>Nom et Prénom</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(f"{profile.nom.upper()} {profile.prenom}", ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Date de naissance</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(profile.date_naissance.strftime('%d/%m/%Y') if profile.date_naissance else 'Non renseignée', ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Lieu de naissance</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(getattr(profile, 'lieu_naissance', 'Non renseigné') or 'Non renseigné', ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Profession</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(profile.profession or 'Non renseignée', ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Situation matrimoniale</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(profile.get_situation_matrimoniale_display() if profile.situation_matrimoniale else 'Non renseignée', ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Adresse complète</b>', ParagraphStyle('CellLabel', fontSize=10, fontName='Helvetica-Bold', textColor=colors.white)),
            Paragraph(profile.adresse or 'Non renseignée', ParagraphStyle('CellValue', fontSize=10, fontName='Helvetica'))
        ],
    ]
    
    beneficiary_table = Table(beneficiary_data, colWidths=[5*cm, 12*cm])
    beneficiary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2C3E50')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2C3E50')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(KeepTogether(beneficiary_table))
    story.append(Spacer(1, 12))
    
    # === CARACTÉRISTIQUES DU PRÊT ===
    story.append(Paragraph("<u>II. CARACTÉRISTIQUES DU PRÊT ACCORDÉ</u>", section_style))
    
    date_demande = loan_request.date_demande.strftime('%d/%m/%Y') if loan_request.date_demande else 'Non renseignée'
    date_validation = loan_request.date_validation.strftime('%d/%m/%Y') if loan_request.date_validation else (date_demande if loan_request.date_demande else 'Non renseignée')
    date_octroi = loan_request.date_paiement.strftime('%d/%m/%Y') if loan_request.date_paiement else (date_validation if loan_request.date_validation else date_demande)
    date_echeance = loan_request.date_fin_remboursement.strftime('%d/%m/%Y') if loan_request.date_fin_remboursement else 'À déterminer'
    
    duree_annees = loan_request.duree_remboursement_mois // 12
    duree_mois_restants = loan_request.duree_remboursement_mois % 12
    duree_text = f"{duree_annees} an(s)" + (f" et {duree_mois_restants} mois" if duree_mois_restants > 0 else "")
    
    montant_lettres = number_to_words(int(loan_request.montant))
    
    montant_formatted = format_currency(float(loan_request.montant))
    avance_formatted = format_currency(float(loan_request.montant_avance))
    
    # Créer les cellules avec Paragraph pour éviter les balises HTML
    loan_data = [
        [
            Paragraph('<b>Date de la demande</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(date_demande, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Date de validation</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(date_validation, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Date d\'octroi du prêt</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(date_octroi, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Montant du prêt accordé</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(f'<b>{montant_formatted}</b>', ParagraphStyle('CellValue2', fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#856404'), backColor=colors.HexColor('#FFF3CD')))
        ],
        [
            Paragraph('<b>Montant en lettres</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(f'<i>{montant_lettres} euros</i>', ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica-Oblique'))
        ],
        [
            Paragraph('<b>Montant de l\'apport (15%)</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(avance_formatted, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Durée de remboursement</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(f"{loan_request.duree_remboursement_mois} mois ({duree_text})", ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Date limite de remboursement</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(date_echeance, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Objet du financement</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(loan_request.motif[:150] + "..." if len(loan_request.motif) > 150 else loan_request.motif, ParagraphStyle('CellValue2', fontSize=10, fontName='Helvetica'))
        ],
        [
            Paragraph('<b>Clé de référence unique</b>', ParagraphStyle('CellLabel2', fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#2C3E50'))),
            Paragraph(f'<font face="Courier">{loan_request.payment_key or "Non générée"}</font>', ParagraphStyle('CellValue2', fontSize=10, fontName='Courier'))
        ],
    ]
    
    loan_table = Table(loan_data, colWidths=[5.5*cm, 11.5*cm])
    loan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#78909C')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (1, 3), (1, 3), colors.HexColor('#FFF3CD')),
    ]))
    
    story.append(KeepTogether(loan_table))
    story.append(Spacer(1, 12))
    
    # === CONDITIONS ===
    story.append(Paragraph("<u>III. CONDITIONS ET MODALITÉS DE REMBOURSEMENT</u>", section_style))
    
    conditions_text = f"""A. MODALITÉS DE REMBOURSEMENT :

• <b>Type de remboursement :</b> Annuités constantes (mensualités fixes)
  Les mensualités restent identiques tout au long du prêt, composées d'une part de capital croissante et d'une part d'intérêts décroissante, offrant une meilleure visibilité sur les paiements futurs.

• <b>Durée du prêt :</b> De 12 mois à 25 ans (300 mois maximum)
  La durée est adaptée selon le montant emprunté, votre capacité de remboursement et votre projet. Durée maximale autorisée : vingt-cinq (25) ans.

• <b>Fréquence des échéances :</b> Mensuelle
  Les remboursements s'effectuent mensuellement, généralement le même jour de chaque mois, convenu lors de la signature du contrat.

• <b>Calcul des mensualités :</b> Selon le taux d'intérêt applicable
  Les mensualités sont calculées selon un système d'amortissement progressif, garantissant une répartition équilibrée du capital et des intérêts sur toute la durée du prêt.

B. MODULATION DES ÉCHÉANCES :

• <b>Augmentation des mensualités :</b> Possibilité d'augmenter vos mensualités à tout moment
  Vous pouvez accélérer le remboursement en augmentant le montant de vos échéances, réduisant ainsi la durée totale du prêt et les intérêts payés.

• <b>Diminution des mensualités :</b> Réduction possible sous conditions
  En cas de difficultés temporaires, une demande de modulation à la baisse peut être étudiée, sous réserve de l'accord du gestionnaire et de la capacité de remboursement.

C. REMBOURSEMENT ANTICIPÉ :

• <b>Remboursement partiel anticipé :</b> Autorisé sans pénalité
  Vous pouvez rembourser partiellement votre prêt avant l'échéance prévue, sans frais supplémentaires, réduisant ainsi le capital restant dû et les intérêts futurs.

• <b>Remboursement total anticipé :</b> Autorisé sous conditions
  Le remboursement total anticipé est possible. Des indemnités de remboursement anticipé peuvent s'appliquer, plafonnées à un semestre d'intérêts sur le capital remboursé, sans dépasser 3% du capital restant dû.

• <b>Période de différé :</b> Possibilité de différer le remboursement du capital
  En début de prêt, une période de différé peut être accordée, avec paiement des seuls intérêts pendant une période déterminée, notamment pour les projets d'investissement.

D. MÉTHODE DE PAIEMENT :

• <b>Mode de paiement :</b> Paiements effectués auprès du gestionnaire de compte désigné
  Les remboursements s'effectuent exclusivement auprès de nos services agréés et habilités, par virement bancaire, prélèvement automatique ou remise de fonds.

• <b>Identification obligatoire :</b> Présentation systématique de la clé de référence unique
  Chaque transaction doit être identifiée avec votre clé de référence unique : <b>{loan_request.payment_key}</b>

• <b>Échéancier détaillé :</b> Disponible sur demande
  Un tableau d'amortissement complet, détaillant chaque échéance (capital, intérêts, capital restant dû), peut être fourni sur simple demande auprès de votre gestionnaire.

E. PÉNALITÉS ET RETARDS :

• <b>Retard de paiement :</b> Soumis aux pénalités prévues
  Tout retard de paiement sera soumis aux pénalités de retard prévues par nos conditions générales de crédit, conformément à la réglementation en vigueur.

• <b>Défaut de paiement :</b> Procédures de recouvrement
  En cas de défaut de paiement répété, des procédures de recouvrement peuvent être engagées, conformément aux dispositions légales et contractuelles.

F. ASSURANCE ET GARANTIES :

• <b>Assurance emprunteur :</b> Fortement recommandée
  Bien que facultative, l'assurance emprunteur est fortement recommandée pour couvrir les risques de décès, d'invalidité ou d'incapacité de travail, protégeant ainsi vos proches et votre projet.

• <b>Garanties :</b> Selon le montant et la nature du prêt
  Selon le montant emprunté et la nature du prêt, des garanties peuvent être exigées (hypothèques, cautions, nantissements), conformément aux pratiques bancaires.

G. CONTACT ET ASSISTANCE :

• <b>Gestionnaire responsable :</b> Damien Boudraux
• <b>Téléphone/WhatsApp :</b> +49 157 50098219
• <b>Email :</b> damien.boudraux17@outlook.fr
• <b>Horaires de service :</b> Lundi au Vendredi de 08h00 à 17h00

Pour toute question concernant votre remboursement, n'hésitez pas à contacter votre gestionnaire qui vous apportera toute l'assistance nécessaire."""
    
    story.append(Paragraph(conditions_text.replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 12))
    
    # === DÉCLARATION ===
    story.append(Paragraph("<u>IV. DÉCLARATION OFFICIELLE ET CERTIFICATION</u>", section_style))
    
    declaration_text = f"""Nous, <b>INVESTOR BANQUE</b>, banque européenne,
    
<b>CERTIFIONS ET ATTESTONS PAR LES PRÉSENTES QUE :</b>

Le prêt d'un montant de <b>{montant_formatted}</b> (en toutes lettres : <b>{montant_lettres} euros</b>) a été officiellement accordé, approuvé et débloqué au profit de <b>Monsieur/Madame {profile.nom.upper()} {profile.prenom}</b>, en date du <b>{date_octroi}</b>, conformément à nos procédures internes de crédit et aux réglementations en vigueur.

Cette attestation est délivrée pour servir et valoir ce que de droit devant toute autorité administrative, judiciaire, notariale ou tout organisme public ou privé qui en ferait la demande. Elle peut être utilisée comme justificatif officiel et authentique dans le cadre des démarches légitimes du bénéficiaire.

La présente attestation est établie en un exemplaire original et ne peut faire l'objet d'aucune reproduction sans l'autorisation expresse et écrite de notre direction générale.

<b>EN FOI DE QUOI</b>, nous avons établi la présente attestation."""
    
    story.append(Paragraph(declaration_text.replace('\n', '<br/>'), declaration_style))
    story.append(Spacer(1, 18))
    
    # === SIGNATURES ===
    lieu_date_text = f"Fait à Europe, le {datetime.now().strftime('%d %B %Y')}"
    lieu_date = Paragraph(f"<b>{lieu_date_text}</b>", ParagraphStyle('DateStyle', fontSize=11, fontName='Helvetica-Bold', alignment=TA_CENTER))
    
    signature_data = [
        [lieu_date, '', ''],
        ['', '', ''],
        [
            Paragraph('<b>LE BÉNÉFICIAIRE</b>', ParagraphStyle('SigTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#2C3E50'))),
            '',
            Paragraph('<b>LA BANQUE</b>', ParagraphStyle('SigTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#2C3E50')))
        ],
        ['', '', ''],
        ['', '', ''],
        [
            Paragraph(f'{profile.nom.upper()} {profile.prenom}', ParagraphStyle('SigName', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER)),
            '',
            Paragraph('INVESTOR BANQUE', ParagraphStyle('SigName', fontSize=10, fontName='Helvetica-Bold', alignment=TA_CENTER))
        ],
        ['', '', ''],
        ['', '', ''],
        ['', '', create_manager_signature_placeholder()],
        ['', '', Paragraph('Le Gestionnaire des Prêts', ParagraphStyle('SigFunction', fontSize=9, fontName='Helvetica', alignment=TA_CENTER))],
        ['', '', ''],
        [Paragraph('(Signature précédée de la mention<br/>"Lu et approuvé")', ParagraphStyle('SigNote', fontSize=8, fontName='Helvetica-Oblique', alignment=TA_CENTER, textColor=colors.HexColor('#6c757d'))), '', ''],
        ['', '', Paragraph('+ Cachet officiel', ParagraphStyle('SigSeal', fontSize=8, fontName='Helvetica-Oblique', alignment=TA_CENTER, textColor=colors.HexColor('#6c757d')))],
    ]
    
    signature_table = Table(signature_data, colWidths=[6*cm, 5*cm, 6*cm])
    signature_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (2, 0)),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('VALIGN', (0, 0), (2, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (2, 0), 8),
        ('SPAN', (0, 11), (1, 11)),
        ('ALIGN', (0, 11), (0, 11), 'CENTER'),
        ('ALIGN', (2, 11), (2, 11), 'CENTER'),
        ('VALIGN', (0, 2), (0, 2), 'MIDDLE'),
        ('VALIGN', (2, 2), (2, 2), 'MIDDLE'),
        ('VALIGN', (0, 5), (0, 5), 'MIDDLE'),
        ('VALIGN', (2, 5), (2, 5), 'MIDDLE'),
        ('VALIGN', (2, 8), (2, 8), 'MIDDLE'),
        ('VALIGN', (2, 9), (2, 9), 'MIDDLE'),
        ('TOPPADDING', (0, 5), (0, 5), 18),
        ('BOTTOMPADDING', (0, 5), (0, 5), 3),
        ('TOPPADDING', (2, 8), (2, 8), 8),
        ('BOTTOMPADDING', (2, 8), (2, 8), 3),
        ('LINEBELOW', (0, 6), (0, 6), 1, colors.HexColor('#2C3E50')),
        ('LINEBELOW', (2, 7), (2, 7), 1, colors.HexColor('#2C3E50')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    
    story.append(KeepTogether(signature_table))
    story.append(Spacer(1, 12))
    
    # === PIED DE PAGE AVEC LOGO ===
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#78909C'), spaceBefore=8, spaceAfter=8))
    
    # Créer un pied de page avec logo et informations
    footer_logo = create_logo_placeholder()
    footer_logo_small = None
    
    # Réduire la taille du logo pour le pied de page
    try:
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logos', 'investor_logo.png'),
        ]
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            for static_dir in settings.STATICFILES_DIRS:
                logo_paths.append(os.path.join(static_dir, 'images', 'logos', 'investor_logo.png'))
        
        for logo_path in logo_paths:
            if logo_path and os.path.exists(logo_path):
                try:
                    img = Image(logo_path)
                    img_width, img_height = img.imageWidth, img.imageHeight
                    aspect_ratio = img_width / img_height if img_height > 0 else 1
                    
                    # Dimensions pour le pied de page (plus petit)
                    max_width = 2 * cm
                    max_height = 1 * cm
                    
                    # Calculer les dimensions en conservant les proportions
                    if aspect_ratio > 1:
                        # Image large
                        display_width = min(max_width, max_height * aspect_ratio)
                        display_height = display_width / aspect_ratio
                    else:
                        # Image haute
                        display_height = min(max_height, max_width / aspect_ratio)
                        display_width = display_height * aspect_ratio
                    
                    footer_logo_small = Image(logo_path, width=display_width, height=display_height)
                    break
                except:
                    continue
    except:
        pass
    
    footer_data = [
        [
            footer_logo_small if footer_logo_small else Paragraph("", ParagraphStyle('Empty')),
            Paragraph(
                f"<b>INVESTOR BANQUE</b><br/>"
                f"<i>Banque européenne</i><br/>"
                f"<font size='7'>Document authentique généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</font><br/>"
                f"<font size='7'>Référence : INV-{loan_request.id:06d} | Empreinte : {abs(hash(f'{loan_request.id}{loan_request.payment_key}'))}</font><br/>"
                f"<font size='7'>Vérification : damien.boudraux17@outlook.fr - +49 157 50098219</font>",
                ParagraphStyle('FooterInfo', 
                    fontSize=7, 
                    textColor=colors.HexColor('#6c757d'),
                    alignment=TA_CENTER,
                    fontName='Helvetica',
                    leading=9
                )
            )
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[3*cm, 14*cm])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(footer_table)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def number_to_words(number):
    """Convertit un nombre en lettres françaises"""
    if number == 0:
        return "zéro"
    
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
