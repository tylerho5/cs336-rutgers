"use client"

import * as React from "react"
import { useState } from 'react';
import { ArrowUpDown, Download, Search } from 'lucide-react';

import { cn } from "@/lib/utils"

interface TableProps {
  headers: string[];
  rows: string[][];
  caption?: string;
}

export function Table({ headers, rows, caption }: TableProps) {
  const [sortColumn, setSortColumn] = useState<number | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [searchTerm, setSearchTerm] = useState("");

  const handleSort = (columnIndex: number) => {
    if (sortColumn === columnIndex) {
      // Toggle direction if same column
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New column, default to ascending
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
  };
  
  // Filter and sort data
  const filteredRows = rows.filter(row => {
    if (!searchTerm) return true;
    return row.some(cell => 
      cell.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });
  
  // Sort the rows if a sort column is selected
  const sortedRows = [...filteredRows];
  if (sortColumn !== null && sortColumn < headers.length) {
    sortedRows.sort((a, b) => {
      const valA = a[sortColumn] || '';
      const valB = b[sortColumn] || '';
      
      // Try numeric comparison first
      const numA = Number(valA);
      const numB = Number(valB);
      
      if (!isNaN(numA) && !isNaN(numB)) {
        return sortDirection === 'asc' ? numA - numB : numB - numA;
      }
      
      // Fall back to string comparison
      return sortDirection === 'asc' 
        ? valA.localeCompare(valB)
        : valB.localeCompare(valA);
    });
  }

  // Export to CSV
  const exportToCsv = () => {
    const headerRow = headers.join(',');
    const csvRows = sortedRows.map(row => row.map(cell => 
      // Wrap cells in quotes to handle commas in content
      `"${cell.replace(/"/g, '""')}"`
    ).join(','));
    
    const csvContent = [headerRow, ...csvRows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'query_results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (headers.length === 0 || rows.length === 0) {
    return (
      <div className="rounded-md border p-8 text-center text-gray-500">
        No data available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="relative w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
          <input
            placeholder="Search results..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8 pr-3 py-2 w-full rounded-md border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          />
        </div>
        <button 
          onClick={exportToCsv}
          className="flex items-center gap-1 px-3 py-1.5 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-emerald-500"
        >
          <Download className="h-4 w-4" />
          <span>Export CSV</span>
        </button>
      </div>

      <div className="overflow-x-auto rounded-md border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          {caption && <caption className="sr-only">{caption}</caption>}
          <thead className="bg-gray-50">
            <tr>
              {headers.map((header, index) => (
                <th
                  key={index}
                  scope="col"
                  className="px-3 py-3.5 text-left text-sm font-medium text-gray-500 select-none"
                >
                  <button
                    onClick={() => handleSort(index)}
                    className="flex items-center gap-1 hover:text-emerald-600 focus:outline-none"
                  >
                    {header}
                    <ArrowUpDown className={`h-4 w-4 transition-colors ${
                      sortColumn === index ? 'text-emerald-600' : 'text-gray-400'
                    }`} />
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {sortedRows.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {row.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className="whitespace-nowrap px-3 py-3 text-sm text-gray-500"
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="text-sm text-gray-500">
        {sortedRows.length} {sortedRows.length === 1 ? 'row' : 'rows'}
      </div>
    </div>
  );
}

function TableHeader({ className, ...props }: React.ComponentProps<"thead">) {
  return (
    <thead
      data-slot="table-header"
      className={cn("[&_tr]:border-b", className)}
      {...props}
    />
  )
}

function TableBody({ className, ...props }: React.ComponentProps<"tbody">) {
  return (
    <tbody
      data-slot="table-body"
      className={cn("[&_tr:last-child]:border-0", className)}
      {...props}
    />
  )
}

function TableFooter({ className, ...props }: React.ComponentProps<"tfoot">) {
  return (
    <tfoot
      data-slot="table-footer"
      className={cn(
        "bg-muted/50 border-t font-medium [&>tr]:last:border-b-0",
        className
      )}
      {...props}
    />
  )
}

function TableRow({ className, ...props }: React.ComponentProps<"tr">) {
  return (
    <tr
      data-slot="table-row"
      className={cn(
        "hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors",
        className
      )}
      {...props}
    />
  )
}

function TableHead({ className, ...props }: React.ComponentProps<"th">) {
  return (
    <th
      data-slot="table-head"
      className={cn(
        "text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
        className
      )}
      {...props}
    />
  )
}

function TableCell({ className, ...props }: React.ComponentProps<"td">) {
  return (
    <td
      data-slot="table-cell"
      className={cn(
        "p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]",
        className
      )}
      {...props}
    />
  )
}

function TableCaption({
  className,
  ...props
}: React.ComponentProps<"caption">) {
  return (
    <caption
      data-slot="table-caption"
      className={cn("text-muted-foreground mt-4 text-sm", className)}
      {...props}
    />
  )
}

export {
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
}
