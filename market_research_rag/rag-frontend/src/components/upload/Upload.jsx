import { useState } from "react";
import { uploadDocument } from "../../api/api"; 
import "./Upload.css";

export default function UploadBox() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return setStatus("Please select a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await uploadDocument(formData);
      setStatus("Upload successful!");
    } catch (err) {
      setStatus("Upload failed");
    }
  };

  return (
    <div className="upload-box">
      <h2>Upload Document</h2>
      <form onSubmit={handleUpload}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit">Upload</button>
      </form>
      {status && <p>{status}</p>}
    </div>
  );
}
