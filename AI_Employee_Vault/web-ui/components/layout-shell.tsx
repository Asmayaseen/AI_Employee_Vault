"use client";

import { useState, useCallback, createContext, useContext } from "react";
import Sidebar from "./sidebar";

interface SidebarContextValue {
  toggle: () => void;
}

const SidebarContext = createContext<SidebarContextValue>({ toggle: () => {} });

export function useSidebarToggle() {
  return useContext(SidebarContext);
}

export default function LayoutShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggle = useCallback(() => setSidebarOpen((prev) => !prev), []);
  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

  return (
    <SidebarContext.Provider value={{ toggle }}>
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      {/* Overlay backdrop for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={closeSidebar}
        />
      )}
      <main className="min-h-screen md:ml-64">{children}</main>
    </SidebarContext.Provider>
  );
}
