
"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function HomePage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const supabase = createClient();

  async function handleEmailAuth(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: `${window.location.origin}/auth/callback`,
          },
        });

        if (error) {
          setMessage(error.message);
        } else {
          setMessage("Check your email to confirm your account.");
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          setMessage(error.message);
        } else {
          window.location.href = "/dashboard";
        }
      }
    } catch {
      setMessage("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleGitHub() {
    setLoading(true);
    setMessage("");

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "github",
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: { prompt: "consent" },
        },
      });

      if (error) {
        setMessage(error.message);
      }
    } catch {
      setMessage("Unable to connect to GitHub. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#F5F4EF] text-[#111111]">
      <header className="flex items-center justify-between border-b-2 border-black px-6 py-5 sm:px-10">
        <a href="/" className="flex items-center gap-3" aria-label="CodeGraph home">
          <span className="flex h-9 w-9 items-center justify-center border-2 border-black bg-[#E8FF55] font-mono text-lg font-bold">
            C
          </span>
          <span className="text-lg font-extrabold tracking-tight">
            CODEGRAPH<span className="text-[#2563EB]">.</span>
          </span>
        </a>

        <span className="hidden font-mono text-xs uppercase tracking-widest text-[#686868] sm:block">
          AI software intelligence
        </span>
      </header>

      <div className="mx-auto grid min-h-[calc(100vh-78px)] max-w-[1440px] lg:grid-cols-2">
        {/* Product introduction */}
        <section className="flex flex-col justify-center border-b-2 border-black px-6 py-12 sm:px-10 lg:border-b-0 lg:border-r-2 lg:px-14 lg:py-16">
          <div className="mb-6 flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-[#16A34A]" />
            <span className="font-mono text-xs font-bold uppercase tracking-[0.18em]">
              Repository intelligence
            </span>
          </div>

          <h1 className="max-w-xl text-4xl font-extrabold leading-[1.05] tracking-tight sm:text-5xl xl:text-6xl">
            Your codebase.
            <br />
            <span className="underline decoration-[#E8FF55] decoration-[10px] underline-offset-[-3px]">
              Fully understood.
            </span>
          </h1>

          <p className="mt-6 max-w-lg text-base leading-7 text-[#555555] sm:text-lg">
            Map dependencies, trace function calls, understand change impact,
            and verify proposed code changes with evidence.
          </p>

          {/* Illustrative graph preview */}
          <div className="mt-10 max-w-xl border-2 border-black bg-white shadow-[5px_5px_0_#111111]">
            <div className="flex items-center justify-between border-b-2 border-black px-4 py-3">
              <span className="font-mono text-xs font-bold uppercase tracking-wider">
                Architecture / overview
              </span>
              <span className="bg-[#E8FF55] px-2 py-1 font-mono text-[10px] font-bold">
                PREVIEW
              </span>
            </div>

            <div className="terminal-surface overflow-hidden p-4 sm:p-6">
              <div className="mb-5 flex items-center gap-2 font-mono text-xs text-white/50">
                <span className="text-[#E8FF55]">●</span>
                repository / src
              </div>

              <div className="grid grid-cols-[1fr_24px_1fr] items-center gap-y-4 font-mono text-xs sm:grid-cols-[1fr_40px_1fr]">
                <div className="border border-white/30 p-3 text-center">
                  <span className="text-[#E8FF55]">module</span>
                  <div className="mt-1 text-white">main.py</div>
                </div>

                <div className="text-center text-[#E8FF55]">→</div>

                <div className="border border-[#2563EB] p-3 text-center">
                  <span className="text-blue-300">service</span>
                  <div className="mt-1 text-white">graph.py</div>
                </div>

                <div className="col-span-3 flex justify-center text-[#E8FF55]">
                  <span>↓ dependency trace ↓</span>
                </div>

                <div className="col-span-3 mx-auto w-3/4 border border-[#16A34A] p-3 text-center">
                  <span className="text-green-300">verification</span>
                  <div className="mt-1 text-white">Evidence-backed changes</div>
                </div>
              </div>

              <div className="mt-6 border-t border-white/20 pt-3 font-mono text-[11px] text-white/50">
                <span className="text-[#E8FF55]">&gt;</span>{" "}
                Understand → Explain → Verify
              </div>
            </div>
          </div>

          <p className="mt-8 font-mono text-xs text-[#686868]">
            BUILT FOR DEVELOPERS WHO WANT TO KNOW WHY.
          </p>
        </section>

        {/* Authentication */}
        <section className="flex items-center justify-center px-6 py-12 sm:px-10 lg:px-14">
          <div className="w-full max-w-md">
            <div className="mb-8">
              <p className="mb-3 font-mono text-xs font-bold uppercase tracking-[0.2em] text-[#686868]">
                {isSignUp ? "Create workspace access" : "Developer access"}
              </p>

              <h2 className="text-3xl font-extrabold tracking-tight sm:text-4xl">
                {isSignUp ? "Create your account." : "Welcome back."}
              </h2>

              <p className="mt-3 text-sm leading-6 text-[#686868]">
                {isSignUp
                  ? "Start exploring your codebase with CodeGraph."
                  : "Sign in to continue understanding your codebase."}
              </p>
            </div>

            <div className="border-2 border-black bg-white p-5 shadow-[5px_5px_0_#111111] sm:p-7">
              <button
                type="button"
                onClick={handleGitHub}
                disabled={loading}
                className="flex w-full items-center justify-center gap-3 border-2 border-black bg-white px-4 py-3.5 text-sm font-bold transition hover:bg-[#F5F4EF] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.57.1.78-.25.78-.55v-2.13c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.69-1.28-1.69-1.05-.72.08-.71.08-.71 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.23-1.28-5.23-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.47.11-3.06 0 0 .97-.31 3.18 1.18A11.1 11.1 0 0 1 12 8.08c.98 0 1.96.13 2.88.39 2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.77.12 3.06.74.81 1.18 1.84 1.18 3.1 0 4.43-2.69 5.4-5.25 5.69.41.35.78 1.04.78 2.1v3.11c0 .3.21.66.79.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
                </svg>
                Continue with GitHub
              </button>

              <div className="my-6 flex items-center gap-4">
                <div className="h-px flex-1 bg-[#D4D4D0]" />
                <span className="font-mono text-[10px] font-bold text-[#686868]">
                  OR EMAIL
                </span>
                <div className="h-px flex-1 bg-[#D4D4D0]" />
              </div>

              <form onSubmit={handleEmailAuth} className="space-y-5">
                <div>
                  <label
                    htmlFor="email"
                    className="mb-2 block text-xs font-bold"
                  >
                    Email address
                  </label>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full border-2 border-[#111111] bg-white px-4 py-3 text-sm outline-none placeholder:text-[#999999] focus:border-[#2563EB]"
                  />
                </div>

                <div>
                  <label
                    htmlFor="password"
                    className="mb-2 block text-xs font-bold"
                  >
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    autoComplete={isSignUp ? "new-password" : "current-password"}
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full border-2 border-[#111111] bg-white px-4 py-3 text-sm outline-none placeholder:text-[#999999] focus:border-[#2563EB]"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full border-2 border-black bg-[#E8FF55] px-4 py-3.5 text-sm font-extrabold transition hover:bg-[#d9f044] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Please wait..."
                    : isSignUp
                      ? "Create account →"
                      : "Sign in →"}
                </button>
              </form>

              {message && (
                <p
                  role="status"
                  aria-live="polite"
                  className="mt-5 border-2 border-black bg-[#F5F4EF] p-3 text-sm leading-5"
                >
                  {message}
                </p>
              )}

              <div className="mt-6 border-t border-[#D4D4D0] pt-5 text-center text-sm text-[#686868]">
                {isSignUp
                  ? "Already have an account?"
                  : "New to CodeGraph?"}{" "}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(!isSignUp);
                    setMessage("");
                  }}
                  className="font-bold text-[#111111] underline decoration-2 underline-offset-4 hover:decoration-[#2563EB]"
                >
                  {isSignUp ? "Sign in" : "Create an account"}
                </button>
              </div>
            </div>

            <p className="mt-6 text-center font-mono text-[10px] uppercase tracking-wider text-[#777777]">
              CodeGraph / AI software intelligence
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
