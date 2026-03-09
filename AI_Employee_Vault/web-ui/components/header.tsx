"use client";

import ThemeToggle from "./theme-toggle";
import { useSidebarToggle } from "./layout-shell";

export default function Header({ title }: { title: string }) {
  const { toggle } = useSidebarToggle();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-[#0097A71A] bg-[#F5F7FA]/80 px-4 backdrop-blur sm:px-6 dark:border-[#00E5FF1A] dark:bg-[#0A0A0A]/80">
      <div className="flex items-center gap-3">
        {/* Hamburger menu - mobile only */}
        <button
          onClick={toggle}
          className="rounded-md p-2 text-[#555555] hover:bg-[#0097A70A] md:hidden dark:text-[#8899AA] dark:hover:bg-[#00E5FF0A]"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h2 className="text-lg font-semibold text-[#0A0A0A] dark:text-[#F0F0F0]">
          {title}
        </h2>
      </div>
      <div className="flex items-center gap-3">
        <ThemeToggle />
      </div>
    </header>
  );
}
