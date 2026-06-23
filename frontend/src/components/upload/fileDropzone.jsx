import React from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud, FileSpreadsheet, FileJson, FileText } from 'lucide-react'

const FileDropzone = ({ onDrop, isLoading }) => {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/json': ['.json'],
      'text/tab-separated-values': ['.tsv'],
    },
    multiple: true,
  })

  return (
    <div
      {...getRootProps()}
      className={`dropzone p-12 text-center transition-all ${
        isDragActive ? 'dropzone-active' : ''
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-primary-600 text-white flex items-center justify-center">
          <UploadCloud className="w-7 h-7" />
        </div>
        <div>
          <p className="text-base font-semibold text-slate-900">
            Drop files to upload
          </p>
          <p className="text-sm text-slate-500 mt-1">
            Supports CSV, XLSX, JSON · Up to 500MB per file
          </p>
        </div>
        <button className="btn-primary mt-2" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Browse files'}
        </button>
      </div>
    </div>
  )
}

export default FileDropzone
