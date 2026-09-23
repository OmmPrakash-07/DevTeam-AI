import { useEffect, useRef, useState } from "react";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function apiEndpoint(path) {
  return new URL(
    `${API_URL.replace(/\/+$/, "")}${path}`,
    window.location.href
  );
}

async function fetchRecentProjects(signal) {
  const response = await fetch(apiEndpoint("/projects"), { signal });
  if (!response.ok) throw new Error("Recent projects could not be loaded.");

  const data = await response.json();
  if (!Array.isArray(data.projects)) throw new Error("Recent projects response was invalid.");
  return data.projects;
}

function formatProjectDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Date unavailable"
    : date.toLocaleDateString(undefined, {
      day: "numeric",
      month: "short",
      year: "numeric",
  });
}

function formatProjectStatus(value) {
  if (!value) return "Not available";
  return value.replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

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

const activityStatusStyles = {
  completed: {
    icon: "✓",
    label: "Completed",
    className: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
  },
  running: {
    icon: "◌",
    label: "Running",
    className: "border-blue-400/20 bg-blue-400/10 text-blue-300",
  },
  failed: {
    icon: "✕",
    label: "Failed",
    className: "border-red-400/20 bg-red-400/10 text-red-300",
  },
  pending: {
    icon: "·",
    label: "Pending",
    className: "border-white/5 bg-slate-950/40 text-slate-500",
  },
};

function getActivityLabel(event) {
  const name = event.display_name ||
    stages.find((stage) => stage.id === event.agent_name)?.name ||
    event.agent_name ||
    "Agent";

  return event.attempt_number != null
    ? `${name} — Attempt ${event.attempt_number}`
    : name;
}

function LiveAgentActivity({ activityHistory = [], currentActiveAgent }) {
  const latestByAgent = {};
  activityHistory.forEach((event) => {
    if (event?.agent_name) latestByAgent[event.agent_name] = event;
  });

  const activeStage = stages.find((stage) => stage.id === currentActiveAgent);
  const activeName = activeStage?.name || currentActiveAgent;

  return (
    <section className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 sm:p-6">
      <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">
            Workflow Activity
          </p>
          <h3 className="mt-1 text-xl font-bold">Live Agent Activity</h3>
        </div>
        {activeName && (
          <p className="text-xs text-blue-300">
            Current agent: <span className="font-semibold">{activeName}</span>
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {stages.map((stage) => {
          const event = latestByAgent[stage.id];
          const status = activityStatusStyles[event?.status] ? event.status : "pending";
          const style = activityStatusStyles[status];
          return (
            <div key={stage.id} className={`rounded-xl border p-3 ${style.className}`}>
              <div className="flex items-center gap-2">
                <span className="text-lg" aria-label={style.label}>{style.icon}</span>
                <span className="text-xs font-medium">{stage.name}</span>
              </div>
              <p className="mt-1 text-[10px] opacity-75">{style.label}</p>
            </div>
          );
        })}
      </div>

      {activityHistory.length > 0 ? (
        <ol className="mt-5 space-y-2">
          {activityHistory.map((event, index) => {
            const status = activityStatusStyles[event?.status] ? event.status : "pending";
            const style = activityStatusStyles[status];
            return (
              <li key={`${event.agent_name || "activity"}-${event.timestamp || index}-${index}`}
                className="flex items-start gap-3 rounded-lg bg-slate-950/50 px-3 py-2.5">
                <span className={`mt-0.5 w-5 shrink-0 text-center ${style.className.split(" ").at(-1)}`}>
                  {style.icon}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-slate-200">
                    {getActivityLabel(event)}
                  </p>
                  {event.message && (
                    <p className="mt-1 break-words text-xs leading-5 text-slate-400">
                      {event.message}
                    </p>
                  )}
                </div>
                <span className="shrink-0 text-[10px] text-slate-500">{style.label}</span>
              </li>
            );
          })}
        </ol>
      ) : (
        <p className="mt-4 text-xs text-slate-500">
          No agent activity history was returned for this project.
        </p>
      )}
    </section>
  );
}

function App() {
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [activityHistory, setActivityHistory] = useState([]);
  const [currentActiveAgent, setCurrentActiveAgent] = useState(null);
  const [projectActionError, setProjectActionError] = useState("");
  const [viewerProjectId, setViewerProjectId] = useState(null);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [recentProjects, setRecentProjects] = useState([]);
  const [recentProjectsLoading, setRecentProjectsLoading] = useState(true);
  const [recentProjectsError, setRecentProjectsError] = useState("");
  const eventSourceRef = useRef(null);
  const recentProjectsRequestRef = useRef(0);
  const recentProjectsRefreshRef = useRef(null);

  useEffect(() => () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    recentProjectsRefreshRef.current?.abort();
    recentProjectsRefreshRef.current = null;
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    const requestId = ++recentProjectsRequestRef.current;
    let active = true;

    fetchRecentProjects(controller.signal)
      .then((projects) => {
        if (active && recentProjectsRequestRef.current === requestId) {
          setRecentProjects(projects);
          setRecentProjectsError("");
        }
      })
      .catch(() => {
        if (active && recentProjectsRequestRef.current === requestId && !controller.signal.aborted) {
          setRecentProjectsError("Recent projects are temporarily unavailable.");
        }
      })
      .finally(() => {
        if (active && recentProjectsRequestRef.current === requestId) {
          setRecentProjectsLoading(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, []);

  const refreshRecentProjects = async () => {
    const requestId = ++recentProjectsRequestRef.current;
    recentProjectsRefreshRef.current?.abort();
    const controller = new AbortController();
    recentProjectsRefreshRef.current = controller;
    try {
      const projects = await fetchRecentProjects(controller.signal);
      if (recentProjectsRequestRef.current === requestId) {
        setRecentProjects(projects);
        setRecentProjectsError("");
      }
    } catch {
      if (recentProjectsRequestRef.current === requestId && !controller.signal.aborted) {
        setRecentProjectsError("Recent projects are temporarily unavailable.");
      }
    } finally {
      if (!controller.signal.aborted && recentProjectsRequestRef.current === requestId) {
        setRecentProjectsLoading(false);
      }
      if (recentProjectsRefreshRef.current === controller) {
        recentProjectsRefreshRef.current = null;
      }
    }
  };

  const generateProject = () => {
    const trimmedRequest = request.trim();
    if (!trimmedRequest) {
      setError("Please describe the software you want to build.");
      return;
    }

    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    const seenEvents = new Set();
    setActivityHistory([]);
    setCurrentActiveAgent(null);
    setLoading(true);
    setError("");
    setResponse(null);
    setProjectActionError("");
    setViewerProjectId(null);

    try {
      const streamUrl = apiEndpoint("/generate/stream");
      streamUrl.searchParams.set("request", trimmedRequest);

      const eventSource = new EventSource(streamUrl.toString());
      eventSourceRef.current = eventSource;
      let settled = false;

      const closeStream = () => {
        eventSource.close();
        if (eventSourceRef.current === eventSource) {
          eventSourceRef.current = null;
        }
      };

      eventSource.addEventListener("activity", (event) => {
        if (eventSourceRef.current !== eventSource) return;

        try {
          const activity = JSON.parse(event.data);
          if (!activity || typeof activity !== "object") return;
          const signature = JSON.stringify([
            activity.agent_name,
            activity.status,
            activity.timestamp,
            activity.attempt_number,
            activity.message,
          ]);
          if (seenEvents.has(signature)) return;
          seenEvents.add(signature);

          setActivityHistory((previous) => [...previous, activity]);
          if (activity.status === "running") {
            setCurrentActiveAgent(activity.agent_name || null);
          } else if (["completed", "failed"].includes(activity.status)) {
            setCurrentActiveAgent((current) =>
              current === activity.agent_name ? null : current
            );
          }
        } catch {
          // Ignore malformed activity payloads and continue consuming the stream.
        }
      });

      eventSource.addEventListener("complete", (event) => {
        if (settled || eventSourceRef.current !== eventSource) return;
        settled = true;

        try {
          const data = JSON.parse(event.data);
          const finalHistory = Array.isArray(data.activity_history) &&
            data.activity_history.every((item) => item && typeof item === "object");

          setActivityHistory((previous) => {
            if (!finalHistory || data.activity_history.length < previous.length) {
              return previous;
            }
            return data.activity_history;
          });
          setCurrentActiveAgent(data.current_active_agent ?? null);
          setResponse(data);
          setLoading(false);
          refreshRecentProjects();
        } catch {
          setError("The generation finished, but its response could not be read.");
          setLoading(false);
        } finally {
          closeStream();
        }
      });

      eventSource.addEventListener("error", () => {
        if (settled || eventSourceRef.current !== eventSource) return;
        settled = true;
        closeStream();
        setError("Generation failed. Please try again.");
        setLoading(false);
      });

      eventSource.onerror = () => {
        if (settled || eventSourceRef.current !== eventSource) return;
        settled = true;
        closeStream();
        setError("Unable to connect to the DevTeam AI backend.");
        setLoading(false);
      };
    } catch {
      eventSourceRef.current?.close();
      eventSourceRef.current = null;
      setError("Unable to connect to the DevTeam AI backend.");
      setLoading(false);
    }
  };

  const resetProject = () => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
    setLoading(false);
    setResponse(null);
    setError("");
    setRequest("");
    setActivityHistory([]);
    setCurrentActiveAgent(null);
    setProjectActionError("");
    setViewerProjectId(null);
  };

  const downloadProject = async (projectId) => {
    setProjectActionError("");
    setDownloadLoading(true);

    try {
      const downloadUrl = apiEndpoint(
        `/projects/${encodeURIComponent(projectId)}/download`
      );
      const downloadResponse = await fetch(downloadUrl);
      if (!downloadResponse.ok) throw new Error("Download failed.");

      const objectUrl = window.URL.createObjectURL(await downloadResponse.blob());
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `${projectId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 1000);
    } catch {
      setProjectActionError("Unable to download this project. Please try again.");
    } finally {
      setDownloadLoading(false);
    }
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

        <RecentProjects
          projects={recentProjects}
          loading={recentProjectsLoading}
          error={recentProjectsError}
          downloadLoading={downloadLoading}
          onView={(projectId) => setViewerProjectId(projectId)}
          onDownload={downloadProject}
        />

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

        {(loading || response || activityHistory.length > 0) && (
          <section className="mt-12">
            <LiveAgentActivity
              activityHistory={activityHistory}
              currentActiveAgent={currentActiveAgent}
            />
          </section>
        )}

        {response && (
          <ProjectGenerationComplete
            projectId={response.project_id}
            downloadLoading={downloadLoading}
            error={projectActionError}
            onView={() => setViewerProjectId(response.project_id)}
            onDownload={() => downloadProject(response.project_id)}
          />
        )}

        {viewerProjectId && (
          <ProjectViewer
            projectId={viewerProjectId}
            onClose={() => setViewerProjectId(null)}
          />
        )}

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


function RecentProjects({
  projects,
  loading,
  error,
  downloadLoading,
  onView,
  onDownload,
}) {
  return (
    <section className="mt-10">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">Your Workspace</p>
          <h3 className="mt-1 text-xl font-bold sm:text-2xl">Recent Projects</h3>
        </div>
        <span className="text-xs text-slate-500">Saved project history</span>
      </div>

      {loading ? (
        <p className="rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-slate-400">
          Loading recent projects...
        </p>
      ) : error ? (
        <p role="status" className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 text-sm text-amber-200/80">
          {error}
        </p>
      ) : projects.length === 0 ? (
        <p className="rounded-xl border border-dashed border-white/10 p-5 text-sm text-slate-500">
          No projects generated yet.
        </p>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <article key={project.project_id} className="rounded-2xl border border-white/10 bg-white/[0.025] p-4 sm:p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="min-w-0">
                  <h4 className="break-words font-semibold text-slate-100">
                    {project.user_request || project.project_id}
                  </h4>
                  <p className="mt-1 text-xs text-slate-500">
                    Created: {formatProjectDate(project.created_at)}
                  </p>
                  <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
                    <span>Status: <span className={project.status === "completed" ? "text-emerald-300" : project.status === "failed" ? "text-red-300" : "text-slate-300"}>{formatProjectStatus(project.status)}</span></span>
                    <span>Tests: {formatProjectStatus(project.test_status)}</span>
                    <span>Files: {project.file_count ?? 0}</span>
                  </p>
                </div>
                <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => onView(project.project_id)}
                    className="rounded-lg border border-blue-300/25 bg-blue-400/10 px-3 py-2 text-xs font-semibold text-blue-200 transition hover:bg-blue-400/20"
                  >
                    View Project
                  </button>
                  <button
                    type="button"
                    onClick={() => onDownload(project.project_id)}
                    disabled={downloadLoading}
                    className="rounded-lg bg-blue-500 px-3 py-2 text-xs font-semibold text-white transition hover:bg-blue-400 disabled:cursor-wait disabled:opacity-60"
                  >
                    Download ZIP
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}


function ProjectGenerationComplete({
  projectId,
  downloadLoading,
  error,
  onView,
  onDownload,
}) {
  return (
    <section className="mt-10 rounded-2xl border border-emerald-400/25 bg-gradient-to-br from-emerald-400/[0.09] to-blue-400/[0.04] p-5 shadow-xl shadow-emerald-950/10 sm:p-7">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-emerald-300">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-400/15 text-lg">✓</span>
            <h3 className="text-lg font-bold sm:text-xl">Project Generation Complete</h3>
          </div>
          <p className="mt-2 text-sm text-slate-300">
            Your project has been successfully generated.
          </p>
          <p className="mt-3 text-xs text-slate-400">
            Project ID: <span className="break-all font-mono text-blue-300">{projectId}</span>
          </p>
        </div>

        <div className="flex flex-col gap-2 sm:min-w-64 sm:flex-row">
          <button
            type="button"
            onClick={onView}
            className="rounded-xl border border-blue-300/30 bg-blue-400/10 px-4 py-3 text-sm font-semibold text-blue-200 transition hover:bg-blue-400/20"
          >
            View Project
          </button>
          <button
            type="button"
            onClick={onDownload}
            disabled={downloadLoading}
            className="rounded-xl bg-blue-500 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400 disabled:cursor-wait disabled:opacity-60"
          >
            {downloadLoading ? "Preparing ZIP..." : "Download ZIP"}
          </button>
        </div>
      </div>
      {error && (
        <p role="alert" className="mt-4 text-sm text-red-300">{error}</p>
      )}
    </section>
  );
}


function ProjectViewer({ projectId, onClose }) {
  const [files, setFiles] = useState([]);
  const [selectedPath, setSelectedPath] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    const loadProject = async () => {
      setLoading(true);
      setError("");
      setFiles([]);
      setSelectedPath("");

      try {
        const projectUrl = apiEndpoint(`/projects/${encodeURIComponent(projectId)}`);
        const projectResponse = await fetch(projectUrl, { signal: controller.signal });
        if (!projectResponse.ok) throw new Error("Project could not be loaded.");

        const data = await projectResponse.json();
        if (!Array.isArray(data.files)) throw new Error("Project response was invalid.");

        if (active) {
          setFiles(data.files);
          setSelectedPath(data.files[0]?.path || "");
        }
      } catch {
        if (active && !controller.signal.aborted) {
          setError("Unable to load project files. Please try again.");
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    loadProject();
    return () => {
      active = false;
      controller.abort();
    };
  }, [projectId]);

  const selectedFile = files.find((file) => file.path === selectedPath);

  return (
    <section className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80 shadow-2xl shadow-black/30">
      <div className="flex flex-col gap-3 border-b border-white/10 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">Project Files</p>
          <h3 className="mt-1 break-all font-mono text-sm text-slate-200">{projectId}</h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="self-start rounded-lg border border-white/10 px-3 py-2 text-sm text-slate-300 transition hover:bg-white/5 sm:self-auto"
        >
          Close Viewer
        </button>
      </div>

      {loading ? (
        <p className="p-6 text-sm text-slate-400">Loading project files...</p>
      ) : error ? (
        <p role="alert" className="p-6 text-sm text-red-300">{error}</p>
      ) : files.length === 0 ? (
        <p className="p-6 text-sm text-slate-400">This project contains no files.</p>
      ) : (
        <div className="grid min-h-80 lg:grid-cols-[minmax(14rem,0.8fr)_minmax(0,2fr)]">
          <nav aria-label="Generated project files" className="border-b border-white/10 p-3 lg:border-b-0 lg:border-r">
            <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Files</p>
            <ul className="max-h-[32rem] space-y-1 overflow-auto">
              {files.map((file) => {
                const depth = Math.min(file.path.split("/").length - 1, 8);
                const selected = selectedPath === file.path;
                return (
                  <li key={file.path}>
                    <button
                      type="button"
                      onClick={() => setSelectedPath(file.path)}
                      title={file.path}
                      className={`w-full truncate rounded-lg py-2 pr-2 text-left font-mono text-xs transition ${selected ? "bg-blue-400/15 text-blue-200" : "text-slate-400 hover:bg-white/5 hover:text-slate-200"}`}
                      style={{ paddingLeft: `${12 + depth * 12}px` }}
                    >
                      <span className="mr-2 text-slate-500">{file.is_binary ? "▧" : "▤"}</span>
                      {file.path}
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="min-w-0">
            <div className="border-b border-white/10 px-4 py-3 font-mono text-xs text-slate-300">
              {selectedFile?.path || "Select a file"}
            </div>
            {selectedFile?.is_binary || selectedFile?.content == null ? (
              <p className="p-5 text-sm text-slate-400">This file cannot be previewed as text.</p>
            ) : (
              <pre className="max-h-[32rem] overflow-auto p-4 text-xs leading-5 text-slate-300 sm:p-5"><code>{selectedFile?.content ?? ""}</code></pre>
            )}
          </div>
        </div>
      )}
    </section>
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
