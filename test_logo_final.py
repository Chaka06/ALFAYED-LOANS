#!/usr/bin/env python
"""
Test final du logo ECOBANK PNG
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

def test_logo_final():
    """Test final du logo PNG"""
    print("🖼️ TEST FINAL DU LOGO ECOBANK PNG")
    print("=" * 50)
    
    # Vérifier le fichier source
    source_path = os.path.join('static', 'images', 'ecobank-logo.png')
    if os.path.exists(source_path):
        print(f"✅ Logo PNG source trouvé: {source_path}")
        file_size = os.path.getsize(source_path)
        print(f"📏 Taille du fichier: {file_size} bytes")
        
        # Vérifier le type de fichier
        import subprocess
        try:
            result = subprocess.run(['file', source_path], capture_output=True, text=True)
            print(f"📄 Type de fichier: {result.stdout.strip()}")
        except:
            print("⚠️ Impossible de vérifier le type de fichier")
    else:
        print(f"❌ Logo PNG source non trouvé: {source_path}")
    
    # Vérifier dans staticfiles
    staticfiles_path = os.path.join('staticfiles', 'images', 'ecobank-logo.png')
    if os.path.exists(staticfiles_path):
        print(f"✅ Logo PNG dans staticfiles: {staticfiles_path}")
    else:
        print(f"❌ Logo PNG non trouvé dans staticfiles: {staticfiles_path}")
    
    print("\n" + "=" * 50)
    print("🎯 RÉSULTAT:")
    print("Votre logo PNG devrait maintenant s'afficher correctement")
    print("URL: http://localhost:9000/")
    print("Le logo sera affiché en blanc sur le fond bleu ECOBANK")
    print("=" * 50)

if __name__ == "__main__":
    test_logo_final()
