from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
from models import File
from django.http import JsonResponse

def televersement(request):
    if request.method == 'POST':
        file = request.Files['document']
        password = request.POST["password"].encode() 
        key = Fernet.generate_key() #génére une clé de chiffrement unique
        cryptogram = Fernet(key) # crée un objet fernet avec la clé généré pour utiliser les fonctions de chiffrement et dechiffrement
        encrypted_key = cryptogram.encrypt(password)  #chiffre le mot de passe 
        #Nouvelle instance du modèle File pour enregistré le fichier téléchargé et sa clé chiffrée
        new_file = File(file=file, encrypted_key=encrypted_key.decode())
        new_file.save()

        # generation du lien unique 
        file_url = f"{request.build_absolute_url('/')}{new_file.id}/"
        return JsonResponse({"l'url du fichier est : ": file_url})
    return render(request, 'upload.html')





