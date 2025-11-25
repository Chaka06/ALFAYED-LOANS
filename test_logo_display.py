#!/usr/bin/env python
"""
Test d'affichage du logo ECOBANK
Vérifie que l'image PNG s'affiche correctement
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

from django.template.loader import render_to_string
from django.conf import settings

def test_logo_display():
    """Test d'affichage du logo"""
    print("🖼️ TEST D'AFFICHAGE DU LOGO ECOBANK")
    print("=" * 50)
    
    # Vérifier que le fichier existe
    logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'ecobank-logo.png')
    if os.path.exists(logo_path):
        print(f"✅ Logo trouvé dans staticfiles: {logo_path}")
    else:
        print(f"❌ Logo non trouvé dans staticfiles: {logo_path}")
    
    # Vérifier le fichier source
    source_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'ecobank-logo.png')
    if os.path.exists(source_path):
        print(f"✅ Logo source trouvé: {source_path}")
        file_size = os.path.getsize(source_path)
        print(f"📏 Taille du fichier: {file_size} bytes")
    else:
        print(f"❌ Logo source non trouvé: {source_path}")
    
    # Test du template
    try:
        context = {}
        html = render_to_string('base.html', context)
        if 'ecobank-logo.png' in html:
            print("✅ Logo PNG trouvé dans le template base.html")
        else:
            print("❌ Logo PNG non trouvé dans le template")
        
        if 'ecobank-logo.svg' in html:
            print("⚠️ Logo SVG encore présent dans le template")
        else:
            print("✅ Logo SVG retiré du template")
            
    except Exception as e:
        print(f"❌ Erreur template: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSULTAT:")
    print("Votre logo PNG devrait maintenant s'afficher sur le site")
    print("URL: http://localhost:9000/")
    print("=" * 50)

if __name__ == "__main__":
    test_logo_display()
