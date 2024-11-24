import os
import uuid
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from cryptography.fernet import Fernet
from .models import File

from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def upload(request):
    if request.method == 'POST':
        file = request.FILES['document']
        password = request.POST["password"].encode() 
        key = Fernet.generate_key() #génére une clé de chiffrement unique
        cryptogram = Fernet(key) # crée un objet fernet avec la clé généré pour utiliser les fonctions de chiffrement et dechiffrement
        encrypted_password = cryptogram.encrypt(password)  #chiffre le mot de passe 
        
        # Créer un nom unique pour le fichier
        file_name = str(uuid.uuid4()) + os.path.splitext(file.name)[-1]
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
        
        # Enregistrer le fichier sur le système de fichiers
        fs = FileSystemStorage()
        fs.save(file_path, file)

        # Sauvegarder le mot de passe chiffré dans un fichier
        encrypted_password_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name + '.key')
        with open(encrypted_password_path, 'wb') as key_file:
            key_file.write(encrypted_password)

        # Générer un lien unique pour accéder au fichier
        file_url = request.build_absolute_uri('/media/uploads/' + file_name)

        # #Nouvelle instance du modèle File pour enregistré le fichier téléchargé et sa clé chiffrée
        # new_file = File(file=file, encrypted_password=encrypted_password.decode())
        # new_file.save()

        # generation du lien unique 
        # file_url = f"{request.build_absolute_url('/')}{new_file.id}/"

        return render(request, 'download.html', {'file_url': file_url})
    return render(request, 'upload.html')

def telechargement(request):
    if request.method == 'POST':
        file_url = request.POST.get("file_url")  # Récupérer le lien du fichier
        password = request.POST.get("password").encode()  # Récupérer le mot de passe

        # Extraire le nom du fichier depuis l'URL
        file_name = file_url.split("/")[-1]  
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)

        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            return HttpResponse("Fichier non trouvé", status=404)

        # Vérifier si le fichier clé existe
        encrypted_password_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name + '.key')
        
        if not os.path.exists(encrypted_password_path):
            return HttpResponse("Clé de chiffrement manquante", status=404)

        # Lire la clé brute depuis le fichier (clé Fernet brute)
        with open(encrypted_password_path, 'rb') as key_file:
            key = key_file.read()  # Clé Fernet brute
        print('here')
        print(key)
        print(len(key))
        cryptogram = Fernet(key)  # Utiliser cette clé brute pour déchiffrer le mot de passe

        # Déchiffrer le mot de passe
        try:
            decrypted_password = cryptogram.decrypt(encrypted_password).decode()
        except Exception as e:
            return HttpResponse(f"Erreur de déchiffrement: {str(e)}", status=400)

        # Comparer les mots de passe
        if decrypted_password == password.decode():
            # Le mot de passe est valide, permettre le téléchargement du fichier
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="application/octet-stream")
                response['Content-Disposition'] = f'attachment; filename="{file_name}"'
                return response
        else:
            return HttpResponse("Mot de passe incorrect", status=400)

    # Afficher la page de téléchargement
    return render(request, 'download.html', {'file_url': request.GET.get('file_url')})
