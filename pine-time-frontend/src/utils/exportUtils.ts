/**
 * Utility functions for exporting data to CSV format
 */

/**
 * Convert an array of objects to CSV format and trigger download
 * @param filename The name of the file to download
 * @param rows Array of objects to convert to CSV
 */
export const exportToCsv = (filename: string, rows: Record<string, any>[]): void => {
  if (!rows || !rows.length) {
    console.warn('No data to export');
    return;
  }

  // Get headers from the first row
  const headers = Object.keys(rows[0]);
  
  // Convert data to CSV format
  const csvContent = [
    // Header row
    headers.join(','),
    // Data rows
    ...rows.map(row => 
      headers.map(header => {
        // Handle values that need to be quoted (contain commas, quotes, or newlines)
        const value = row[header] === null || row[header] === undefined ? '' : row[header].toString();
        const needsQuotes = value.includes(',') || value.includes('"') || value.includes('\n');
        
        if (needsQuotes) {
          // Escape quotes by doubling them and wrap in quotes
          return `"${value.replace(/"/g, '""')}"`;
        }
        
        return value;
      }).join(',')
    )
  ].join('\n');
  
  // Create a blob and download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  // Set up download link
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  // Add to document, trigger download, and clean up
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};
