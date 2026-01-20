"use client";

import { forwardRef } from "react";

interface LinkedInPreviewProps {
  content: string;
  hashtags: string[];
  hideEngagement?: boolean;
}

// LinkedIn reaction icons
function LikeIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="#0A66C2">
      <path d="M19.46 11l-3.91-3.91a7 7 0 01-1.69-2.74l-.49-1.47A2.76 2.76 0 0010.76 1 2.75 2.75 0 008 3.74v1.12a9.19 9.19 0 00.46 2.85L8.89 9H4.12A2.12 2.12 0 002 11.12a2.16 2.16 0 00.92 1.76A2.11 2.11 0 002 14.62a2.14 2.14 0 001.28 2 2 2 0 00-.28 1 2.12 2.12 0 002 2.12v.14A2.12 2.12 0 007.12 22h7.49a8.08 8.08 0 003.58-.84l.31-.16H21V11zM19 19h-1l-.73.37a6.14 6.14 0 01-2.69.63H7.72a1 1 0 01-1-.72l-.25-.87-.85-.41A1 1 0 015 17l.17-1-.76-.74A1 1 0 014.27 14l.66-1.09-.73-1.1a1 1 0 01.46-1.43l1-.47L6 9.46a8.19 8.19 0 01-.12-1.42v-4A.76.76 0 016.76 3h.01a.77.77 0 01.74.57l.49 1.47a8.91 8.91 0 002.13 3.45l4.16 4.14V19z" />
    </svg>
  );
}

function CommentIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M7 9h10v1H7V9zm0 4h7v-1H7v1zm16-2a6.78 6.78 0 01-2.84 5.61L12 22v-4H8A7 7 0 018 4h8a7 7 0 017 7zm-2 0a5 5 0 00-5-5H8a5 5 0 000 10h6v2.28L18 15a4.79 4.79 0 003-4z" />
    </svg>
  );
}

function RepostIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M13.96 5H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2v-1h-2v1H6V7h7.96L12 10.5l1.5 1.5 5-5-5-5L12 3.5 13.96 5zm5.54 9v-5h-2v5h-2l2.5 3 2.5-3h-1z" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 3L0 10l7.66 4.26L16 8l-6.26 8.34L14 24l7-21z" />
    </svg>
  );
}

export const LinkedInPreview = forwardRef<HTMLDivElement, LinkedInPreviewProps>(
  function LinkedInPreview({ content, hashtags, hideEngagement = false }, ref) {
    return (
      <div ref={ref} className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-3 flex items-start gap-3">
        <div className="w-12 h-12 bg-gradient-to-br from-[#00a651] to-[#008c44] rounded-full flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-lg">M</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="font-semibold text-sm text-gray-900 hover:text-[#0A66C2] hover:underline cursor-pointer">
              Monarch Networth Capital
            </span>
          </div>
          <p className="text-xs text-gray-500 truncate">
            12,450 followers
          </p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <span>Just now</span>
            <span>•</span>
            <svg className="w-3 h-3" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 1a7 7 0 107 7 7 7 0 00-7-7zM3 8a5 5 0 011.35-3.42 4.94 4.94 0 01.85 1.45A4.94 4.94 0 005 8a5 5 0 00.05.66A5 5 0 013 8zm5 5a5 5 0 01-3.61-1.55 4.94 4.94 0 01.77-1.45A4.94 4.94 0 008 10.25a4.94 4.94 0 002.84-.25 4.94 4.94 0 01.77 1.45A5 5 0 018 13zM8 9a4.94 4.94 0 01-2.84-.25 4.94 4.94 0 01-.77-1.45A5 5 0 018 6a5 5 0 013.61 1.55 4.94 4.94 0 01-.77 1.45A4.94 4.94 0 018 9zm5-1a5 5 0 00-.05-.66A5 5 0 0013 8a5 5 0 00-1.35-3.42 4.94 4.94 0 00-.85 1.45A4.94 4.94 0 0011 8a5 5 0 01-.05.66A5 5 0 0113 8z" />
            </svg>
          </p>
        </div>
        {!hideEngagement && (
          <button className="text-gray-400 hover:text-gray-600 p-1">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="5" cy="12" r="2" />
              <circle cx="12" cy="12" r="2" />
              <circle cx="19" cy="12" r="2" />
            </svg>
          </button>
        )}
      </div>

      {/* Content */}
      <div className="px-4 pb-3">
        <div className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
          {content}
        </div>
        {hashtags.length > 0 && (
          <div className="mt-2 text-sm">
            {hashtags.map((tag, i) => (
              <span key={tag}>
                <span className="text-[#0A66C2] hover:underline cursor-pointer">
                  #{tag}
                </span>
                {i < hashtags.length - 1 && " "}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Engagement stats - hidden when exporting */}
      {!hideEngagement && (
        <>
          <div className="px-4 py-2 flex items-center justify-between text-xs text-gray-500 border-t border-gray-100">
            <div className="flex items-center gap-1">
              <div className="flex -space-x-1">
                <div className="w-4 h-4 bg-[#0A66C2] rounded-full flex items-center justify-center">
                  <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19.46 11l-3.91-3.91a7 7 0 01-1.69-2.74l-.49-1.47A2.76 2.76 0 0010.76 1 2.75 2.75 0 008 3.74v1.12a9.19 9.19 0 00.46 2.85L8.89 9H4.12A2.12 2.12 0 002 11.12a2.16 2.16 0 00.92 1.76A2.11 2.11 0 002 14.62a2.14 2.14 0 001.28 2 2 2 0 00-.28 1 2.12 2.12 0 002 2.12v.14A2.12 2.12 0 007.12 22h7.49a8.08 8.08 0 003.58-.84l.31-.16H21V11z" />
                  </svg>
                </div>
                <div className="w-4 h-4 bg-[#DF704D] rounded-full flex items-center justify-center">
                  <span className="text-[8px] text-white">❤️</span>
                </div>
              </div>
              <span className="hover:text-[#0A66C2] hover:underline cursor-pointer">247</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="hover:text-[#0A66C2] hover:underline cursor-pointer">18 comments</span>
              <span>•</span>
              <span className="hover:text-[#0A66C2] hover:underline cursor-pointer">12 reposts</span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="px-2 py-1 flex items-center justify-around border-t border-gray-200">
            <button className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-100 rounded transition-colors text-sm font-medium">
              <LikeIcon />
              <span>Like</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-100 rounded transition-colors text-sm font-medium">
              <CommentIcon />
              <span>Comment</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-100 rounded transition-colors text-sm font-medium">
              <RepostIcon />
              <span>Repost</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-3 text-gray-600 hover:bg-gray-100 rounded transition-colors text-sm font-medium">
              <SendIcon />
              <span>Send</span>
            </button>
          </div>
        </>
      )}
    </div>
    );
  }
);
