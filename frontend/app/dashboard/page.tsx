"use client";

import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export default function DashboardPage() {
  const router = useRouter();

  async function handleSignOut() {
    const supabase = createClient();

    await supabase.auth.signOut();

    router.push("/");
    router.refresh();
  }

  return (
    <main className="min-h-screen bg-[#050507] text-white">
      <nav className="flex items-center justify-between border-b border-white/10 px-8 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white font-bold text-black">
            C
          </div>

          <span className="font-semibold">
            CodeGraph
          </span>
        </div>

        <button
          onClick={handleSignOut}
          className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
        >
          Sign out
        </button>
      </nav>

      <div className="flex min-h-[calc(100vh-73px)] items-center justify-center">
        <div className="text-center">
          <p className="mb-3 text-sm font-medium uppercase tracking-[0.25em] text-violet-400">
            CodeGraph
          </p>

          <h1 className="text-4xl font-semibold tracking-tight">
            Your workspace
          </h1>

          <p className="mt-4 text-white/40">
            Repository intelligence starts here.
          </p>
        </div>
      </div>
    </main>
  );
}