"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Bell } from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar } from "@/components/ui/avatar";

interface HeaderProps {
  title: string;
  showBack?: boolean;
  showNotification?: boolean;
  showAvatar?: boolean;
  avatarSrc?: string;
  avatarAlt?: string;
  xp?: number;
  streak?: number;
  className?: string;
}

export function Header({
  title,
  showBack = false,
  showNotification = false,
  showAvatar = true,
  avatarSrc,
  avatarAlt = "",
  xp,
  streak,
  className,
}: HeaderProps) {
  const router = useRouter();

  return (
    <header
      className={cn(
        "sticky top-0 z-40 bg-surface/95 backdrop-blur-sm border-b border-border",
        className
      )}
    >
      <div className="flex items-center justify-between h-14 px-4">
        <div className="flex items-center gap-3">
          {showBack && (
            <button
              onClick={() => router.back()}
              className="flex items-center justify-center h-9 w-9 rounded-full hover:bg-surface-muted transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
          )}
          <h1 className="text-lg font-semibold text-foreground truncate">
            {title}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          {(xp !== undefined || streak !== undefined) && (
            <div className="hidden sm:flex items-center gap-3 text-sm">
              {xp !== undefined && (
                <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-accent-light text-accent">
                  <span className="font-medium">{xp}</span>
                  <span className="text-xs">XP</span>
                </div>
              )}
              {streak !== undefined && streak > 0 && (
                <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-secondary-light text-secondary">
                  <span className="text-xs">🔥</span>
                  <span className="font-medium">{streak}</span>
                </div>
              )}
            </div>
          )}

          {showNotification && (
            <button
              className="relative flex items-center justify-center h-9 w-9 rounded-full hover:bg-surface-muted transition-colors"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-danger" />
            </button>
          )}

          {showAvatar && (
            <Avatar
              src={avatarSrc}
              alt={avatarAlt}
              size="sm"
              className="cursor-pointer"
            />
          )}
        </div>
      </div>
    </header>
  );
}
