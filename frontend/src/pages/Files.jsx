import { useEffect, useRef, useState } from "react";
import { api } from "../services/api";

function formatBytes(bytes) {
  if (!bytes) return "0 KB";
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default function Files() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const load = async () => {
    try {
      const data = await api.listFiles();
      setFiles(data.files);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await api.uploadFile(file);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDelete = async (fileId) => {
    await api.deleteFile(fileId);
    load();
  };

  return (
    <div className="section">
      <h2>Cloud files</h2>
      <p style={{ color: "var(--color-ink-soft)" }}>
        Demo object storage for optional meal photos or exported plans. Images, PDFs, and text files
        up to 5 MB.
      </p>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="file-input-wrap" style={{ marginBottom: 24 }}>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleUpload}
          disabled={uploading}
          accept=".png,.jpg,.jpeg,.gif,.webp,.pdf,.txt,.json"
        />
        {uploading && <p style={{ marginTop: 10 }}>Uploading…</p>}
      </div>

      {files.length === 0 && (
        <div className="empty-state">
          <p>No files uploaded yet.</p>
        </div>
      )}
      {files.map((f) => (
        <div className="list-row" key={f.file_id}>
          <div>
            <strong>{f.filename}</strong>{" "}
            <span style={{ color: "var(--color-ink-soft)" }}>· {formatBytes(f.size_bytes)}</span>
          </div>
          <button className="btn btn-danger" onClick={() => handleDelete(f.file_id)}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}
