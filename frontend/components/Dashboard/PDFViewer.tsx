"use client";

import { useEffect, useRef } from "react";

interface PDFViewerProps {
  file: File | string | null;
  pageNumber?: number;
}

export default function PDFViewer({ file, pageNumber }: PDFViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const blobUrlRef = useRef<string | null>(null);

  // Cleanup blob URL on unmount
  useEffect(() => {
    return () => {
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!file || !containerRef.current) return;

    const loadPDF = async () => {
      try {
        let url: string;
        if (file instanceof File) {
          // Revoke previous blob URL if it exists
          if (blobUrlRef.current) {
            URL.revokeObjectURL(blobUrlRef.current);
          }
          url = URL.createObjectURL(file);
          blobUrlRef.current = url;
        } else {
          url = file;
        }

        // Add page number to URL if specified
        if (pageNumber && pageNumber > 0) {
          url += `#page=${pageNumber}`;
        }

        // Create iframe for PDF display
        const iframe = document.createElement("iframe");
        iframe.src = url;
        iframe.className = "w-full h-full border-0";
        iframe.style.borderRadius = "12px";
        iframeRef.current = iframe;
        
        if (containerRef.current) {
          containerRef.current.innerHTML = "";
          containerRef.current.appendChild(iframe);
        }
      } catch (error) {
        console.error("Error loading PDF:", error);
      }
    };

    loadPDF();
  }, [file]);

  // Navigate to specific page when pageNumber changes
  useEffect(() => {
    if (!file || !iframeRef.current) return;

    try {
      let baseUrl: string;
      if (file instanceof File) {
        // Use the stored blob URL
        if (!blobUrlRef.current) {
          blobUrlRef.current = URL.createObjectURL(file);
        }
        baseUrl = blobUrlRef.current;
      } else {
        // For string URLs, remove any existing hash
        baseUrl = file.split('#')[0];
      }

      // Update iframe src with page number
      if (pageNumber && pageNumber > 0) {
        iframeRef.current.src = `${baseUrl}#page=${pageNumber}`;
      } else {
        iframeRef.current.src = baseUrl;
      }
    } catch (error) {
      console.error("Error navigating to page:", error);
    }
  }, [pageNumber, file]);

  if (!file) {
    return (
      <div className="w-full h-full bg-gray-800 rounded-xl flex items-center justify-center">
        <p className="text-gray-400 dm-sans-button">No PDF loaded</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-full bg-black rounded-xl overflow-hidden shadow-lg"
    />
  );
}

