import { useState } from "react";

const API = "http://localhost:5000";

export default function App() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setTranscript(""); setResult(""); setError("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Upload failed");
      setTranscript(data.transcript);
      setResult(data.result);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>🎙️ Meeting Assistant</h1>
      <p style={styles.sub}>Upload a recording — get summary & action items</p>

      <div style={styles.card}>
        <input type="file" accept=".mp4,.mkv,.mp3,.wav,.m4a"
          onChange={(e) => setFile(e.target.files[0])} />
        {file && <p style={styles.filename}>📁 {file.name}</p>}
        <button onClick={handleUpload} disabled={!file || status === "uploading"} style={styles.button}>
          {status === "uploading" ? "Processing… (may take a few mins)" : "Upload & Analyse"}
        </button>
      </div>

      {error && <p style={styles.error}>❌ {error}</p>}

      {status === "done" && (
        <>
          <div style={styles.card}>
            <h2>📋 Summary & Action Items</h2>
            <pre style={styles.pre}>{result}</pre>
          </div>
          <div style={styles.card}>
            <h2>📝 Raw Transcript</h2>
            <p style={styles.transcript}>{transcript}</p>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: { maxWidth: 720, margin: "60px auto", padding: "0 20px", fontFamily: "system-ui, sans-serif" },
  title: { fontSize: 32, fontWeight: 700 },
  sub: { color: "#666", marginBottom: 32 },
  card: { background: "#f8f9fa", borderRadius: 12, padding: 24, marginBottom: 20, display: "flex", flexDirection: "column", gap: 12 },
  filename: { color: "#444", fontSize: 14 },
  button: { padding: "12px 24px", background: "#4F46E5", color: "#fff", border: "none", borderRadius: 8, fontSize: 15, cursor: "pointer", fontWeight: 600 },
  pre: { whiteSpace: "pre-wrap", lineHeight: 1.7, color: "#333" },
  transcript: { lineHeight: 1.7, color: "#555", whiteSpace: "pre-wrap" },
  error: { color: "#dc2626" },
};