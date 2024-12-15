import os
import uuid
import base64
from django.shortcuts import render
from django.http import HttpResponse
from cryptography.fernet import Fernet
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib import messages
import hashlib


def generate_fernet_key(password: bytes, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password,
        salt, 
        100000
    )
    
    return base64.urlsafe_b64encode(key[:32]) 


def upload(request):
    if request.method == 'POST':
        file = request.FILES['document']
        password = request.POST["password"].encode()  # Encode the password
        
        # Generate an encryption key
        salt = os.urandom(16) 
        key = generate_fernet_key(password, salt)
        cryptogram = Fernet(key)

        file_data = file.read()
        encrypted_data = cryptogram.encrypt(file_data)


        file_name = f"{uuid.uuid4()}{os.path.splitext(file.name)[-1]}"

        file_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(file_dir, exist_ok=True) 

        file_path = os.path.join(file_dir, file_name)
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        # Save the encrypted password and key to a metadata dictionary
        metadata_id = get_random_string(32)

        metadata_dir = os.path.join(settings.MEDIA_ROOT, 'metadata')
        os.makedirs(metadata_dir, exist_ok=True)

        metadata_path = os.path.join(metadata_dir, f"{metadata_id}.meta")
        with open(metadata_path, 'w') as meta_file:
            meta_file.write(f"{base64.urlsafe_b64encode(salt).decode()}|{file_name}")

      
        file_url = request.build_absolute_uri(f'/version1/download/{metadata_id}/')

        return render(request, 'upload.html', {'file_url': file_url})
    
    return render(request, 'upload.html')

def download(request, metadata_id):
    try:
        metadata_path = os.path.join(settings.MEDIA_ROOT, 'metadata', f"{metadata_id}.meta")
        if not os.path.exists(metadata_path):
            messages.error(request, "Lien invalide")
            return render(request, 'download.html')

        with open(metadata_path, 'r') as meta_file:
            metadata = meta_file.read()
        
        salt_b64, file_name = metadata.split('|')
        salt = base64.urlsafe_b64decode(salt_b64)

        if request.method == 'POST':
            password = request.POST["password"].encode()
            #pprint.pprint(password)
            
            key = generate_fernet_key(password, salt)
            
            cryptogram = Fernet(key)
            #pprint.pprint('la')

            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
            if not os.path.exists(file_path):
                messages.error(request, "Fichier non trouvé")
                return render(request, 'download.html')

            with open(file_path, 'rb') as file:
                encrypted_data = file.read()
                try:
                    decrypted_data = cryptogram.decrypt(encrypted_data)
                except Exception:
                    messages.error(request, "Mot de passe invalide")
                    return render(request, 'download.html')

            response = HttpResponse(decrypted_data, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
            return response

        return render(request, 'download.html')

    except Exception as e:
        messages.error(request, "Une erreur s'est produite.")
        return render(request, 'download.html')
