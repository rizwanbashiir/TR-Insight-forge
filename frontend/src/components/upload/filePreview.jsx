import React from 'react'
import { FileSpreadsheet, X, Check } from 'lucide-react'
import { formatNumber } from '../../utils/formatter'

const FilePreview = ({ files, onRemove, selectedDatasets, onSelect }) => {
  if (!files || files.length === 0) return null

  const selectedCount = selectedDatasets?.length || 0

  return (
    <div className="space-y-4">
      {/* Selected indicator */}
      {selectedCount > 0 && (
        <div className="flex items-center justify-between px-4 py-3 bg-white border border-slate-200 rounded-xl">
          <div className="flex items-center gap-2">
            <Check className="w-4 h-4 text-success-600" />
            <span className="text-sm font-medium text-slate-900">
              {selectedCount} dataset{selectedCount > 1 ? 's' : ''} selected
            </span>
            <span className="text-sm text-slate-500">· Ready for analysis</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="btn-secondary text-sm px-3 py-1.5">
              Clear
            </button>
            <button className="btn-primary text-sm px-3 py-1.5">
              Run analysis
            </button>
          </div>
        </div>
      )}

      {/* File list */}
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-900">Dataset history</h3>
        </div>
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-100">
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-8"></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Filename
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Rows
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                Uploaded
              </th>
              <th className="px-6 py-3 w-10"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {files.map((file) => (
              <tr key={file.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-4">
                  <input
                    type="checkbox"
                    checked={selectedDatasets?.includes(file.id)}
                    onChange={() => onSelect?.(file.id)}
                    className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                  />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <FileSpreadsheet className="w-5 h-5 text-primary-600" />
                    <span className="text-sm font-medium text-slate-900">
                      {file.name}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-600">{file.type || 'Sales'}</span>
                </td>
                <td className="px-6 py-4">
                  <span className="badge-green">Ready</span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-900">
                    {formatNumber(file.rowCount || 48902)}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-slate-500">{file.uploaded || '2 hours ago'}</span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => onRemove(file.id)}
                    className="p-1 text-slate-400 hover:text-danger-600 hover:bg-danger-50 rounded transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default FilePreview
