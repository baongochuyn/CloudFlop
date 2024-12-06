from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from .models import File
from django.conf import settings
import json
import base64
import os
import datetime
from django.http import HttpResponse, HttpResponseForbidden

def upload(request):
    option_once = False
    if request.method == 'POST':
        file = request.FILES['document']
        expiration_date = request.POST["expiration_date"]
        receiver_email = request.POST["receiver_email"]
        metadata = request.POST["metadata"]

        if 'unique_usage' in request.POST:
            option_once = True

        if metadata:
            metadata = json.loads(metadata)
            binary_data = file.read()

            new_file = File(
                file=binary_data,
                file_name=metadata['file_name'],
                expiration_date=expiration_date,
                option_once=option_once
            )
            new_file.save()
            
            # Encrypt metadata and encode for the URL
            metadata_str = f"{metadata['key']}|{metadata['encrypted_password']}|{metadata['file_name']}"

            encrypted_metadata = base64.urlsafe_b64encode(metadata_str.encode('utf-8')).decode('utf-8')

            # Generate the unique encrypted URL
            file_url = request.build_absolute_uri(f'/version2/download/{encrypted_metadata}/')

            subject = 'Lien du fichier partagé'
            message = 'Voici le lien du fichier : '+ file_url
            from_email = settings.DEFAULT_FROM_EMAIL 
            recipient_list = [receiver_email] 

            send_mail(subject, message, from_email, recipient_list)
        
            messages.success(request,"Lien envoyé avec succès")
    
    return render(request, 'upload1.html')

def download(request, encrypted_metadata):
    # Get the password from the user
    if request.method == 'POST':
        file_name = request.POST["file_name"]
        
        try:
            object_file = File.objects.get(file_name=file_name)

            if(((object_file.option_once == False) and  (object_file.expiration_date > datetime.date.today())) or 
               ((object_file.option_once == True) and (object_file.downloaded == False) and (object_file.expiration_date > datetime.date.today()))):
                object_file.downloaded = True
                object_file.save()
            
                response = HttpResponse(object_file.file, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
                return response
            else:
                messages.error(request,"Le fichier ne peut plus être téléchargé")
        except File.DoesNotExist:
            messages.error(request,"Fichier introuvable")
    
    return render(request, 'download1.html')
