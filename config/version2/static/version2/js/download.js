const decryptPassword = (encrypted_password, key) => {
    const decrypted = CryptoJS.AES.decrypt(encrypted_password, key);
    return decrypted.toString(CryptoJS.enc.Utf8);
};



function handleFormSubmission(event) {
    event.preventDefault(); 
    let url = window.location.href;
    const form = event.target;

    let metadata_str = url.split('/download/')[1].replace(/\/$/, '');
    let decodedStr = atob(metadata_str); 
    let metadataArray = decodedStr.split('|');
    let keyBase64 = metadataArray[0];
    let encryptedPassword = metadataArray[1];
    let fileName = metadataArray[2];
    console.log(fileName);
   

    const password = form.querySelector('#password').value;

    const wordArray = CryptoJS.enc.Base64.parse(keyBase64);
    const key = CryptoJS.enc.Hex.stringify(wordArray);
 

    const decryptedPassword = decryptPassword(encryptedPassword,key);


    if(decryptedPassword == password) {
        const fileInput = document.createElement('input');
        fileInput.type = 'hidden';
        fileInput.name = 'file_name';
        fileInput.value = fileName;
        form.appendChild(fileInput);

        form.submit();
    } else {
        alert('password error');
    }

}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("download_form");
    if (form) {
        form.addEventListener("submit", handleFormSubmission);
    }
});