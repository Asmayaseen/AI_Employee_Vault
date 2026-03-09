"use client";

import { useEffect, useState } from "react";
import Header from "@/components/header";
import { getVaultSummary, getVaultFolder, getVaultFile, type VaultFile } from "@/lib/api";

const FOLDERS = [
  "Inbox",
  "Needs_Action",
  "Plans",
  "Pending_Approval",
  "Approved",
  "Rejected",
  "Done",
  "Logs",
  "Briefings",
  "Accounting",
  "Queued_Actions",
];

export default function VaultPage() {
  const [summary, setSummary] = useState<Record<string, number>>({});
  const [activeFolder, setActiveFolder] = useState<string | null>(null);
  const [files, setFiles] = useState<VaultFile[]>([]);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getVaultSummary()
      .then((data) => {
        setSummary(data.summary);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  async function openFolder(folder: string) {
    setActiveFolder(folder);
    setFileContent(null);
    setSelectedFile(null);
    try {
      const data = await getVaultFolder(folder);
      setFiles(data.files);
    } catch {
      setFiles([]);
    }
  }

  async function openFile(folder: string, filename: string) {
    setSelectedFile(filename);
    try {
      const data = await getVaultFile(`${folder}/${filename}`);
      setFileContent(data.content);
    } catch {
      setFileContent("Error loading file content");
    }
  }

  return (
    <>
      <Header title="Vault Browser" />
      <div className="p-4 sm:p-6">
        {loading ? (
          <div className="flex items-center justify-center p-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-[#0097A7] border-t-transparent dark:border-[#00E5FF] dark:border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Folder List */}
            <div>
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                Folders
              </h3>
              <div className="space-y-1">
                {FOLDERS.map((folder) => (
                  <button
                    key={folder}
                    onClick={() => openFolder(folder)}
                    className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm transition ${
                      activeFolder === folder
                        ? "bg-[#0097A715] text-[#0097A7] dark:bg-[#00E5FF15] dark:text-[#00E5FF]"
                        : "text-[#555555] hover:bg-[#0097A70A] dark:text-[#8899AA] dark:hover:bg-[#00E5FF0A]"
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                      </svg>
                      {folder}
                    </span>
                    <span className="rounded-full bg-[#0097A715] px-2 py-0.5 text-xs font-medium text-[#0097A7] dark:bg-[#00E5FF15] dark:text-[#00E5FF]">
                      {summary[folder] ?? 0}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* File List */}
            <div>
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                {activeFolder ? `${activeFolder} (${files.length})` : "Select a folder"}
              </h3>
              {activeFolder && (
                <div className="space-y-1">
                  {files.length === 0 ? (
                    <p className="text-sm text-[#555555] dark:text-[#8899AA]">Empty folder</p>
                  ) : (
                    files.map((file) => (
                      <button
                        key={file.filename}
                        onClick={() => openFile(activeFolder, file.filename)}
                        className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                          selectedFile === file.filename
                            ? "bg-[#0097A715] text-[#0097A7] dark:bg-[#00E5FF15] dark:text-[#00E5FF]"
                            : "text-[#555555] hover:bg-[#0097A70A] dark:text-[#8899AA] dark:hover:bg-[#00E5FF0A]"
                        }`}
                      >
                        <p className="truncate font-medium">{file.filename}</p>
                        <p className="text-xs text-[#888888] dark:text-[#667788]">
                          {(file.size / 1024).toFixed(1)} KB &middot;{" "}
                          {new Date(file.modified).toLocaleDateString()}
                        </p>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>

            {/* File Content */}
            <div>
              <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[#555555] dark:text-[#8899AA]">
                {selectedFile || "Select a file"}
              </h3>
              {fileContent !== null && (
                <pre className="card max-h-[70vh] overflow-auto whitespace-pre-wrap text-xs text-[#333333] dark:text-[#AABBCC]">
                  {fileContent}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
