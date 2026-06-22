import { useState, useCallback } from 'react'
import { parseFile, detectMissingValues, detectDuplicates, inferDataType } from '../utils/parser'

export const useUpload = () => {
  const [files, setFiles] = useState([])
  const [parsedData, setParsedData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [qualityReport, setQualityReport] = useState(null)

  const handleFileDrop = useCallback(async (acceptedFiles) => {
    setIsLoading(true)
    setError(null)

    try {
      const newFiles = acceptedFiles.map((file) => ({
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        id: Math.random().toString(36).substr(2, 9),
      }))

      setFiles((prev) => [...prev, ...newFiles])

      // Parse the first file for preview
      if (acceptedFiles.length > 0) {
        const result = await parseFile(acceptedFiles[0])
        setParsedData(result)

        // Generate quality report
        const missing = detectMissingValues(result.data, result.headers)
        const duplicates = detectDuplicates(result.data)
        const types = {}
        result.headers.forEach((header) => {
          const values = result.data.map((row) => row[header])
          types[header] = inferDataType(values)
        })

        setQualityReport({
          missing,
          duplicates: duplicates.length,
          types,
          totalRows: result.rowCount,
          totalColumns: result.headers.length,
        })
      }
    } catch (err) {
      setError(err.message || 'Failed to parse file')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const removeFile = useCallback((id) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }, [])

  const clearFiles = useCallback(() => {
    setFiles([])
    setParsedData(null)
    setQualityReport(null)
    setError(null)
  }, [])

  return {
    files,
    parsedData,
    isLoading,
    error,
    qualityReport,
    handleFileDrop,
    removeFile,
    clearFiles,
  }
}
