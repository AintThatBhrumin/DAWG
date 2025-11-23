import { useState } from "react";

export default function OutputViewer({ result }) {
  const [showJson, setShowJson] = useState(false);

  if (!result) return null;

  const structured = result.structured;

  return (
    <div className="w-full max-w-3xl bg-gray-900 p-6 rounded-lg border border-gray-700">
      <div className="flex justify-between mb-4">
        <h2 className="text-2xl font-semibold">Extracted Invoice Data</h2>
        <button
          onClick={() =>
            navigator.clipboard.writeText(JSON.stringify(structured, null, 2))
          }
          className="bg-gray-700 px-3 py-1 rounded hover:bg-gray-600"
        >
          Copy JSON
        </button>
      </div>

      {/* Simple Table */}
      <table className="table-auto w-full mb-4 text-left">
        <tbody>
          {Object.entries(structured).map(([key, value]) => {
            if (key === "items" || key === "raw_text") return null;
            return (
              <tr key={key} className="border-b border-gray-700">
                <td className="py-2 font-semibold w-40 capitalize">
                  {key.replace("_", " ")}
                </td>
                <td className="py-2">{value ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Items */}
      <h3 className="text-xl font-semibold mt-4 mb-2">Items</h3>
      <table className="table-auto w-full mb-4">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="py-2">Name</th>
            <th className="py-2">Qty</th>
            <th className="py-2">Unit Price</th>
            <th className="py-2">Total</th>
          </tr>
        </thead>
        <tbody>
          {structured.items?.map((item, idx) => (
            <tr key={idx} className="border-b border-gray-800">
              <td className="py-2">{item.name}</td>
              <td className="py-2">{item.quantity}</td>
              <td className="py-2">{item.unit_price}</td>
              <td className="py-2">{item.total_price}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Collapsible JSON */}
      <button
        onClick={() => setShowJson(!showJson)}
        className="mt-4 bg-gray-800 px-4 py-2 rounded"
      >
        {showJson ? "Hide JSON" : "Show JSON"}
      </button>

      {showJson && (
        <pre className="bg-black p-4 mt-3 rounded text-green-400 text-sm overflow-x-auto max-h-96">
          {JSON.stringify(structured, null, 2)}
        </pre>
      )}
    </div>
  );
}
