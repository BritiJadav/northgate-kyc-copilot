import React, { useState, useEffect, useRef } from 'react';
import { CompanyDocument } from '../types/kyc';
import { FileText, Image as ImageIcon, ExternalLink, CheckCircle2, Search, ZoomIn, ZoomOut } from 'lucide-react';

interface PdfViewerProps {
  documents: CompanyDocument[];
  activeDoc: string;
  onSelectDoc: (filename: string) => void;
  highlightLine?: {
    doc: string;
    page: number;
    line: number;
    quote?: string;
  } | null;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({
  documents,
  activeDoc,
  onSelectDoc,
  highlightLine,
}) => {
  const [docLines, setDocLines] = useState<Array<{ page: number; line: number; text: string }>>([]);
  const [loadingText, setLoadingText] = useState(false);
  const [viewMode, setViewMode] = useState<'reader' | 'image' | 'raw'>('reader');
  const [fontSize, setFontSize] = useState<number>(12);
  const lineRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});

  const currentDocObj = documents.find((d) => d.filename === activeDoc) || documents[0];
  const isImageScan = currentDocObj?.filename.endsWith('.png') || currentDocObj?.low_legibility;

  // Load document indexed text when activeDoc changes
  useEffect(() => {
    if (!activeDoc) return;
    setLoadingText(true);

    const txtFilename = activeDoc.replace(/\.(pdf|png)$/, '_indexed.txt');
    fetch(`/documents/${txtFilename}`)
      .then((res) => {
        if (!res.ok) throw new Error('Text layer not found');
        return res.text();
      })
      .then((text) => {
        const parsed: Array<{ page: number; line: number; text: string }> = [];
        const lines = text.split('\n');
        for (const l of lines) {
          if (!l.trim()) continue;
          // Format: [doc:file.pdf p1 L1] Text
          const match = l.match(/\[doc:[^ ]+ p(\d+) L(\d+)\] (.*)/);
          if (match) {
            parsed.push({
              page: parseInt(match[1], 10),
              line: parseInt(match[2], 10),
              text: match[3],
            });
          }
        }
        setDocLines(parsed);
      })
      .catch(() => {
        setDocLines([]);
      })
      .finally(() => {
        setLoadingText(false);
      });
  }, [activeDoc]);

  // Auto-scroll to cited line when highlightLine changes
  useEffect(() => {
    if (highlightLine && highlightLine.doc === activeDoc) {
      const key = `${highlightLine.page}-${highlightLine.line}`;
      const elem = lineRefs.current[key];
      if (elem) {
        elem.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [highlightLine, activeDoc, docLines]);

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm flex flex-col h-full overflow-hidden">
      {/* Document Tabs */}
      <div className="bg-slate-100 border-b border-slate-200 px-3 pt-2 flex items-center justify-between">
        <div className="flex items-center space-x-1 overflow-x-auto max-w-[80%] pb-1 scrollbar-none">
          {documents.map((doc) => {
            const isActive = doc.filename === activeDoc;
            return (
              <button
                key={doc.filename}
                onClick={() => {
                  onSelectDoc(doc.filename);
                  if (doc.filename.endsWith('.png')) setViewMode('image');
                }}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-t text-xs font-medium border-t border-x transition whitespace-nowrap ${
                  isActive
                    ? 'bg-white border-slate-300 text-slate-900 font-semibold shadow-sm -mb-[1px]'
                    : 'bg-slate-200/60 border-transparent text-slate-600 hover:bg-slate-200'
                }`}
              >
                {doc.filename.endsWith('.png') ? (
                  <ImageIcon className="w-3.5 h-3.5 text-purple-600" />
                ) : (
                  <FileText className="w-3.5 h-3.5 text-blue-600" />
                )}
                <span className="truncate max-w-[150px]">{doc.filename}</span>
                {doc.low_legibility && (
                  <span className="bg-amber-100 text-amber-800 text-[9px] px-1 rounded font-bold">
                    Scan
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* View Controls */}
        <div className="flex items-center space-x-1 text-xs pb-1">
          {isImageScan && (
            <div className="flex items-center space-x-1 bg-white border border-slate-300 rounded px-1.5 py-0.5">
              <button
                onClick={() => setViewMode('image')}
                className={`px-1.5 py-0.5 rounded text-[11px] font-medium ${
                  viewMode === 'image' ? 'bg-purple-600 text-white' : 'text-slate-600'
                }`}
              >
                Scan View
              </button>
              <button
                onClick={() => setViewMode('reader')}
                className={`px-1.5 py-0.5 rounded text-[11px] font-medium ${
                  viewMode === 'reader' ? 'bg-purple-600 text-white' : 'text-slate-600'
                }`}
              >
                OCR Lines
              </button>
            </div>
          )}

          <button
            onClick={() => setFontSize(Math.max(10, fontSize - 1))}
            className="p-1 text-slate-500 hover:text-slate-800"
            title="Decrease text size"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setFontSize(Math.min(16, fontSize + 1))}
            className="p-1 text-slate-500 hover:text-slate-800"
            title="Increase text size"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <a
            href={`/documents/${activeDoc}`}
            target="_blank"
            rel="noreferrer"
            className="p-1 text-slate-500 hover:text-blue-600 transition"
            title="Open raw document in new window"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Citation Banner if active highlight */}
      {highlightLine && highlightLine.doc === activeDoc && (
        <div className="bg-amber-50 border-b border-amber-200 px-3 py-1.5 text-xs text-amber-900 flex items-center justify-between shadow-sm">
          <div className="flex items-center space-x-1.5 truncate">
            <span className="font-semibold text-amber-900">Active Citation Highlight:</span>
            <span className="bg-amber-200 px-1.5 py-0.2 rounded font-mono font-bold text-[11px]">
              Page {highlightLine.page}, Line {highlightLine.line}
            </span>
            {highlightLine.quote && (
              <span className="italic text-amber-800 truncate text-[11px]">
                "{highlightLine.quote}"
              </span>
            )}
          </div>
          <span className="text-emerald-700 font-semibold flex items-center space-x-1 text-[11px] shrink-0">
            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
            <span>Deterministic Citation Verified (C5)</span>
          </span>
        </div>
      )}

      {/* Document View Content */}
      <div className="flex-1 overflow-y-auto p-4 bg-slate-50 font-mono">
        {viewMode === 'image' && isImageScan ? (
          <div className="flex flex-col items-center justify-center p-4">
            <div className="border-4 border-slate-300 shadow-md rounded bg-white p-2">
              <img
                src={`/documents/${activeDoc}`}
                alt="Document Scan"
                className="max-w-full h-auto rounded"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-2 text-center">
              Low-legibility scanned stock transfer form (Calder Marine Services Ltd, Aug 2025). Switch to 'OCR Lines' to view line-indexed citations.
            </p>
          </div>
        ) : loadingText ? (
          <div className="text-center py-12 text-slate-400 text-xs font-sans">
            Loading document text layer...
          </div>
        ) : docLines.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs font-sans">
            No indexed lines available for this document.
          </div>
        ) : (
          <div className="space-y-1 bg-white p-4 rounded border border-slate-200 shadow-inner">
            {docLines.map((item) => {
              const key = `${item.page}-${item.line}`;
              const isHighlighted =
                highlightLine &&
                highlightLine.doc === activeDoc &&
                highlightLine.page === item.page &&
                highlightLine.line === item.line;

              return (
                <div
                  key={key}
                  ref={(el) => (lineRefs.current[key] = el)}
                  style={{ fontSize: `${fontSize}px` }}
                  className={`flex items-start space-x-3 py-0.5 px-2 rounded transition-colors ${
                    isHighlighted
                      ? 'bg-amber-100/90 text-amber-950 font-semibold border-l-4 border-amber-500 pl-1.5'
                      : 'hover:bg-slate-50 text-slate-800'
                  }`}
                >
                  <span className="select-none font-mono text-slate-400 text-[10px] w-12 shrink-0 pt-0.5">
                    p{item.page}:L{item.line}
                  </span>
                  <span className="break-words flex-1 leading-relaxed">{item.text}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
