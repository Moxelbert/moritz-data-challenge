import React, { useState } from "react";

const UploadJson = () => {
  const [file, setFile] = useState(null);
  const [statusMessage, setStatusMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setStatusMessage("Please select a JSON file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload-json", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`,  // Assuming token is stored in localStorage
        },
        body: formData,
      });
      if (response.ok) {
        setStatusMessage("File uploaded successfully!");
      } else {
        setStatusMessage("Failed to upload the file");
      }
    } catch (error) {
      setStatusMessage("An error occurred: " + error.message);
    }
  };

  return (
    <div>
      <h2>Upload JSON File</h2>
      <input type="file" accept=".json" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>
      {statusMessage && <p>{statusMessage}</p>}
    </div>
  );
};

export default UploadJson;