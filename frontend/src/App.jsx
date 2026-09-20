import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const stages = [
  {
    id: "project_manager",
    name: "Project Manager",
    icon: "📋",
  },
  {
    id: "architect",
    name: "Architect",
    icon: "🏗️",
  },
  {
    id: "developer",
    name: "Developer",
    icon: "💻",
  },
  {
    id: "filesystem",
    name: "File System",
    icon: "📁",
  },
  {
    id: "tester",
    name: "Tester",
    icon: "🧪",
  },
  {
    id: "debugger",
    name: "Debugger",
    icon: "🐞",
  },
  {
    id: "code_reviewer",
    name: "Code Reviewer",
    icon: "🔍",
  },
  {
    id: "documentation",
    name: "Documentation",
    icon: "📚",
  },
];

function App() {
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");

  const generateProject = async () => {
    if (!request.trim()) {
      setError("Please describe the software you want to build.");
      return;
    }

    setLoading(true);
    setError("");
    setResponse(null);

    try {
      const res = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          request: request.trim(),
        }),
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Generation failed.");
      }

      const data = await res.json();

      setResponse(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to connect to the DevTeam AI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetProject = () => {
    setResponse(null);
    setError("");
    setRequest("");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/15 text-xl ring-1 ring-blue-400/20">
              🤖
            </div>

            <div>
              <h1 className="text-lg font-bold tracking-tight sm:text-xl">
                DevTeam AI
              </h1>

              <p className="hidden text-xs text-slate-400 sm:block">
                Autonomous Software Development Team
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            <span className="text-xs font-medium text-emerald-300">
              Backend Online
            </span>
          </div>

        </div>
      </header>

      {/* Main */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">

        {/* Hero */}
        <section className="mx-auto max-w-4xl text-center">

          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-blue-400/20 bg-blue-400/10 px-4 py-2 text-xs font-medium text-blue-300">
            <span>⚡</span>
            Multi-Agent Autonomous Development
          </div>

          <h2 className="text-3xl font-black tracking-tight sm:text-5xl lg:text-6xl">
            Build software with an
            <span className="block bg-gradient-to-r from-blue-400 via-cyan-300 to-purple-400 bg-clip-text text-transparent">
              AI Development Team
            </span>
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
            Describe your software idea. DevTeam AI coordinates specialized
            AI agents to plan, architect, develop, test, debug, review and
            document your project.
          </p>

        </section>

        {/* Request Box */}
        <section className="mx-auto mt-10 max-w-4xl">

          <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-6">

            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold">
                  What do you want to build?
                </h3>

                <p className="mt-1 text-xs text-slate-500 sm:text-sm">
                  Describe the project in natural language.
                </p>
              </div>

              <span className="hidden rounded-lg bg-slate-800 px-2.5 py-1 text-xs text-slate-400 sm:block">
                AI
              </span>
            </div>

            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Example: Create a Python expense tracker with categories, monthly reports and unit tests..."
              rows={5}
              disabled={loading}
              className="w-full resize-none rounded-xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm leading-6 text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/10 disabled:cursor-not-allowed disabled:opacity-60"
            />

            {error && (
              <div className="mt-4 rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300">
                ⚠️ {error}
              </div>
            )}

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

              <span className="text-xs text-slate-500">
                {request.length} characters
              </span>

              <button
                onClick={generateProject}
                disabled={loading}
                className="w-full rounded-xl bg-blue-500 px-5 py-3 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Generating...
                  </span>
                ) : (
                  "🚀 Generate Project"
                )}
              </button>

            </div>
          </div>
        </section>

        {/* Pipeline */}
        <section className="mt-12">

          <div className="mb-5 flex items-end justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
                Development Pipeline
              </p>

              <h3 className="mt-1 text-xl font-bold sm:text-2xl">
                AI Agent Workflow
              </h3>
            </div>

            <span className="text-xs text-slate-500">
              8 Agents
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">

            {stages.map((stage, index) => (
              <div
                key={stage.id}
                className="relative rounded-xl border border-white/10 bg-white/[0.025] p-4 text-center transition hover:-translate-y-1 hover:border-blue-400/30 hover:bg-white/[0.05]"
              >
                <div className="text-2xl">
                  {stage.icon}
                </div>

                <p className="mt-2 text-xs font-medium text-slate-300">
                  {stage.name}
                </p>

                <span className="mt-2 block text-[10px] text-slate-600">
                  {String(index + 1).padStart(2, "0")}
                </span>
              </div>
            ))}

          </div>
        </section>

        {/* Result */}
        {response && (
          <ProjectResult
            response={response}
            onReset={resetProject}
          />
        )}

        {/* Empty state */}
        {!response && !loading && (
          <section className="mt-12 rounded-2xl border border-dashed border-white/10 p-8 text-center sm:p-12">
            <div className="text-4xl">🧠</div>

            <h3 className="mt-4 text-lg font-semibold">
              Ready to build
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              Enter a software requirement above and let the AI development
              team handle the engineering workflow.
            </p>
          </section>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-6">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 text-center text-xs text-slate-600 sm:flex-row sm:px-6 lg:px-8">
          <span>
            DevTeam AI • Multi-Agent Software Engineering
          </span>

          <span>
            React + Tailwind + FastAPI + LangGraph
          </span>
        </div>
      </footer>

    </div>
  );
}


function ProjectResult({ response, onReset }) {
  const testResults = response.test_results || {};
  const testSuite = testResults.test_suite || {};
  const review = response.review || {};

  return (
    <section className="mt-12 space-y-6">

      {/* Result Header */}
      <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/[0.04] p-5 sm:p-6">

        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">

          <div>
            <div className="flex items-center gap-2 text-emerald-400">
              <span>✓</span>
              <span className="text-sm font-semibold">
                Project Generated Successfully
              </span>
            </div>

            <h3 className="mt-2 text-xl font-bold sm:text-2xl">
              {response.user_request}
            </h3>
          </div>

          <button
            onClick={onReset}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/5"
          >
            New Project
          </button>

        </div>

        {/* Project ID */}
        <div className="mt-5 rounded-xl bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Project ID
          </p>

          <p className="mt-1 break-all font-mono text-sm text-blue-300">
            {response.project_id}
          </p>
        </div>

      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">

        <StatCard
          label="Generated Files"
          value={response.generated_files?.length || 0}
          icon="📁"
        />

        <StatCard
          label="Tests Passed"
          value={testSuite.passed ?? 0}
          icon="🧪"
        />

        <StatCard
          label="Tests Failed"
          value={testSuite.failed ?? 0}
          icon="❌"
        />

        <StatCard
          label="Debug Attempts"
          value={response.debug_attempts ?? 0}
          icon="🐞"
        />

      </div>

      {/* Two-column section */}
      <div className="grid gap-6 lg:grid-cols-2">

        {/* Files */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">

          <div className="mb-4">
            <h3 className="font-bold">
              Generated Files
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Files created by the development team.
            </p>
          </div>

          <div className="space-y-2">
            {(response.generated_files || []).map((file) => (
              <div
                key={file}
                className="flex items-center gap-3 rounded-lg border border-white/5 bg-slate-950/50 px-3 py-2.5"
              >
                <span>📄</span>

                <span className="min-w-0 break-all font-mono text-xs text-slate-300">
                  {file}
                </span>
              </div>
            ))}
          </div>

        </div>

        {/* Tests */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">

          <div className="mb-4">
            <h3 className="font-bold">
              Test Results
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Automated verification of the generated project.
            </p>
          </div>

          <div
            className={`rounded-xl border p-4 ${
              testSuite.status === "passed"
                ? "border-emerald-400/20 bg-emerald-400/10"
                : "border-red-400/20 bg-red-400/10"
            }`}
          >
            <div className="flex items-center justify-between">

              <span className="text-sm font-medium">
                Test Suite
              </span>

              <span
                className={
                  testSuite.status === "passed"
                    ? "text-emerald-400"
                    : "text-red-400"
                }
              >
                {testSuite.status === "passed"
                  ? "PASSED"
                  : "FAILED"}
              </span>

            </div>

            <div className="mt-4 grid grid-cols-3 gap-2">

              <MiniStat
                label="Passed"
                value={testSuite.passed ?? 0}
              />

              <MiniStat
                label="Failed"
                value={testSuite.failed ?? 0}
              />

              <MiniStat
                label="Errors"
                value={testSuite.errors ?? 0}
              />

            </div>
          </div>

        </div>

      </div>

      {/* Review */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 sm:p-6">

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

          <div>
            <p className="text-xs uppercase tracking-wider text-purple-400">
              Code Review
            </p>

            <h3 className="mt-1 text-lg font-bold">
              AI Code Reviewer
            </h3>
          </div>

          <div
            className={`rounded-full px-4 py-2 text-xs font-bold ${
              review.overall_status === "approved"
                ? "bg-emerald-400/10 text-emerald-400"
                : "bg-red-400/10 text-red-400"
            }`}
          >
            {review.overall_status || "UNKNOWN"}
          </div>

        </div>

        <p className="mt-4 text-sm leading-6 text-slate-400">
          {review.summary || "No review summary available."}
        </p>

        {review.suggestions?.length > 0 && (
          <div className="mt-5">

            <p className="mb-2 text-sm font-semibold">
              Suggestions
            </p>

            <div className="space-y-2">
              {review.suggestions.map(
                (suggestion, index) => (
                  <div
                    key={index}
                    className="rounded-lg bg-slate-950/50 px-3 py-2.5 text-xs leading-5 text-slate-400"
                  >
                    💡 {suggestion}
                  </div>
                )
              )}
            </div>

          </div>
        )}

      </div>

      {/* Requirements */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 sm:p-6">

        <h3 className="font-bold">
          Requirements
        </h3>

        <div className="mt-4 grid gap-2 sm:grid-cols-2">

          {(response.requirements || []).map(
            (requirement, index) => (
              <div
                key={index}
                className="flex gap-3 rounded-lg bg-slate-950/50 p-3"
              >
                <span className="text-blue-400">
                  {index + 1}.
                </span>

                <span className="text-xs leading-5 text-slate-400">
                  {requirement}
                </span>
              </div>
            )
          )}

        </div>

      </div>

    </section>
  );
}


function StatCard({ label, value, icon }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4">
      <div className="text-xl">
        {icon}
      </div>

      <p className="mt-3 text-2xl font-black">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {label}
      </p>
    </div>
  );
}


function MiniStat({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-950/60 p-3 text-center">
      <p className="text-lg font-bold">
        {value}
      </p>

      <p className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">
        {label}
      </p>
    </div>
  );
}


export default App;