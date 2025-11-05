#!/usr/bin/env python
"""
Test de mise à jour des couleurs ECOBANK
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecobank_project.settings')
django.setup()

def test_colors_update():
    """Test de mise à jour des couleurs"""
    print("🎨 TEST DE MISE À JOUR DES COULEURS ECOBANK")
    print("=" * 60)
    
    # Vérifier le fichier CSS
    css_path = 'static/css/style.css'
    if os.path.exists(css_path):
        print(f"✅ Fichier CSS trouvé: {css_path}")
        
        with open(css_path, 'r') as f:
            content = f.read()
            
        if '#00A651' in content:
            print("✅ Couleurs ECOBANK mises à jour dans CSS")
        else:
            print("❌ Couleurs ECOBANK non trouvées dans CSS")
    else:
        print(f"❌ Fichier CSS non trouvé: {css_path}")
    
    # Vérifier le template base
    template_path = 'templates/base.html'
    if os.path.exists(template_path):
        print(f"✅ Template base trouvé: {template_path}")
        
        with open(template_path, 'r') as f:
            content = f.read()
            
        if '#00A651' in content:
            print("✅ Couleurs ECOBANK mises à jour dans template")
        else:
            print("❌ Couleurs ECOBANK non trouvées dans template")
            
        if 'linear-gradient' in content:
            print("✅ Dégradés ECOBANK trouvés dans template")
        else:
            print("❌ Dégradés ECOBANK non trouvés dans template")
    else:
        print(f"❌ Template base non trouvé: {template_path}")
    
    print("\n" + "=" * 60)
    print("🎯 RÉSULTAT:")
    print("Les couleurs ECOBANK devraient maintenant être visibles sur le site")
    print("URL: http://localhost:9000/")
    print("Videz le cache de votre navigateur (Ctrl+F5 ou Cmd+Shift+R)")
    print("=" * 60)

if __name__ == "__main__":
    test_colors_update()
