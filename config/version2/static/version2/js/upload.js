
function generateUUID() {
    return crypto.randomUUID(); 
}


function getFileExtension(filename) {
    return filename.substring(filename.lastIndexOf('.')) || '';
}

const generateKey = () => {
    return CryptoJS.lib.WordArray.random(32).toString(CryptoJS.enc.Hex);
};

const encryptPassword = (password, key) => {
    const encrypted = CryptoJS.AES.encrypt(password, key).toString();
    return encrypted;
};

function handleFormSubmission(event) {
    event.preventDefault(); 

    const form = event.target;
    const fileInput = form.querySelector('input[type="file"]');

    const file = fileInput.files[0];

    const uuid = generateUUID();
    const extension = getFileExtension(file.name);
    const newFileName = uuid + extension;
    console.log(newFileName);

    const password = form.querySelector('#password').value;
    const encode_password = CryptoJS.enc.Utf8.parse(password);
    console.log(encode_password);

    const key = generateKey();
    const encryptedPassword = encryptPassword(encode_password,key);
    const keyBase64 = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Hex.parse(key));

    const metadata = {
        key: keyBase64,
        encrypted_password: encryptedPassword,
        file_name: newFileName,
    };

    const formData = new FormData(form);
    formData.set("document", file, newFileName); 
    formData.append("metadata", JSON.stringify(metadata));

    const metadataInput = document.createElement('input');
    metadataInput.type = 'hidden';
    metadataInput.name = 'metadata';
    metadataInput.value = JSON.stringify(metadata);
    form.appendChild(metadataInput);

    form.submit();
}

// Attach event listener to the form
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload_form");
    if (form) {
        form.addEventListener("submit", handleFormSubmission);
    }
});
