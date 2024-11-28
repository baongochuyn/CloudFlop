import os
import uuid
import base64
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from cryptography.fernet import Fernet

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import pprint

def upload(request):
    if request.method == 'POST':
        file = request.FILES['document']
        password = request.POST["password"].encode()  # Encode the password
        
        # Generate an encryption key
        key = Fernet.generate_key()  # Unique encryption key
        cryptogram = Fernet(key)  # Fernet object for encryption and decryption
        encrypted_password = cryptogram.encrypt(password)  # Encrypt the password
        
        # Create a unique file name
        file_name = str(uuid.uuid4()) + os.path.splitext(file.name)[-1]
        
        # Save the file to the filesystem
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        fs.save(file_name, file)
        
        # Save the encrypted password and key to a metadata dictionary
        metadata = {
            "key": base64.urlsafe_b64encode(key).decode('utf-8'),  # Encode key for safe URL transmission
            "encrypted_password": encrypted_password.decode('utf-8'),  # Decode for safe storage
            "file_name": file_name
        }
        
        # Encrypt metadata and encode for the URL
        metadata_str = f"{metadata['key']}|{metadata['encrypted_password']}|{metadata['file_name']}"
        encrypted_metadata = base64.urlsafe_b64encode(metadata_str.encode('utf-8')).decode('utf-8')
        
        # Generate the unique encrypted URL
        file_url = request.build_absolute_uri(f'/download/version1/{encrypted_metadata}/')
        
        return render(request, 'upload.html', {'file_url': file_url})
    
    return render(request, 'upload.html')

def download(request, encrypted_metadata):
    try:
        # Decode and split metadata
        metadata_str = base64.urlsafe_b64decode(encrypted_metadata).decode('utf-8')
        key, encrypted_password, file_name = metadata_str.split('|')
        pprint.pprint('ok')
        pprint.pprint(encrypted_password)
        pprint.pprint(file_name)
        # Get the password from the user
        if request.method == 'POST':
            password = request.POST["password"].encode()
            pprint.pprint(key)
            pprint.pprint( Fernet(base64.urlsafe_b64decode(key)))
            # Decrypt the encrypted password using the key
            cryptogram = Fernet(base64.urlsafe_b64decode(key))
            decrypted_password = cryptogram.decrypt(encrypted_password.encode())
            pprint.pprint('ici')
            pprint.pprint(encrypted_password.encode())
            
            # Check if the passwords match
            if decrypted_password != password:
                messages.error(request,"Invalid password")
                return render(request, 'download.html')
            
            # Serve the file for download
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file_name)
            if not os.path.exists(file_path):
                messages.error(request,"File not found.")
                return render(request, 'download.html')
            
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
                return response
        
        return render(request, 'download.html')
    
    except Exception as e:
        messages.error(request,"Error processing your request.")
        return render(request, 'download.html')
