import React from 'react'
import FileDropzone from '../components/upload/FileDropzone'
import FilePreview from '../components/upload/FilePreview'
import { useUpload } from '../hooks/useUpload'

const Upload = () => {
  const { files, parsedData, isLoading, error, qualityReport, handleFileDrop, removeFile, clearFiles } = useUpload()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-header">Datasets</h1>
        <p className="page-subheader">Upload and manage the data powering your analyses.</p>
      </div>

      <FileDropzone onDrop={handleFileDrop} isLoading={isLoading} />

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">
          {error}
        </div>
      )}

      <FilePreview
        files={files}
        onRemove={removeFile}
        selectedDatasets={['1', '2']}
        onSelect={(id) => console.log(id)}
      />
    </div>
  )
}

export default Upload
