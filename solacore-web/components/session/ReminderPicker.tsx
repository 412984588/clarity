"use client";

import { useState } from "react";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Bell, X } from "lucide-react";
import { format } from "date-fns";

interface ReminderPickerProps {
  value: Date | null;
  onChange: (date: Date | null) => void;
}

export function ReminderPicker({ value, onChange }: ReminderPickerProps) {
  const [date, setDate] = useState<Date | undefined>(value || undefined);
  const [time, setTime] = useState(value ? format(value, "HH:mm") : "09:00");
  const [open, setOpen] = useState(false);

  const handleSave = () => {
    if (date) {
      const [hours, minutes] = time.split(":").map(Number);
      const reminderDate = new Date(date);
      reminderDate.setHours(hours, minutes, 0, 0);
      onChange(reminderDate);
      setOpen(false);
    }
  };

  const handleClear = () => {
    setDate(undefined);
    setTime("09:00");
    onChange(null);
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          <Bell className="mr-2 h-4 w-4" />
          {value ? format(value, "PPp") : "设置提醒"}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-3 space-y-3">
          <Calendar
            mode="single"
            selected={date}
            onSelect={setDate}
            disabled={(date) => date < new Date()}
          />
          <div className="flex gap-2">
            <Input
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSave} size="sm" disabled={!date}>
              保存
            </Button>
            {value && (
              <Button onClick={handleClear} size="sm" variant="ghost">
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
}
