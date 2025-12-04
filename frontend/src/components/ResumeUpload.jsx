import { useState } from 'react';
import axios from 'axios';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [preview, setPreview] = useState("");

const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setStatus("Uploading & Parsing... (This may take 10s)");
      
      // FIX: Remove the manual 'headers' config. 
      // Axios + Browser will handle multipart/form-data automatically.
      const res = await axios.post("http://localhost:8000/resume/upload", formData);
      
      setStatus("Success!");
      setPreview(res.data.preview); 
    } catch (err) {
      console.error(err);
      setStatus("Error uploading resume.");
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px' }}>
      <h2>Step 1: Upload Master Resume</h2>
      <input 
        type="file" 
        accept=".pdf"
        onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)} 
      />
      <button onClick={handleUpload} style={{ marginLeft: '10px' }}>
        Upload
      </button>
      
      <p><strong>Status:</strong> {status}</p>
      {preview && <div style={{ background: '#f0f0f0', padding: '10px' }}>{preview}</div>}
    </div>
  );
};

export default ResumeUpload;