import Papa from 'papaparse'
import * as XLSX from 'xlsx'

export const parseCSV = (file, options = {}) => {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: true,
      ...options,
      complete: (results) => {
        resolve({
          data: results.data,
          headers: results.meta.fields || [],
          rowCount: results.data.length,
        })
      },
      error: (error) => reject(error),
    })
  })
}

export const parseExcel = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(firstSheet, { header: 1 })

        const headers = jsonData[0] || []
        const rows = jsonData.slice(1).map((row) => {
          const obj = {}
          headers.forEach((header, i) => {
            obj[header] = row[i] !== undefined ? row[i] : null
          })
          return obj
        })

        resolve({
          data: rows,
          headers,
          rowCount: rows.length,
        })
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}

export const parseJSON = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        const rows = Array.isArray(data) ? data : [data]
        const headers = rows.length > 0 ? Object.keys(rows[0]) : []
        resolve({
          data: rows,
          headers,
          rowCount: rows.length,
        })
      } catch (err) {
        reject(err)
      }
    }
    reader.onerror = reject
    reader.readAsText(file)
  })
}

export const detectFileType = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  const typeMap = {
    csv: 'csv',
    tsv: 'csv',
    xlsx: 'excel',
    xls: 'excel',
    json: 'json',
  }
  return typeMap[ext] || 'unknown'
}

export const parseFile = async (file) => {
  const type = detectFileType(file.name)
  switch (type) {
    case 'csv':
      return parseCSV(file)
    case 'excel':
      return parseExcel(file)
    case 'json':
      return parseJSON(file)
    default:
      throw new Error(`Unsupported file type: ${type}`)
  }
}

export const inferDataType = (values) => {
  const nonNull = values.filter((v) => v !== null && v !== undefined && v !== '')
  if (nonNull.length === 0) return 'empty'

  const allNumbers = nonNull.every((v) => !isNaN(parseFloat(v)) && isFinite(v))
  if (allNumbers) return 'number'

  const allDates = nonNull.every((v) => !isNaN(Date.parse(v)))
  if (allDates) return 'date'

  return 'string'
}

export const detectMissingValues = (data, headers) => {
  const missing = {}
  headers.forEach((header) => {
    const count = data.filter((row) => {
      const val = row[header]
      return val === null || val === undefined || val === '' || val === 'NaN'
    }).length
    if (count > 0) {
      missing[header] = {
        count,
        percentage: ((count / data.length) * 100).toFixed(1),
      }
    }
  })
  return missing
}

export const detectDuplicates = (data) => {
  const seen = new Set()
  const duplicates = []
  data.forEach((row, index) => {
    const key = JSON.stringify(row)
    if (seen.has(key)) {
      duplicates.push(index)
    } else {
      seen.add(key)
    }
  })
  return duplicates
}
