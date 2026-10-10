
"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

type RepositoryFile = {
  path: string;
  extension: string;
  size_bytes: number;
};

type FilesResponse = {
  repository: string;
  file_count: number;
  files: RepositoryFile[];
};

type GraphResponse = {
  repository: string;
  node_count: number;
  edge_count: number;
  graph: {
    nodes?: unknown[];
    edges?: unknown[];
    [key: string]: unknown;
  };
};

export default function DashboardPage() {
  const router = useRouter();

  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [files, setFiles] = useState<FilesResponse | null>(null);
  const [graph, setGraph] = useState<GraphResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [cloning, setCloning] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadRepository = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [filesResponse, graphResponse] = await Promise.all([
        fetch(`${API_URL}/repositories/files`),
        fetch(`${API_URL}/repositories/graph`),
      ]);

      if (!filesResponse.ok || !graphResponse.ok) {
        throw new Error(
          "Unable to load repository data. Check that the backend is running and a repository is available.",
        );
      }

      const [filesData, graphData] = await Promise.all([
        filesResponse.json(),
        graphResponse.json(),
      ]);

      setFiles(filesData);
      setGraph(graphData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "An unexpected error occurred while loading the repository.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRepository();
  }, [loadRepository]);

  async function handleClone(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCloning(true);
    setError("");
    setNotice("");

    try {
      const response = await fetch(`${API_URL}/repositories/clone`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repository_url: repositoryUrl.trim() }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          typeof data?.detail === "string"
            ? data.detail
            : "Repository cloning failed.",
        );
      }

      setNotice("Repository cloned successfully.");
      setRepositoryUrl("");
      await loadRepository();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to clone the repository.",
      );
    } finally {
      setCloning(false);
    }
  }

  async function handleSignOut() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  return (
    <main className="min-h-screen bg-[#F5F4EF] text-[#111111]">
      <nav className="flex items-center justify-between border-b-2 border-black bg-white px-5 py-4 sm:px-8">
        <a href="/dashboard" className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center border-2 border-black bg-[#E8FF55] font-mono text-lg font-bold">
            C
          </span>
          <span className="font-extrabold tracking-tight">
            CODEGRAPH<span className="text-[#2563EB]">.</span>
          </span>
        </a>

        <div className="flex items-center gap-3">
          <span className="hidden font-mono text-xs uppercase tracking-wider text-[#686868] sm:block">
            Developer workspace
          </span>
          <button
            onClick={handleSignOut}
            className="border-2 border-black px-3 py-2 text-sm font-bold transition hover:bg-[#F5F4EF]"
          >
            Sign out
          </button>
        </div>
      </nav>

      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8 sm:py-12">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="mb-3 font-mono text-xs font-bold uppercase tracking-[0.2em] text-[#686868]">
              Repository intelligence / 001
            </p>
            <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl">
              Your workspace.
            </h1>
            <p className="mt-3 max-w-xl leading-7 text-[#686868]">
              Explore source files, map dependencies, and understand the
              structure behind your code.
            </p>
          </div>

          <button
            onClick={() => void loadRepository()}
            disabled={loading}
            className="border-2 border-black bg-white px-4 py-3 text-sm font-bold hover:bg-[#E8FF55] disabled:opacity-50"
          >
            {loading ? "Refreshing..." : "Refresh data ↻"}
          </button>
        </div>

        <section className="mt-9 border-2 border-black bg-white p-5 shadow-[4px_4px_0_#111111] sm:p-7">
          <div className="flex items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center border-2 border-black bg-[#E8FF55] font-mono font-bold">
              +
            </span>
            <div>
              <h2 className="text-xl font-extrabold">Connect a repository</h2>
              <p className="mt-1 text-sm leading-6 text-[#686868]">
                Enter a Git repository URL to clone it into the backend
                workspace.
              </p>
            </div>
          </div>

          <form
            onSubmit={handleClone}
            className="mt-5 flex flex-col gap-3 sm:flex-row"
          >
            <input
              type="url"
              required
              value={repositoryUrl}
              onChange={(event) => setRepositoryUrl(event.target.value)}
              placeholder="https://github.com/owner/repository"
              aria-label="Git repository URL"
              className="min-w-0 flex-1 border-2 border-black bg-white px-4 py-3 text-sm outline-none focus:border-[#2563EB]"
            />
            <button
              type="submit"
              disabled={cloning}
              className="border-2 border-black bg-[#E8FF55] px-6 py-3 text-sm font-extrabold hover:bg-[#d9f044] disabled:opacity-50"
            >
              {cloning ? "Cloning..." : "Clone repository →"}
            </button>
          </form>

          <p className="mt-3 font-mono text-xs text-[#686868]">
            The backend currently uses one workspace location for cloned
            repositories.
          </p>
        </section>

        {error && (
          <div
            role="alert"
            className="mt-6 border-2 border-[#DC2626] bg-white p-4 text-sm leading-6"
          >
            <strong className="block">Something went wrong</strong>
            <span>{error}</span>
          </div>
        )}

        {notice && (
          <div
            role="status"
            className="mt-6 border-2 border-black bg-[#E8FF55] p-4 text-sm font-bold"
          >
            {notice}
          </div>
        )}

        <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <MetricCard
            label="Source files"
            value={loading ? "—" : String(files?.file_count ?? 0)}
            detail="Discovered by the backend"
          />
          <MetricCard
            label="Graph nodes"
            value={loading ? "—" : String(graph?.node_count ?? 0)}
            detail="Repository structure"
          />
          <MetricCard
            label="Graph edges"
            value={loading ? "—" : String(graph?.edge_count ?? 0)}
            detail="Recorded relationships"
          />
        </section>

        <section className="mt-8 border-2 border-black bg-white">
          <div className="flex flex-col justify-between gap-2 border-b-2 border-black px-5 py-4 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-lg font-extrabold">Source files</h2>
              <p className="mt-1 text-sm text-[#686868]">
                {files?.repository ?? "Repository workspace"}
              </p>
            </div>
            <span className="w-fit border border-black bg-[#F5F4EF] px-3 py-1 font-mono text-xs">
              {loading ? "Loading" : `${files?.file_count ?? 0} FILES`}
            </span>
          </div>

          {loading ? (
            <p className="p-6 text-sm text-[#686868]">
              Loading repository data...
            </p>
          ) : files?.files.length ? (
            <div className="max-h-[460px] overflow-auto">
              {files.files.map((file) => (
                <div
                  key={file.path}
                  className="flex items-center justify-between gap-4 border-b border-[#E4E3DE] px-5 py-3 last:border-b-0 hover:bg-[#F5F4EF]"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center border border-black font-mono text-[10px] font-bold">
                      {file.extension.replace(".", "").slice(0, 4) || "FILE"}
                    </span>
                    <span className="truncate font-mono text-xs sm:text-sm">
                      {file.path.replace(/\\/g, "/")}
                    </span>
                  </div>
                  <span className="shrink-0 font-mono text-xs text-[#686868]">
                    {formatBytes(file.size_bytes)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="p-6 text-sm text-[#686868]">
              No source files were returned. Connect a repository or refresh
              the data.
            </p>
          )}
        </section>

        <footer className="mt-8 border-t-2 border-black py-5 font-mono text-xs text-[#686868]">
          CODEGRAPH / UNDERSTAND → EXPLAIN → VERIFY
        </footer>
      </div>
    </main>
  );
}

function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="border-2 border-black bg-white p-5 shadow-[4px_4px_0_#111111]">
      <p className="font-mono text-xs font-bold uppercase tracking-wider text-[#686868]">
        {label}
      </p>
      <p className="mt-3 text-4xl font-extrabold tracking-tight">{value}</p>
      <p className="mt-2 text-sm text-[#686868]">{detail}</p>
    </div>
  );
}

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
