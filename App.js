import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResponse(JSON.stringify(data, null, 2));
    } catch (err) {
      setResponse("Error uploading file");
    }
  };

  return (
    <div style={{ padding: 32 }}>
      <h1>Course Outline PDF Upload</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept="application/pdf" onChange={handleFileChange} />
        <button type="submit" disabled={!file}>Upload</button>
      </form>
      {response && (
        <div style={{ marginTop: 20 }}>
          <h2>Server Response:</h2>
          <pre>{response}</pre>
        </div>
      )}
    </div>
  );
}

export default App;