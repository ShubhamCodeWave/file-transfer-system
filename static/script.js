const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressDetails = document.getElementById('progressDetails');
const usernameInput = document.getElementById('username');

// Create message container for announcements
const statusBox = document.createElement('div');
statusBox.setAttribute('aria-live', 'assertive');
statusBox.className = 'alert alert-success visually-hidden mt-4';
statusBox.setAttribute('role', 'alert');
document.querySelector('main').appendChild(statusBox);

function announceStatus(message, isSuccess = false) {
  progressContainer.setAttribute('aria-live', 'polite');
  progressDetails.textContent = message;
  if (isSuccess) {
    statusBox.classList.remove('visually-hidden');
    statusBox.textContent = message;

    uploadForm.classList.add('visually-hidden');
    setTimeout(() => {
      statusBox.classList.add('visually-hidden');
      uploadForm.classList.remove('visually-hidden');
      uploadForm.reset();
      resetProgress();
      usernameInput.focus();
      checkFormState();
    }, 5000);
  }
}

function resetProgress() {
  progressBar.style.width = '0%';
  progressBar.setAttribute('aria-valuenow', 0);
  progressBar.textContent = '0%';
  progressDetails.textContent = '';
  submitBtn.disabled = true;
}

function checkFormState() {
  const nameValid = usernameInput.value.trim().length > 0;
  const fileValid = fileInput.files.length === 1;
  submitBtn.disabled = !(nameValid && fileValid);
}

usernameInput.addEventListener('input', checkFormState);
fileInput.addEventListener('change', checkFormState);

uploadForm.addEventListener('submit', e => {
  e.preventDefault();

  const username = usernameInput.value.trim();
  const file = fileInput.files[0];

  if (!username || !file) {
    announceStatus('Full name and one file are required.');
    return;
  }

  const formData = new FormData();
  formData.append('username', username);
  formData.append('file', file);

  progressContainer.classList.remove('visually-hidden');
  resetProgress();
  announceStatus('Starting upload...');

  submitBtn.disabled = true;
  usernameInput.disabled = true;
  fileInput.disabled = true;

  const xhr = new XMLHttpRequest();
  const startTime = Date.now();

  xhr.upload.addEventListener('progress', e => {
    if (e.lengthComputable) {
      const percent = (e.loaded / e.total) * 100;
      const elapsed = (Date.now() - startTime) / 1000;
      const speed = (e.loaded / 1024 / 1024) / elapsed;
      const mbLoaded = (e.loaded / 1024 / 1024).toFixed(2);
      const mbTotal = (e.total / 1024 / 1024).toFixed(2);

      progressBar.style.width = ${percent.toFixed(2)}%;
      progressBar.setAttribute('aria-valuenow', percent.toFixed(0));
      progressBar.textContent = ${percent.toFixed(0)}%;
      progressDetails.textContent = Uploaded ${mbLoaded} MB of ${mbTotal} MB at ${speed.toFixed(2)} MB/s.;
    }
  });

  xhr.upload.addEventListener('load', () => {
    announceStatus('Upload complete. Waiting for server...');
  });

  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4) {
      usernameInput.disabled = false;
      fileInput.disabled = false;

      if (xhr.status === 200) {
        const resp = JSON.parse(xhr.responseText);
        if (resp.status === 'success') {
          const filename = resp.message.match(/"([^"]+)"/)?.[1] || 'your file';
          announceStatus(
            ${filename} uploaded successfully. Note: All fields have been reset. You can now send another file.,
            true
          );
        } else {
          announceStatus('Upload failed: ' + resp.message);
        }
      } else {
        announceStatus('An unexpected error occurred during upload.');
      }
    }
  };

  xhr.open('POST', '/upload');
  xhr.send(formData);
});

// Initialize
uploadForm.reset();
resetProgress();