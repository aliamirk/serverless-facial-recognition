import './App.css';
import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

function App() {
  const [image, setImage] = useState(null);
  const [uploadMessage, setUploadMessage] = useState('Please upload an image to authenticate');
  const [imgPreviewUrl, setImgPreviewUrl] = useState(null);
  const [isAuth, setAuth] = useState(false);

  async function sendImage(e) {
    e.preventDefault();

    if (!image) {
      setUploadMessage('Please select an image before submitting.');
      return;
    }

    const visitorImageName = uuidv4();
    console.log(visitorImageName);

    try {
      // Upload image to backend (API Gateway / S3 via Lambda)
      await fetch(`https://<your-api-id>.execute-api.us-east-1.amazonaws.com/v1/visitor-images-0ef12/${visitorImageName}.jpeg`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'image/jpeg'
        },
        body: image
      });

      // Wait 2 seconds before calling authenticate
      // await new Promise(resolve => setTimeout(resolve, 1500)); // 2000 ms = 2 sec
      // Authenticate the image
      const response = await authenticate(visitorImageName);

      if (response?.Message === 'Success') {
        console.log(response);
        setUploadMessage(`Hi ${response.firstName} ${response.lastName}, welcome to work, hope you have a productive day today!`);
        setAuth(true);
      } else {
        setUploadMessage('Authentication Failed: This person is not an employee.');
        setAuth(false);
      }
    } catch (e) {
      console.error(e);
      setUploadMessage('There was an error during the authentication process. Please try again.');
      setAuth(false);
    }
  }

  async function authenticate(visitorImageName) {
    const requestURL = `https://<your-api-id>.execute-api.us-east-1.amazonaws.com/v1/employee?` +
      new URLSearchParams({ objectKey: `${visitorImageName}.jpeg` }).toString();

    try {
      const res = await fetch(requestURL, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });

      return await res.json();
    } catch (e) {
      console.error('Error in authentication request:', e);
      return null;
    }
  }

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImgPreviewUrl(URL.createObjectURL(file));
    }
  }

  return (
    <div className="App">
      <h2>Facial Recognition System</h2>
      <form onSubmit={sendImage}>
        <input
          type="file"
          name="image"
          accept="image/jpeg,image/png"
          onChange={handleFileChange}
        />
        <button type="submit">Authenticate</button>
      </form>

      <div className={isAuth ? 'success' : 'failure'}>
        {uploadMessage}
      </div>

      {imgPreviewUrl && (
        <img src={imgPreviewUrl} alt="Visitor Preview" height={250} width={250} />
      )}
    </div>
  );
}

export default App;
