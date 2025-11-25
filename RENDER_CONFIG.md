# Configuration Render - Investor Banque

## 📋 Champs à remplir dans Render

### 1. **Name**
```
investor-banque-loans
```

### 2. **Branch**
```
main
```
(✓ Déjà rempli)

### 3. **Region**
```
Oregon (US West)
```
(✓ Déjà sélectionné - OK pour commencer)

### 4. **Root Directory**
```
(Laisser vide)
```

### 5. **Build Command**
```
pip install -r requirements.txt
```
(✓ Déjà rempli - OK)

### 6. **Start Command**
```
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ecobank_project.wsgi:application
```
⚠️ **IMPORTANT** : Remplacez `gunicorn app:app` par la commande ci-dessus

### 7. **Instance Type**
```
Free
```
(✓ Déjà sélectionné - OK pour commencer)

### 8. **Environment Variables**
Cliquez sur "Add Environment Variable" et ajoutez ces variables :

#### Variable 1 :
- **KEY** : `RENDER`
- **VALUE** : `1`

#### Variable 2 :
- **KEY** : `SECRET_KEY`
- **VALUE** : `op&^qy99va26u2*zl+e1)k0+v*_z!f8qac53wmq=66jec)wd1a`

#### Variable 3 :
- **KEY** : `DEBUG`
- **VALUE** : `False`

#### Variable 4 :
- **KEY** : `DATABASE_URL`
- **VALUE** : *(À ajouter après création de PostgreSQL - voir ci-dessous)*

#### Variable 5 :
- **KEY** : `ALLOWED_HOSTS`
- **VALUE** : `investor-banque-loans.onrender.com`

---

## 🗄️ Base de données PostgreSQL

**AVANT de créer le Web Service**, créez d'abord une base PostgreSQL :

1. Dans Render Dashboard → "New +" → "PostgreSQL"
2. Configurer :
   - **Name** : `investor-banque-db`
   - **Database** : `investor_banque`
   - **Region** : `Oregon (US West)` (même que le Web Service)
   - **Plan** : `Free`
3. Cliquez sur "Create Database"
4. **Copiez la `DATABASE_URL`** qui s'affiche
5. Ajoutez-la dans les Environment Variables du Web Service (Variable 4 ci-dessus)

---

## ✅ Après le déploiement

1. Attendez que le déploiement se termine (5-10 minutes)
2. Votre site sera accessible à : `https://investor-banque-loans.onrender.com`
3. Créez le superutilisateur via le Shell Render :
   - Onglet "Shell" dans votre service
   - Commande : `python manage.py createsuperuser`
   - Username : `admin5`
   - Password : `01254533`

---

## 🔧 Dépannage

Si le déploiement échoue :
1. Vérifiez les logs dans l'onglet "Logs"
2. Vérifiez que toutes les variables d'environnement sont correctes
3. Vérifiez que la DATABASE_URL est bien configurée

