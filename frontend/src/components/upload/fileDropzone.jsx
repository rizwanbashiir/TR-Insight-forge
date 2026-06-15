import { useRef, useState } from "react";
import { useData } from "@/context/DataContext";

const ACCEPTED_TYPES = {
  "text/csv": [".csv"],
  "application/json": [".json"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-excel": [".xls"],
};

export default function FileDropzone({ onFileSelect }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const { dispatch } = useData();

  const handleFiles = (files) => {
    const file = files[0];
    if (!file) return;
    dispatch({ type: "SET_FILE", payload: file });
    onFileSelect?.(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => setDragging(false);

  const handleInputChange = (e) => {
    handleFiles(e.target.files);
  };

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={`
        bento-card rounded-xl border-dashed border-2 cursor-pointer
        flex flex-col items-center justify-center text-center gap-md
        p-xl transition-all select-none
        ${dragging
          ? "border-primary bg-primary-fixed/30 scale-[1.01]"
          : "border-primary/30 bg-surface-container-low hover:bg-surface-container"
        }
      `}
    >
      <div
        className={`
          w-16 h-16 rounded-full flex items-center justify-center transition-all
          ${dragging ? "bg-primary scale-110" : "bg-primary-container"}
        `}
      >
        <span
          className={`material-symbols-outlined text-4xl ${dragging ? "text-on-primary" : "text-on-primary-container"}`}
        >
          cloud_upload
        </span>
      </div>

      <div>
        <h2 className="font-headline-md text-headline-md text-on-surface">
          {dragging ? "Release to upload" : "Drop your file here"}
        </h2>
        <p className="font-body-md text-on-surface-variant mt-xs">
          Supports CSV, JSON, and Excel — or connect directly to your database.
        </p>
      </div>

      <div className="flex gap-sm flex-wrap justify-center">
        {[".CSV", ".XLSX", ".JSON"].map((ext) => (
          <span
            key={ext}
            className="px-sm py-1 rounded bg-surface-container text-outline font-label-sm text-label-sm border border-outline-variant"
          >
            {ext}
          </span>
        ))}
      </div>

      <div className="flex gap-sm flex-wrap justify-center">
        <button
          className="bg-primary text-on-primary px-lg py-sm rounded-lg font-bold hover:opacity-90 transition-all active:scale-95 shadow-md"
          onClick={(e) => { e.stopPropagation(); inputRef.current?.click(); }}
        >
          Upload File
        </button>
        <button
          className="bg-secondary-container text-on-secondary-container px-lg py-sm rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
          onClick={(e) => e.stopPropagation()}
        >
          Connect Data Source
        </button>
      </div>

      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={Object.keys(ACCEPTED_TYPES).join(",")}
        onChange={handleInputChange}
      />
    </div>
  );
}