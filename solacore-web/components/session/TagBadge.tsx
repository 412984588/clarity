"use client";

import { X } from "lucide-react";

interface TagBadgeProps {
  tag: string;
  onRemove?: () => void;
  variant?: "default" | "outline";
}

export function TagBadge({
  tag,
  onRemove,
  variant = "default",
}: TagBadgeProps) {
  const baseClasses =
    "inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium transition-colors";
  const variantClasses = {
    default: "bg-blue-100 text-blue-800 hover:bg-blue-200",
    outline: "border border-gray-300 text-gray-700 hover:bg-gray-50",
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]}`}>
      {tag}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-1 hover:bg-blue-300 rounded-full p-0.5 transition-colors"
          aria-label={`Remove tag ${tag}`}
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </span>
  );
}
