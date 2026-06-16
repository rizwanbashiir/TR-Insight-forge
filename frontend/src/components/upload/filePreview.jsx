import { useData } from "@/context/DataContext";
import { formatBytes, formatDate } from "@/utils/formatter";

export default function FilePreview({ onRemove }) {
  const { state } = useData();
  const { file, parsedData } = state;

  if (!file) return null;

  const ext = file.name.split(".").pop().toUpperCase();

  const iconMap = {
    CSV: { icon: "table_chart", color: "text-green-600", bg: "bg-green-50" },
    XLSX: { icon: "grid_on", color: "text-blue-600", bg: "bg-blue-50" },
    XLS: { icon: "grid_on", color: "text-blue-600", bg: "bg-blue-50" },
    JSON: { icon: "data_object", color: "text-yellow-600", bg: "bg-yellow-50" },
  };

  const iconInfo = iconMap[ext] || { icon: "description", color: "text-outline", bg: "bg-surface-container" };

  return (
    <div className="bento-card rounded-xl p-md flex flex-col gap-md">
      {/* File info header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-sm">
          <div className={`w-10 h-10 rounded-lg ${iconInfo.bg} flex items-center justify-center`}>
            <span className={`material-symbols-outlined ${iconInfo.color}`}>{iconInfo.icon}</span>
          </div>
          <div>
            <p className="font-bold text-on-surface truncate max-w-xs">{file.name}</p>
            <p className="font-label-sm text-label-sm text-on-surface-variant">
              {formatBytes(file.size)} · {ext} · Uploaded {formatDate(new Date())}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-sm">
          <span className="flex items-center gap-xs font-label-sm text-label-sm text-green-600 bg-green-50 px-sm py-xs rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
            Ready
          </span>
          <button
            onClick={onRemove}
            className="material-symbols-outlined text-on-surface-variant hover:text-error transition-colors"
          >
            close
          </button>
        </div>
      </div>

      {/* Preview table */}
      {parsedData && parsedData.length > 0 && (
        <div className="overflow-auto max-h-64 custom-scrollbar rounded-lg border border-outline-variant">
          <table className="w-full text-sm border-collapse">
            <thead className="bg-surface-container-low sticky top-0">
              <tr>
                {Object.keys(parsedData[0]).map((col) => (
                  <th
                    key={col}
                    className="px-sm py-xs text-left font-label-sm text-label-sm text-on-surface-variant uppercase border-b border-outline-variant whitespace-nowrap"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {parsedData.slice(0, 8).map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-outline-variant hover:bg-surface-container-low/50 transition-colors"
                >
                  {Object.values(row).map((val, j) => (
                    <td
                      key={j}
                      className="px-sm py-xs font-label-sm text-label-sm text-on-surface whitespace-nowrap max-w-[160px] truncate"
                    >
                      {String(val ?? "")}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {parsedData.length > 8 && (
            <p className="text-center font-label-sm text-label-sm text-on-surface-variant py-sm">
              + {parsedData.length - 8} more rows
            </p>
          )}
        </div>
      )}

      {/* Stats row */}
      {parsedData && (
        <div className="flex gap-md flex-wrap">
          {[
            { label: "Rows", value: parsedData.length.toLocaleString() },
            { label: "Columns", value: Object.keys(parsedData[0] || {}).length },
            { label: "Format", value: ext },
          ].map((stat) => (
            <div key={stat.label} className="flex flex-col">
              <span className="font-label-sm text-label-sm text-on-surface-variant uppercase">{stat.label}</span>
              <span className="font-headline-md text-headline-md text-primary">{stat.value}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}