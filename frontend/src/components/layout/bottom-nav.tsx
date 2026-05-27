"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Home, BookOpen, PenTool, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { BOTTOM_NAV_TABS } from "@/lib/constants";

const iconMap = {
  "/home": Home,
  "/courses": BookOpen,
  "/practice": PenTool,
  "/settings": User,
} as const;

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-surface border-t border-border safe-area-inset-bottom">
      <div className="flex items-center justify-around h-16 px-2">
        {BOTTOM_NAV_TABS.map((tab) => {
          const Icon = iconMap[tab.href as keyof typeof iconMap];
          const isActive = pathname === tab.href || pathname.startsWith(tab.href + "/");

          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "flex flex-col items-center justify-center gap-1 px-4 py-2 rounded-lg transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {Icon && (
                <Icon
                  className={cn(
                    "h-5 w-5 transition-transform",
                    isActive && "scale-110"
                  )}
                  strokeWidth={isActive ? 2.5 : 2}
                />
              )}
              <span className="text-xs font-medium">{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
