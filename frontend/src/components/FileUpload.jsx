import { useState } from "react";

export default function FileUpload({ setResult }) {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const API = import.meta.env.VITE_API_BASE_URL;

  const extract = async () => {
    setLoading(true);

    try {
      let response;

      if (file) {
        const form = new FormData();
        form.append("file", file);

        response = await fetch(`${API}/invoices/extract`, {
          method: "POST",
          body: form,
        });
      } else {
        response = await fetch(`${API}/invoices/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Extraction failed.");
    }

    setLoading(false);
  };

  return (
    <div className="mb-10 w-full max-w-xl">
      <h2 className="text-2xl font-semibold mb-4">Upload Invoice</h2>

      {/* File Upload */}
      <input
        type="file"
        accept=".pdf, image/*"
        onChange={(e) => setFile(e.target.files[0])}
        className="mb-4"
      />

      <p className="my-3 text-gray-400">OR Paste raw text</p>

      {/* Raw Text */}
      <textarea
        className="w-full h-32 bg-gray-800 p-3 rounded"
        placeholder="Paste text..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        onClick={extract}
        className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded w-full font-semibold"
        disabled={loading}
      >
        {loading ? "Extracting..." : "Extract Data"}
      </button>
    </div>
  );
}
