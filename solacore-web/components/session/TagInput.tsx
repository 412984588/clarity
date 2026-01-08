"use client";

import { useState, KeyboardEvent } from "react";
import { TagBadge } from "./TagBadge";
import { Plus } from "lucide-react";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  maxTags?: number;
}

export function TagInput({
  value = [],
  onChange,
  placeholder = "添加标签...",
  maxTags = 10,
}: TagInputProps) {
  const [inputValue, setInputValue] = useState("");
  const [isInputVisible, setIsInputVisible] = useState(false);

  const handleAddTag = () => {
    const trimmedValue = inputValue.trim();
    if (!trimmedValue) return;
    if (value.includes(trimmedValue)) {
      setInputValue("");
      return;
    }
    if (value.length >= maxTags) {
      alert(`最多只能添加 ${maxTags} 个标签`);
      return;
    }

    onChange([...value, trimmedValue]);
    setInputValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    } else if (e.key === "Escape") {
      setInputValue("");
      setIsInputVisible(false);
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2 items-center">
        {value.map((tag) => (
          <TagBadge key={tag} tag={tag} onRemove={() => handleRemoveTag(tag)} />
        ))}

        {isInputVisible ? (
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => {
              if (!inputValue.trim()) {
                setIsInputVisible(false);
              }
            }}
            placeholder={placeholder}
            className="px-2 py-1 text-xs border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[120px]"
            autoFocus
            maxLength={50}
          />
        ) : (
          <button
            type="button"
            onClick={() => setIsInputVisible(true)}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs text-gray-600 border border-dashed border-gray-300 rounded-full hover:bg-gray-50 hover:border-gray-400 transition-colors"
          >
            <Plus className="w-3 h-3" />
            添加标签
          </button>
        )}
      </div>

      {value.length > 0 && (
        <p className="text-xs text-gray-500">
          {value.length} / {maxTags} 个标签
        </p>
      )}
    </div>
  );
}
