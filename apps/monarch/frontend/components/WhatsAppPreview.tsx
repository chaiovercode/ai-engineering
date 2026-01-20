"use client";

import { forwardRef } from "react";

interface WhatsAppPreviewProps {
  message: string;
}

function DoubleCheck() {
  return (
    <svg className="w-4 h-4 text-[#53BDEB] inline-block ml-1" viewBox="0 0 16 15" fill="currentColor">
      <path d="M15.01 3.316l-.478-.372a.365.365 0 00-.51.063L8.666 9.879a.32.32 0 01-.484.033l-.358-.325a.319.319 0 00-.484.033l-.378.456a.32.32 0 00.063.476l1.218 1.102a.32.32 0 00.484-.033l6.272-8.048a.366.366 0 00-.063-.51zm-4.986.71l-.478-.372a.365.365 0 00-.51.063L4.566 9.879a.32.32 0 01-.484.033L1.891 7.769a.366.366 0 00-.51.063l-.479.372a.365.365 0 00-.063.51l3.136 3.102a.32.32 0 00.484-.033l6.272-8.048a.366.366 0 00-.063-.51z" />
    </svg>
  );
}

function formatWhatsAppText(text: string): string {
  return text
    .replace(/\*([^*]+)\*/g, '<strong class="font-semibold">$1</strong>')
    .replace(/_([^_]+)_/g, '<em>$1</em>')
    .replace(/~([^~]+)~/g, '<del>$1</del>')
    .replace(/```([^`]+)```/g, '<code class="bg-gray-200 px-1 rounded text-sm font-mono">$1</code>')
    .replace(/\n/g, '<br />');
}

export const WhatsAppPreview = forwardRef<HTMLDivElement, WhatsAppPreviewProps>(
  function WhatsAppPreview({ message }, ref) {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });

    return (
      <div ref={ref} className="bg-[#E5DDD5] rounded-lg overflow-hidden">
      {/* WhatsApp header */}
      <div className="bg-[#075E54] px-4 py-3 flex items-center gap-3">
        <button className="text-white">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z" />
          </svg>
        </button>
        <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center overflow-hidden">
          <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
        </div>
        <div className="flex-1">
          <p className="text-white font-medium text-sm">Client Name</p>
          <p className="text-white/70 text-xs">online</p>
        </div>
        <div className="flex items-center gap-4 text-white">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm-9-2V7H4v3H1v2h3v3h2v-3h3v-2H6zm9 4c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
          </svg>
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
            <circle cx="5" cy="12" r="2" />
            <circle cx="12" cy="12" r="2" />
            <circle cx="19" cy="12" r="2" />
          </svg>
        </div>
      </div>

      {/* Chat area */}
      <div
        className="p-4 min-h-[200px]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c8c4be' fill-opacity='0.15'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundColor: '#E5DDD5'
        }}
      >
        {/* Message bubble */}
        <div className="max-w-[85%] ml-auto">
          <div className="bg-[#DCF8C6] rounded-lg rounded-tr-none p-3 shadow-sm relative">
            {/* Tail */}
            <div
              className="absolute -right-2 top-0 w-0 h-0"
              style={{
                borderLeft: '8px solid #DCF8C6',
                borderTop: '8px solid transparent',
              }}
            />

            <div
              className="text-sm text-gray-900 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: formatWhatsAppText(message) }}
            />

            <div className="flex items-center justify-end mt-1 -mb-1 text-[11px] text-gray-500">
              <span>{timeString}</span>
              <DoubleCheck />
            </div>
          </div>
        </div>
      </div>

      {/* Input area */}
      <div className="bg-[#F0F0F0] px-2 py-2 flex items-center gap-2">
        <button className="p-2 text-gray-500">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
          </svg>
        </button>
        <button className="p-2 text-gray-500">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5a2.5 2.5 0 015 0v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5a2.5 2.5 0 005 0V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z" />
          </svg>
        </button>
        <div className="flex-1 bg-white rounded-full px-4 py-2">
          <input
            type="text"
            placeholder="Type a message"
            className="w-full text-sm outline-none"
            disabled
          />
        </div>
        <button className="p-2 text-gray-500">
          <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 15c1.66 0 2.99-1.34 2.99-3L15 6c0-1.66-1.34-3-3-3S9 4.34 9 6v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 15 6.7 12H5c0 3.42 2.72 6.23 6 6.72V22h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" />
          </svg>
        </button>
      </div>
    </div>
    );
  }
);
