"use client";

import { useState, useRef, useEffect } from "react";
import type { SavedReport } from "@/lib/storage";

interface ReportHistoryItemProps {
  report: SavedReport;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
  onUpdateTitle: (title: string) => void;
}

function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return new Date(timestamp).toLocaleDateString();
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z" />
      <path d="M10 11v6M14 11v6" />
    </svg>
  );
}

function PencilIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
    </svg>
  );
}

export function ReportHistoryItem({
  report,
  isActive,
  onClick,
  onDelete,
  onUpdateTitle,
}: ReportHistoryItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(report.title);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isEditing]);

  const handleSaveTitle = () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== report.title) {
      onUpdateTitle(trimmed);
    } else {
      setEditTitle(report.title);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSaveTitle();
    } else if (e.key === "Escape") {
      setEditTitle(report.title);
      setIsEditing(false);
    }
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (showDeleteConfirm) {
      onDelete();
      setShowDeleteConfirm(false);
    } else {
      setShowDeleteConfirm(true);
      setTimeout(() => setShowDeleteConfirm(false), 3000);
    }
  };

  const preview = report.linkedin?.content?.substring(0, 80) || report.reportText.substring(0, 80);

  return (
    <div
      onClick={onClick}
      className={`mx-2 mb-1 p-3 cursor-pointer transition-all duration-200 border-2 group ${
        isActive
          ? "bg-[var(--gold)]/10 border-[var(--gold)] shadow-[2px_2px_0px_var(--gold)]"
          : "bg-white border-transparent hover:border-[var(--ink)] hover:shadow-[2px_2px_0px_var(--ink)]"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        {isEditing ? (
          <input
            ref={inputRef}
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleSaveTitle}
            onKeyDown={handleKeyDown}
            onClick={(e) => e.stopPropagation()}
            className="flex-1 text-sm font-medium text-[var(--ink)] bg-white border-2 border-[var(--ink)] px-2 py-0.5 outline-none"
            maxLength={50}
          />
        ) : (
          <h4 className="text-sm font-medium text-[var(--ink)] truncate flex-1">
            {report.title}
          </h4>
        )}

        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {!isEditing && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsEditing(true);
              }}
              className="p-1 hover:bg-[var(--paper-dark)]"
              title="Edit title"
            >
              <PencilIcon className="w-3 h-3 text-[var(--slate)]" />
            </button>
          )}
          <button
            onClick={handleDelete}
            className={`p-1 transition-colors ${
              showDeleteConfirm
                ? "bg-red-100 hover:bg-red-200"
                : "hover:bg-[var(--paper-dark)]"
            }`}
            title={showDeleteConfirm ? "Click again to confirm" : "Delete"}
          >
            <TrashIcon
              className={`w-3 h-3 ${
                showDeleteConfirm ? "text-red-600" : "text-[var(--slate)]"
              }`}
            />
          </button>
        </div>
      </div>

      <p className="text-xs text-[var(--slate)] mt-1">
        {formatRelativeTime(report.createdAt)}
        {report.variantB?.linkedin && (
          <span className="ml-2 text-[var(--gold)] font-medium">A/B</span>
        )}
      </p>

      <p className="text-xs text-[var(--slate-light)] mt-1 line-clamp-2">
        {preview}...
      </p>
    </div>
  );
}
