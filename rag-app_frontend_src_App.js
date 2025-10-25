import React, {useState} from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [uploadResp, setUploadResp] = useState(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Choose a file");
    const fd = new FormData();
    fd.append("file", file);
    try {
      const r = await axios.post("/api/upload", fd, { headers: {"Content-Type":"multipart/form-data"} });
      setUploadResp(r.data);
      alert("Uploaded: " + JSON.stringify(r.data));
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + err.message);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!query) return alert("Type a query");
    try {
      const r = await axios.post("/api/query", { query, top_k: 3 });
      setAnswer(r.data.answer);
    } catch (err) {
      console.error(err);
      alert("Query failed: " + err.message);
    }
  };

  return (
    <div style={{maxWidth:800, margin:"2rem auto", fontFamily:"sans-serif"}}>
      <h2>RAG Demo UI</h2>

      <form onSubmit={handleUpload}>
        <div>
          <input type="file" onChange={(e)=>setFile(e.target.files[0])} />
          <button type="submit">Upload</button>
        </div>
      </form>

      <hr />

      <form onSubmit={handleQuery}>
        <div>
          <input style={{width:"80%"}} value={query} onChange={(e)=>setQuery(e.target.value)} placeholder="Ask a question about uploaded docs" />
          <button type="submit">Ask</button>
        </div>
      </form>

      <div style={{marginTop:20}}>
        <strong>Answer:</strong>
        <div style={{whiteSpace:"pre-wrap", marginTop:8, background:"#f6f6f6", padding:12}}>
          {answer || "No answer yet"}
        </div>
      </div>
    </div>
  );
}
