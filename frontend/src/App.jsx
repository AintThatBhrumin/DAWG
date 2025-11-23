import { useState } from "react";
import FileUpload from "./components/FileUpload";
import OutputViewer from "./components/OutputViewer";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="min-h-screen bg-gray-950 text-white p-10">
      <h1 className="text-4xl font-bold mb-10">AI Invoice Extractor</h1>

      <FileUpload setResult={setResult} />

      <OutputViewer result={result} />
    </div>
  );
}
