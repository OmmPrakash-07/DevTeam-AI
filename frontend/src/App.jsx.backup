import { useEffect, useRef, useState } from "react";



const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";



const buttonStyles = {

  primary:

    "rounded-xl bg-blue-500 font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-400 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50",

  secondary:

    "rounded-xl border border-blue-300/25 bg-blue-400/10 font-semibold text-blue-200 transition hover:bg-blue-400/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-wait disabled:opacity-60",

  ghost:

    "rounded-xl border border-white/10 text-slate-300 transition hover:bg-white/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50",

  danger:

    "rounded-xl border border-red-400/25 bg-red-400/10 font-semibold text-red-200 transition hover:bg-red-400/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50",

};



function isHiddenProjectFile(path) {

  const normalizedPath = String(path || "").replace(/\\\\/g, "/");

  const segments = normalizedPath.split("/");

  const filename = segments[segments.length - 1] || "";



  return segments.includes("__pycache__") || /\\.(?:pyc|pyo)$/i.test(filename);

}



function buildProjectNavigatorEntries(files) {

  const entries = [];

  const addedFolders = new Set();



  files

    .filter((file) => !isHiddenProjectFile(file.path))

    .forEach((file) => {

      const normalizedPath = String(file.path || "").replace(/\\\\/g, "/");

      const segments = normalizedPath.split("/").filter(Boolean);



      segments.slice(0, -1).forEach((segment, index) => {

        const folderPath = segments.slice(0, index + 1).join("/");

        if (!addedFolders.has(folderPath)) {

          addedFolders.add(folderPath);

          entries.push({

            type: "folder",

            path: folderPath,

            name: segment,

            depth: index,

          });

        }

      });



      entries.push({

        type: "file",

        path: file.path,

        name: segments[segments.length - 1] || file.path,

        depth: Math.max(segments.length - 1, 0),

        file,

      });

    });



  return entries;

}



function FileIcon({ className = "h-4 w-4" }) {

  return (

    <svg

      className={className}

      viewBox="0 0 24 24"

      fill="none"

      stroke="currentColor"

      strokeWidth="1.7"

      aria-hidden="true"

    >

      <path

        strokeLinecap="round"

        strokeLinejoin="round"

        d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"

      />

      <path

        strokeLinecap="round"

        strokeLinejoin="round"

        d="M14 3v6h6M8 13h8M8 17h8"

      />

    </svg>

  );

}



function FolderIcon({ className = "h-4 w-4" }) {

  return (

    <svg

      className={className}

      viewBox="0 0 24 24"

      fill="none"

      stroke="currentColor"

      strokeWidth="1.7"

      aria-hidden="true"

    >

      <path

        strokeLinecap="round"

        strokeLinejoin="round"

        d="M3 6.5A1.5 1.5 0 0 1 4.5 5H10l2 2h7.5A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"

      />

      <path strokeLinecap="round" strokeLinejoin="round" d="M3 9h18" />

    </svg>

  );

}



function apiEndpoint(path) {

  return new URL(`${API_URL.replace(/\/+$/, "")}${path}`, window.location.href);

}



async function fetchRecentProjects(signal) {

  const response = await fetch(apiEndpoint("/projects"), { signal });

  if (!response.ok) throw new Error("Recent projects could not be loaded.");



  const data = await response.json();

  if (!Array.isArray(data.projects))

    throw new Error("Recent projects response was invalid.");

  return data.projects;

}



async function fetchHistoryEntries(signal) {

  const response = await fetch(apiEndpoint("/history"), { signal });

  if (!response.ok) throw new Error("Conversation history could not be loaded.");

  const data = await response.json();

  const entries = Array.isArray(data.history)

    ? data.history

    : Array.isArray(data)

      ? data

      : null;

  if (!entries) throw new Error("History response was invalid.");

  return entries;
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



function formatHistoryDate(value) {

  const date = new Date(value);

  return Number.isNaN(date.getTime())

    ? "Date unavailable"

    : date.toLocaleString(undefined, {

        day: "numeric",

        month: "short",

        year: "numeric",

        hour: "numeric",

        minute: "2-digit",

      });
}



function formatProjectStatus(value) {

  if (!value) return "Not available";

  return value

    .replace(/[_-]+/g, " ")

    .replace(/\b\w/g, (letter) => letter.toUpperCase());

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



const navigationItems = [

  { id: "home", label: "Home", icon: "home" },

  { id: "new-project", label: "New Project", icon: "plus" },

  { id: "my-projects", label: "My Projects", icon: "folder" },

  { id: "history", label: "History", icon: "history" },

  { id: "settings", label: "Settings", icon: "settings" },

];



function DevTeamLogo({ className = "h-11 w-11" }) {

  return (

    <img

      src="/jarvis.png"

      alt="DevTeam AI logo"

      className={`${className} shrink-0 object-contain`}

    />

  );

}



function HamburgerIcon({ open }) {

  return (

    <svg

      className="h-5 w-5"

      viewBox="0 0 24 24"

      fill="none"

      stroke="currentColor"

      strokeWidth="1.8"

      strokeLinecap="round"

      aria-hidden="true"

    >

      <path d={open ? "M6 6l12 12" : "M4 6h16"} />

      <path

        d="M4 12h16"

        className={`transition-opacity duration-200 ${open ? "opacity-0" : "opacity-100"}`}

      />

      <path d={open ? "M6 18L18 6" : "M4 18h16"} />

    </svg>

  );

}



function SettingsIcon() {

  return (

    <svg

      className="h-5 w-5 shrink-0"

      viewBox="0 0 24 24"

      fill="none"

      stroke="currentColor"

      strokeWidth="1.7"

      strokeLinecap="round"

      strokeLinejoin="round"

      aria-hidden="true"

    >

      <path d="M10.3 2.8h3.4l.5 2a7.6 7.6 0 0 1 1.6.9l1.9-.8 1.7 3-1.5 1.4a7.7 7.7 0 0 1 0 1.9l1.5 1.4-1.7 3-1.9-.8a7.6 7.6 0 0 1-1.6.9l-.5 2h-3.4l-.5-2a7.6 7.6 0 0 1-1.6-.9l-1.9.8-1.7-3 1.5-1.4a7.7 7.7 0 0 1 0-1.9L4.6 7.9l1.7-3 1.9.8a7.6 7.6 0 0 1 1.6-.9z" />

      <circle cx="12" cy="12" r="2.75" />

    </svg>

  );

}



function NavigationIcon({ name }) {

  if (name === "settings") return <SettingsIcon />;



  const common = {

    className: "h-5 w-5 shrink-0",

    viewBox: "0 0 24 24",

    fill: "none",

    stroke: "currentColor",

    strokeWidth: "1.7",

    strokeLinecap: "round",

    strokeLinejoin: "round",

    "aria-hidden": "true",

  };



  if (name === "home") {

    return (

      <svg {...common}>

        <path d="m3 10 9-7 9 7" />

        <path d="M5 9v11h14V9M9 20v-6h6v6" />

      </svg>

    );

  }

  if (name === "plus") {

    return (

      <svg {...common}>

        <path d="M12 5v14M5 12h14" />

      </svg>

    );

  }

  if (name === "folder") {

    return (

      <svg {...common}>

        <path d="M3 6.5A1.5 1.5 0 0 1 4.5 5H10l2 2h7.5A1.5 1.5 0 0 1 21 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z" />

        <path d="M3 9h18" />

      </svg>

    );

  }

  if (name === "history") {

    return (

      <svg {...common}>

        <path d="M3 12a9 9 0 1 0 2.6-6.4L3 8" />

        <path d="M3 4v4h4M12 7v5l3 2" />

      </svg>

    );

  }

  return null;

}



function NavItem({ item, active, onClick }) {

  return (

    <button

      type="button"

      onClick={onClick}

      aria-current={active ? "page" : undefined}

      className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 ${active ? "border border-blue-300/20 bg-blue-400/10 text-blue-200" : "border border-transparent text-slate-400 hover:bg-white/5 hover:text-slate-100"}`}

    >

      <NavigationIcon name={item.icon} />

      <span>{item.label}</span>

    </button>

  );

}



function Sidebar({ open, activeItem, onNavigate, settingsMessage }) {

  return (

    <>

      {open && (

        <button

          type="button"

          aria-label="Close navigation"

          onClick={() => onNavigate(null)}

          className="fixed inset-x-0 bottom-0 top-[72px] z-40 bg-slate-950/55 backdrop-blur-[2px] lg:hidden"

        />

      )}

      <aside

        id="devteam-sidebar"

        aria-label="Primary navigation"

        aria-hidden={!open}

        inert={!open}

        className={`fixed bottom-0 left-0 top-[72px] z-50 flex w-80 max-w-[calc(100vw-1rem)] flex-col overflow-y-auto overscroll-contain border-r border-white/10 bg-slate-950/95 px-5 py-6 shadow-2xl shadow-black/30 backdrop-blur-2xl transition-transform duration-300 ease-in-out ${open ? "translate-x-0" : "-translate-x-full"}`}

      >

        <div className="flex items-center gap-3 border-b border-white/10 pb-6">

          <DevTeamLogo />

          <div className="min-w-0">

            <h2 className="font-bold tracking-tight text-slate-100">

              DevTeam AI

            </h2>

            <p className="mt-1 text-xs leading-5 text-slate-400">

              Your AI Software Development Team

            </p>

          </div>

        </div>



        <nav aria-label="Main menu" className="mt-6 space-y-2">

          {navigationItems.map((item) => (

            <NavItem

              key={item.id}

              item={item}

              active={activeItem === item.id}

              onClick={() => onNavigate(item.id)}

            />

          ))}

        </nav>



        {settingsMessage && (

          <p

            role="status"

            className="mt-4 rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2.5 text-xs leading-5 text-slate-400"

          >

            {settingsMessage}

          </p>

        )}



        <div className="mt-auto rounded-2xl border border-blue-300/15 bg-gradient-to-br from-blue-400/[0.08] to-purple-400/[0.06] p-4">

          <DevTeamLogo className="h-9 w-9" />

          <p className="mt-3 text-sm leading-6 text-slate-300">

            Turn your idea into working software with AI agents

          </p>

        </div>

      </aside>

    </>

  );

}



function getActivityLabel(event) {

  const name =

    event.display_name ||

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

          const status = activityStatusStyles[event?.status]

            ? event.status

            : "pending";

          const style = activityStatusStyles[status];

          return (

            <div

              key={stage.id}

              className={`rounded-xl border p-3 ${style.className}`}

            >

              <div className="flex items-center gap-2">

                <span className="text-lg" aria-label={style.label}>

                  {style.icon}

                </span>

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

            const status = activityStatusStyles[event?.status]

              ? event.status

              : "pending";

            const style = activityStatusStyles[status];

            return (

              <li

                key={`${event.agent_name || "activity"}-${event.timestamp || index}-${index}`}

                className="flex items-start gap-3 rounded-lg bg-slate-950/50 px-3 py-2.5"

              >

                <span

                  className={`mt-0.5 w-5 shrink-0 text-center ${style.className.split(" ").at(-1)}`}

                >

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

                <span className="shrink-0 text-[10px] text-slate-500">

                  {style.label}

                </span>

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



function ModelSelector({ selectedModel, onSelectModel }) {
  const [open, setOpen] = useState(false);
  const [providers, setProviders] = useState([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [modelError, setModelError] = useState("");

  useEffect(() => {
    let active = true;

    const loadModels = async () => {
      setLoadingModels(true);
      setModelError("");

      try {
        const response = await fetch(apiEndpoint("/models"));

        if (!response.ok) {
          throw new Error(`Models could not be loaded (${response.status})`);
        }

        const data = await response.json();

        if (active) {
          setProviders(
            Array.isArray(data.providers) ? data.providers : []
          );
        }
      } catch (error) {
        if (active) {
          setModelError(
            error instanceof Error
              ? error.message
              : "Models could not be loaded."
          );
        }
      } finally {
        if (active) {
          setLoadingModels(false);
        }
      }
    };

    loadModels();

    return () => {
      active = false;
    };
  }, []);

  const selectedLabel =
    selectedModel?.name ||
    selectedModel?.modelId ||
    "Select Model";

  return (
    <div className="relative w-52">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-3 rounded-xl border border-white/10 bg-slate-950/70 px-3 py-2.5 text-left transition hover:border-blue-400/30 hover:bg-white/[0.04] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400/30"
      >
        <div className="min-w-0">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
            Model
          </div>

          <div className="mt-0.5 truncate text-xs font-medium text-slate-200">
            {selectedLabel}
          </div>
        </div>

        <svg
          className={`h-4 w-4 shrink-0 text-slate-500 transition-transform ${
            open ? "rotate-180" : ""
          }`}
          viewBox="0 0 20 20"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="m5 7.5 5 5 5-5"
            stroke="currentColor"
            strokeWidth="1.7"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {open && (
        <div className="absolute bottom-full left-0 z-50 mb-2 max-h-72 w-72 overflow-y-auto rounded-xl border border-white/10 bg-slate-950 p-2 shadow-2xl shadow-black/40">
          {loadingModels && (
            <div className="px-3 py-3 text-xs text-slate-500">
              Loading models...
            </div>
          )}

          {modelError && !loadingModels && (
            <div className="rounded-lg border border-red-400/20 bg-red-400/10 px-3 py-2.5 text-xs text-red-300">
              {modelError}
            </div>
          )}

          {!loadingModels &&
            !modelError &&
            providers.map((provider) => (
              <div key={provider.id} className="mb-2 last:mb-0">
                <div className="px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  {provider.name}
                </div>

                {(provider.models || []).map((model) => {
                  const selected =
                    selectedModel?.providerId === provider.id &&
                    selectedModel?.modelId === model.id;

                  return (
                    <button
                      key={`${provider.id}-${model.id}`}
                      type="button"
                      onClick={() => {
                        onSelectModel({
                          providerId: provider.id,
                          modelId: model.id,
                          name: model.name || model.id,
                        });
                        setOpen(false);
                      }}
                      className={`flex w-full items-center justify-between rounded-lg px-2.5 py-2 text-left text-xs transition ${
                        selected
                          ? "bg-blue-400/10 text-blue-200"
                          : "text-slate-300 hover:bg-white/[0.05] hover:text-white"
                      }`}
                    >
                      <span className="truncate">
                        {model.name || model.id}
                      </span>

                      {selected && (
                        <span className="ml-2 shrink-0 text-blue-300">
                          ✓
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

function App() {

  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [activeNavigationItem, setActiveNavigationItem] = useState("home");

  const [currentView, setCurrentView] = useState("home");

  const [settingsMessage, setSettingsMessage] = useState("");

  const [selectedModel, setSelectedModel] = useState(() => {
    try {
      const saved = window.localStorage.getItem(
        "devteam-selected-model"
      );

      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [request, setRequest] = useState("");

  const [loading, setLoading] = useState(false);

  const [response, setResponse] = useState(null);

  const [assistantResponse, setAssistantResponse] = useState(null);

  const [generationIntent, setGenerationIntent] = useState(null);

  const [error, setError] = useState("");

  const [activityHistory, setActivityHistory] = useState([]);

  const [currentActiveAgent, setCurrentActiveAgent] = useState(null);

  const [projectActionError, setProjectActionError] = useState("");

  const [viewerProjectId, setViewerProjectId] = useState(null);

  const [downloadLoading, setDownloadLoading] = useState(false);

  const [recentProjects, setRecentProjects] = useState([]);

  const [recentProjectsLoading, setRecentProjectsLoading] = useState(false);

  const [recentProjectsError, setRecentProjectsError] = useState("");

  const [historyEntries, setHistoryEntries] = useState([]);

  const [historyLoading, setHistoryLoading] = useState(false);

  const [historyError, setHistoryError] = useState("");

  const [selectedHistoryId, setSelectedHistoryId] = useState(null);

  const [selectedHistory, setSelectedHistory] = useState(null);

  const [historyDetailLoading, setHistoryDetailLoading] = useState(false);

  const [historyDetailError, setHistoryDetailError] = useState("");

  const [historyDeleteLoading, setHistoryDeleteLoading] = useState(false);
  useEffect(() => {
    try {
      if (selectedModel) {
        window.localStorage.setItem(
          "devteam-selected-model",
          JSON.stringify(selectedModel)
        );
      }
    } catch {
      // Continue without persistence if localStorage is unavailable.
    }
  }, [selectedModel]);




  const eventSourceRef = useRef(null);

  const hamburgerButtonRef = useRef(null);

  const homeSectionRef = useRef(null);

  const requestSectionRef = useRef(null);

  const requestInputRef = useRef(null);

  const recentProjectsSectionRef = useRef(null);

  const recentProjectsRequestRef = useRef(0);

  const historyRequestRef = useRef(0);



  useEffect(

    () => () => {

      eventSourceRef.current?.close();

      eventSourceRef.current = null;
      historyRequestRef.current += 1;

    },

    [],

  );



  useEffect(() => {

    if (currentView !== "my-projects") {

      return undefined;

    }



    const controller = new AbortController();

    const requestId = ++recentProjectsRequestRef.current;

    let active = true;



    const loadProjects = async () => {

      try {

        const projects = await fetchRecentProjects(controller.signal);



        if (!active || requestId !== recentProjectsRequestRef.current) {

          return;

        }



        setRecentProjects(projects);

      } catch (requestError) {

        if (

          requestError?.name === "AbortError" ||

          !active ||

          requestId !== recentProjectsRequestRef.current

        ) {

          return;

        }



        setRecentProjectsError(

          requestError?.message || "Unable to load projects.",

        );

      } finally {

        if (active && requestId === recentProjectsRequestRef.current) {

          setRecentProjectsLoading(false);

        }

      }

    };



    loadProjects();



    return () => {

      active = false;

      controller.abort();

    };

  }, [currentView]);



  useEffect(() => {
    if (currentView !== "history") {
      return undefined;
    }

    const controller = new AbortController();
    const requestId = ++historyRequestRef.current;
    let active = true;

    const loadHistory = async () => {
      try {
        const entries = await fetchHistoryEntries(controller.signal);

        if (!active || requestId !== historyRequestRef.current) {
          return;
        }

        setHistoryEntries(entries);
        setHistoryError("");
      } catch (requestError) {
        if (
          requestError?.name === "AbortError" ||
          !active ||
          requestId !== historyRequestRef.current
        ) {
          return;
        }

        setHistoryError(
          requestError?.message || "Unable to load conversation history.",
        );
      } finally {
        if (active && requestId === historyRequestRef.current) {
          setHistoryLoading(false);
        }
      }
    };

    loadHistory();

    return () => {
      active = false;
      controller.abort();
    };
  }, [currentView]);



  useEffect(() => {

    if (!sidebarOpen) return undefined;



    const handleKeyDown = (event) => {

      if (event.key === "Escape") {

        setSidebarOpen(false);

        hamburgerButtonRef.current?.focus();

      }

    };



    document.addEventListener("keydown", handleKeyDown);

    return () => document.removeEventListener("keydown", handleKeyDown);

  }, [sidebarOpen]);



  const navigateSidebar = (destination) => {

    if (destination === null) {

      setSidebarOpen(false);

      hamburgerButtonRef.current?.focus();

      return;

    }



    setActiveNavigationItem(destination);

    setSettingsMessage("");



    if (destination === "settings") {

      setCurrentView("settings");

      setSettingsMessage("Settings are not available yet.");

      setSidebarOpen(false);

      window.scrollTo({ top: 0, behavior: "smooth" });

      return;

    }



    if (destination === "home") {

      setCurrentView("home");

      setSidebarOpen(false);

      window.scrollTo({ top: 0, behavior: "smooth" });

      return;

    }



    if (destination === "new-project") {

      setCurrentView("home");

      setSidebarOpen(false);



      window.setTimeout(() => {

        requestSectionRef.current?.scrollIntoView({

          behavior: "smooth",

          block: "center",

        });

        requestInputRef.current?.focus({ preventScroll: true });

      }, 50);



      return;

    }



    if (destination === "my-projects") {

      setRecentProjectsLoading(true);

      setRecentProjectsError("");

      setCurrentView("my-projects");

      setSidebarOpen(false);



      window.scrollTo({

        top: 0,

        behavior: "smooth",

      });



      return;

    }



    if (destination === "history") {

      setHistoryLoading(true);

      setHistoryError("");

      setSelectedHistoryId(null);

      setSelectedHistory(null);

      setHistoryDetailError("");

      setCurrentView("history");

      setSidebarOpen(false);

      window.scrollTo({ top: 0, behavior: "smooth" });

    }

  };






  const sendMessage = () => {

    const trimmedRequest = request.trim();



    if (!trimmedRequest) {

      setError("Please enter a question or describe a software project.");

      return;

    }



    eventSourceRef.current?.close();

    eventSourceRef.current = null;



    const seenEvents = new Set();



    setCurrentView("home");

    setActiveNavigationItem("home");

    setActivityHistory([]);

    setCurrentActiveAgent(null);

    setGenerationIntent(null);

    setLoading(true);

    setError("");

    setResponse(null);

    setAssistantResponse(null);

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



      eventSource.addEventListener("intent", (event) => {

        if (eventSourceRef.current !== eventSource) return;



        try {

          const data = JSON.parse(event.data);



          if (

            ["ANSWER", "CODING_HELP", "BUILD_PROJECT"].includes(data.intent)

          ) {

            setGenerationIntent(data.intent);

          }

        } catch {

          // Ignore malformed intent payloads.

        }

      });



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

              current === activity.agent_name ? null : current,

            );

          }

        } catch {

          // Ignore malformed activity payloads.

        }

      });



      eventSource.addEventListener("complete", (event) => {

        if (settled || eventSourceRef.current !== eventSource) return;



        settled = true;



        try {

          const data = JSON.parse(event.data);



          setGenerationIntent("BUILD_PROJECT");

          setAssistantResponse(null);



          const finalHistory =

            Array.isArray(data.activity_history) &&

            data.activity_history.every(

              (item) => item && typeof item === "object",

            );



          setActivityHistory((previous) => {

            if (

              !finalHistory ||

              data.activity_history.length < previous.length

            ) {

              return previous;

            }



            return data.activity_history;

          });



          setCurrentActiveAgent(data.current_active_agent ?? null);

          setResponse(data);

          setLoading(false);

        } catch {

          setError(

            "The generation finished, but its response could not be read.",

          );

          setLoading(false);

        } finally {

          closeStream();

        }

      });



      eventSource.addEventListener("response", (event) => {

        if (settled || eventSourceRef.current !== eventSource) return;



        settled = true;



        try {

          const data = JSON.parse(event.data);



          if (

            !["ANSWER", "CODING_HELP"].includes(data.intent) ||

            typeof data.answer !== "string"

          ) {

            throw new Error("Invalid assistant response.");

          }



          setGenerationIntent(data.intent);

          setAssistantResponse(data);



          setLoading(false);

        } catch {

          setError("The assistant response could not be read.");

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



  const refreshHistory = async () => {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const entries = await fetchHistoryEntries();
      setHistoryEntries(entries);
    } catch (requestError) {
      setHistoryError(
        requestError?.message || "Unable to refresh conversation history.",
      );
    } finally {
      setHistoryLoading(false);
    }
  };



  const viewHistoryEntry = async (historyId) => {
    setSelectedHistoryId(historyId);
    setSelectedHistory(null);
    setHistoryDetailLoading(true);
    setHistoryDetailError("");

    try {
      const response = await fetch(
        apiEndpoint(`/history/${encodeURIComponent(historyId)}`),
      );

      if (!response.ok) {
        throw new Error("Conversation could not be loaded.");
      }

      const data = await response.json();
      setSelectedHistory(data.history || data);
    } catch (requestError) {
      setHistoryDetailError(
        requestError?.message || "Unable to load this conversation.",
      );
    } finally {
      setHistoryDetailLoading(false);
    }
  };



  const deleteHistoryEntry = async (historyId) => {
    setHistoryDeleteLoading(true);
    setHistoryError("");

    try {
      const response = await fetch(
        apiEndpoint(`/history/${encodeURIComponent(historyId)}`),
        { method: "DELETE" },
      );

      if (!response.ok) {
        throw new Error("Conversation could not be deleted.");
      }

      if (selectedHistoryId === historyId) {
        setSelectedHistoryId(null);
        setSelectedHistory(null);
        setHistoryDetailError("");
      }

      await refreshHistory();
    } catch (requestError) {
      setHistoryError(
        requestError?.message || "Unable to delete this conversation.",
      );
    } finally {
      setHistoryDeleteLoading(false);
    }
  };



  const resetProject = () => {

    eventSourceRef.current?.close();

    eventSourceRef.current = null;



    setLoading(false);

    setResponse(null);

    setAssistantResponse(null);

    setGenerationIntent(null);

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

        `/projects/${encodeURIComponent(projectId)}/download`,

      );



      const downloadResponse = await fetch(downloadUrl);



      if (!downloadResponse.ok) {

        throw new Error("Download failed.");

      }



      const objectUrl = window.URL.createObjectURL(

        await downloadResponse.blob(),

      );



      const link = document.createElement("a");

      link.href = objectUrl;

      link.download = `${projectId}.zip`;



      document.body.appendChild(link);

      link.click();

      link.remove();



      window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 1000);

    } catch {

      setProjectActionError(

        "Unable to download this project. Please try again.",

      );

    } finally {

      setDownloadLoading(false);

    }

  };



  return (

    <div className="min-h-screen bg-slate-950 text-slate-100">

      <header className="sticky top-0 z-50 h-[72px] border-b border-white/10 bg-slate-950/80 backdrop-blur-xl">

        <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">

          <div className="flex min-w-0 items-center gap-2 pl-14 sm:gap-3">

            <DevTeamLogo className="h-10 w-10 sm:h-11 sm:w-11" />



            <div className="min-w-0">

              <h1 className="text-sm font-bold tracking-tight text-slate-100 sm:text-xl">

                DevTeam AI

              </h1>



              <p className="max-w-36 text-[10px] leading-3 text-slate-400 sm:max-w-none sm:text-xs sm:leading-normal">

                Autonomous Software Development Team

              </p>

            </div>

          </div>



          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-2 py-1.5 sm:px-3">

            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />



            <span className="hidden text-xs font-medium text-emerald-300 sm:block">

              Backend Online

            </span>

          </div>

        </div>

      </header>



      <button

        ref={hamburgerButtonRef}

        type="button"

        aria-label={sidebarOpen ? "Close navigation" : "Open navigation"}

        aria-expanded={sidebarOpen}

        aria-controls="devteam-sidebar"

        onClick={() => {

          setSettingsMessage("");

          setSidebarOpen((open) => !open);

        }}

        className="fixed left-4 top-4 z-[60] flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900/90 text-slate-300 shadow-lg shadow-black/20 backdrop-blur transition hover:bg-white/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-300 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950"

      >

        <HamburgerIcon open={sidebarOpen} />

      </button>



      <Sidebar

        open={sidebarOpen}

        activeItem={activeNavigationItem}

        onNavigate={navigateSidebar}

        settingsMessage={settingsMessage}

      />



      <main

        className={`mx-auto max-w-7xl px-4 py-8 transition-[margin] duration-300 ease-in-out sm:px-6 sm:py-10 lg:px-8 ${

          sidebarOpen ? "lg:ml-80" : ""

        }`}

      >

        {currentView === "home" && (

          <>

            <section

              ref={homeSectionRef}

              className="mx-auto max-w-4xl scroll-mt-24 text-center"

            >

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

                Ask a question, get coding help, or describe a software idea.

                DevTeam AI chooses the appropriate response and only starts

                project generation when you request software to be built.

              </p>

            </section>



            <section

              ref={requestSectionRef}

              className="mx-auto mt-10 max-w-4xl scroll-mt-24"

            >

              <div className="rounded-2xl border border-white/10 bg-white/[0.035] p-4 shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-6">

                <div className="mb-4 flex items-center justify-between gap-3">

                  <div>

                    <h3 className="font-semibold">

                      Ask or build with DevTeam AI

                    </h3>



                    <p className="mt-1 text-xs text-slate-500 sm:text-sm">

                      Ask a question, get coding help, or describe a project to

                      build.

                    </p>

                  </div>



                  <span className="hidden rounded-lg bg-slate-800 px-2.5 py-1 text-xs text-slate-400 sm:block">

                    AI

                  </span>

                </div>



                <textarea

                  ref={requestInputRef}

                  value={request}

                  onChange={(event) => setRequest(event.target.value)}

                  onKeyDown={(event) => {

                    if (

                      event.key === "Enter" &&

                      (event.ctrlKey || event.metaKey)

                    ) {

                      event.preventDefault();

                      sendMessage();

                    }

                  }}

                  placeholder="Ask anything or describe a software project..."

                  rows={5}

                  disabled={loading}

                  className="w-full resize-none rounded-xl border border-white/10 bg-slate-950/70 px-4 py-4 text-sm leading-6 text-slate-200 outline-none transition placeholder:text-slate-600 focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/10 disabled:cursor-not-allowed disabled:opacity-60"

                />
<div className="mt-3 flex items-center">
  <ModelSelector
    selectedModel={selectedModel}
    onSelectModel={setSelectedModel}
  />
</div>



                {error && (

                  <div

                    role="alert"

                    className="mt-4 rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300"

                  >

                    ⚠️ {error}

                  </div>

                )}



                <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                  <span className="text-xs text-slate-500">

                    {request.length} characters • Ctrl + Enter to send

                  </span>



                  <button

                    type="button"

                    onClick={sendMessage}

                    disabled={loading}

                    className={`${buttonStyles.primary} w-full px-5 py-3 text-sm sm:w-auto`}

                  >

                    {loading ? (

                      <span className="flex items-center justify-center gap-2">

                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />

                        Working...

                      </span>

                    ) : (

                      "Send"

                    )}

                  </button>

                </div>

              </div>

            </section>



            {generationIntent === "BUILD_PROJECT" && (

              <section className="mt-12">

                <div className="relative mb-5 text-center">

                  <p className="text-xs font-semibold tracking-wide text-blue-400">

                    Development Pipeline

                  </p>



                  <h3 className="mt-1 text-xl font-bold sm:text-2xl">

                    AI Agent Workflow

                  </h3>



                  <span className="mt-2 block text-xs text-slate-500 sm:absolute sm:right-0 sm:top-1/2 sm:mt-0">

                    8 Agents

                  </span>

                </div>



                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">

                  {stages.map((stage, index) => (

                    <div

                      key={stage.id}

                      className="relative rounded-xl border border-white/10 bg-white/[0.025] p-4 text-center transition hover:-translate-y-1 hover:border-blue-400/30 hover:bg-white/[0.05]"

                    >

                      <div className="text-2xl">{stage.icon}</div>



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

            )}



            {generationIntent === "BUILD_PROJECT" &&

              (loading || response || activityHistory.length > 0) && (

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



            {assistantResponse && (

              <AssistantResponse response={assistantResponse} />

            )}



            {viewerProjectId && (

              <ProjectViewer

                projectId={viewerProjectId}

                onClose={() => setViewerProjectId(null)}

              />

            )}



            {response && (

              <ProjectResult response={response} onReset={resetProject} />

            )}



            {!response && !assistantResponse && !loading && (

              <section className="mt-12 rounded-2xl border border-dashed border-white/10 p-8 text-center sm:p-12">

                <div className="text-4xl">🧠</div>



                <h3 className="mt-4 text-lg font-semibold">

                  Ready when you are

                </h3>



                <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">

                  Ask a question, request coding help, or describe an

                  application and DevTeam AI will choose the right way to help.

                </p>

              </section>

            )}

          </>

        )}



        {currentView === "my-projects" && (

          <>

            <MyProjects

              sectionRef={recentProjectsSectionRef}

              projects={recentProjects}

              loading={recentProjectsLoading}

              error={recentProjectsError}

              downloadLoading={downloadLoading}

              onView={(projectId) => setViewerProjectId(projectId)}

              onDownload={downloadProject}

            />



            {viewerProjectId && (

              <ProjectViewer

                projectId={viewerProjectId}

                onClose={() => setViewerProjectId(null)}

              />

            )}



            {projectActionError && (

              <p

                role="alert"

                className="mx-auto mt-4 max-w-5xl text-sm text-red-300"

              >

                {projectActionError}

              </p>

            )}

          </>

        )}



        {currentView === "history" && (

          <History
            history={historyEntries}
            loading={historyLoading}
            error={historyError}
            selectedHistory={selectedHistory}
            selectedHistoryId={selectedHistoryId}
            detailLoading={historyDetailLoading}
            detailError={historyDetailError}
            deleteLoading={historyDeleteLoading}
            onView={viewHistoryEntry}
            onClose={() => {
              setSelectedHistoryId(null);
              setSelectedHistory(null);
              setHistoryDetailError("");
            }}
            onDelete={deleteHistoryEntry}
            onRefresh={refreshHistory}
          />

        )}



        {currentView === "settings" && (

          <section className="mx-auto max-w-4xl py-4 sm:py-8">

            <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-8 text-center shadow-2xl shadow-black/20 backdrop-blur-xl sm:p-12">

              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/20 bg-blue-400/10">

                <SettingsIcon />

              </div>



              <h2 className="mt-5 text-3xl font-semibold tracking-tight text-white">

                Settings

              </h2>



              <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-400">

                {settingsMessage || "Settings are not available yet."}

              </p>

            </div>

          </section>

        )}

      </main>



      <footer className="border-t border-white/10 py-6">

        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 text-center text-xs text-slate-600 sm:flex-row sm:px-6 lg:px-8">

          <span>DevTeam AI • Multi-Agent Software Engineering</span>

          <span>React + Tailwind + FastAPI + LangGraph</span>

        </div>

      </footer>

    </div>

  );

}



function AssistantResponse({ response }) {

  const title = response.intent === "CODING_HELP" ? "Coding Help" : "Answer";



  return (

    <section

      className="mt-10 rounded-2xl border border-blue-300/15 bg-white/[0.035] p-5 shadow-xl shadow-black/10 sm:p-7"

      aria-live="polite"

    >

      <p className="text-xs font-semibold tracking-wide text-blue-300">

        {title}

      </p>

      <h3 className="mt-2 break-words text-lg font-semibold text-slate-100">

        {response.user_request}

      </h3>

      <div className="mt-4 whitespace-pre-wrap break-words text-sm leading-7 text-slate-300">

        {response.answer}

      </div>

    </section>

  );

}



function MyProjects({

  sectionRef,

  projects,

  loading,

  error,

  downloadLoading,

  onView,

  onDownload,

}) {

  return (

    <section ref={sectionRef} className="mt-10 scroll-mt-24">

      <div className="mb-4 text-center">

        <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">

          Your Workspace

        </p>

        <h3 className="mt-1 text-xl font-bold sm:text-2xl">My Projects</h3>

        <p className="mx-auto mt-2 max-w-2xl text-sm text-slate-500">

          Your generated software projects and their complete development data.

        </p>

      </div>



      {loading ? (

        <p className="rounded-xl border border-white/10 bg-white/[0.025] p-4 text-sm text-slate-400">

          Loading projects...

        </p>

      ) : error ? (

        <p

          role="status"

          className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-4 text-sm text-amber-200/80"

        >

          {error}

        </p>

      ) : projects.length === 0 ? (

        <p className="rounded-xl border border-dashed border-white/10 p-5 text-sm text-slate-500">

          No projects generated yet. Build a project from Home to see it here.

        </p>

      ) : (

        <div className="space-y-3">

          {projects.map((project) => (

            <article

              key={project.project_id}

              className="rounded-2xl border border-white/10 bg-white/[0.025] p-4 sm:p-5"

            >

              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">

                <div className="min-w-0">

                  <h4 className="break-words font-semibold text-slate-100">

                    {project.user_request || project.project_id}

                  </h4>

                  <p className="mt-1 text-xs text-slate-500">

                    Created: {formatProjectDate(project.created_at)}

                  </p>

                  <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">

                    <span>

                      Status:{" "}

                      <span

                        className={

                          project.status === "completed"

                            ? "text-emerald-300"

                            : project.status === "failed"

                              ? "text-red-300"

                              : "text-slate-300"

                        }

                      >

                        {formatProjectStatus(project.status)}

                      </span>

                    </span>

                    <span>

                      Tests: {formatProjectStatus(project.test_status)}

                    </span>

                    <span>Files: {project.file_count ?? 0}</span>

                  </p>

                </div>

                <div className="flex shrink-0 flex-col gap-2 sm:flex-row">

                  <button

                    type="button"

                    onClick={() => onView(project.project_id)}

                    className={`${buttonStyles.primary} px-3 py-2 text-xs`}

                  >

                    View Project

                  </button>

                  <button

                    type="button"

                    onClick={() => onDownload(project.project_id)}

                    disabled={downloadLoading}

                    className={`${buttonStyles.secondary} px-3 py-2 text-xs`}

                  >

                    {downloadLoading ? "Preparing ZIP..." : "Download ZIP"}

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



function History({

  history,

  loading,

  error,

  selectedHistory,

  selectedHistoryId,

  detailLoading,

  detailError,

  deleteLoading,

  onView,

  onClose,

  onDelete,

  onRefresh,

}) {

  return (

    <section className="mx-auto w-full max-w-5xl py-4 sm:py-8">

      <div className="mb-8 text-center">

        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-400">

          Conversation History

        </p>

        <h2 className="mt-2 text-3xl font-semibold tracking-tight text-white">

          History

        </h2>

        <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-400">

          Questions and coding-help conversations stay here. Project-generation

          requests are stored only in My Projects.

        </p>

      </div>



      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

        <p className="text-xs text-slate-500">

          {history.length} saved conversation{history.length === 1 ? "" : "s"}

        </p>

        <button

          type="button"

          onClick={onRefresh}

          disabled={loading || deleteLoading}

          className={`${buttonStyles.ghost} px-3 py-2 text-xs`}

        >

          {loading ? "Refreshing..." : "Refresh History"}

        </button>

      </div>



      {error && (

        <div

          role="alert"

          className="mb-5 rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3 text-sm text-red-300"

        >

          {error}

        </div>

      )}



      {loading && history.length === 0 ? (

        <div className="rounded-3xl border border-white/10 bg-white/[0.025] p-10 text-center sm:p-14">

          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-blue-400/20 border-t-blue-300" />

          <h3 className="mt-5 text-lg font-semibold text-white">

            Loading history...

          </h3>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">

            Retrieving your saved questions and coding-help conversations.

          </p>

        </div>

      ) : history.length === 0 ? (

        <div className="rounded-3xl border border-dashed border-white/10 bg-white/[0.025] p-10 text-center sm:p-14">

          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-blue-400/20 bg-blue-400/10">

            <svg

              className="h-8 w-8 text-blue-300"

              viewBox="0 0 24 24"

              fill="none"

              stroke="currentColor"

              strokeWidth="1.7"

              strokeLinecap="round"

              strokeLinejoin="round"

              aria-hidden="true"

            >

              <path d="M3 12a9 9 0 1 0 2.6-6.4L3 8" />

              <path d="M3 4v4h4M12 7v5l3 2" />

            </svg>

          </div>

          <h3 className="mt-5 text-lg font-semibold text-white">

            No conversations yet

          </h3>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">

            Ask a question or request coding help from Home. Saved

            conversations will appear here automatically.

          </p>

        </div>

      ) : (

        <div className="space-y-4">

          {history.map((item) => {

            const historyId = item.history_id || item.id;

            const intentLabel =

              item.intent === "CODING_HELP" ? "Coding Help" : "Answer";

            const createdAt = item.created_at || item.createdAt;

            const isSelected = selectedHistoryId === historyId;



            return (

              <article

                key={historyId}

                className={`rounded-2xl border bg-white/[0.025] p-5 shadow-xl shadow-black/10 backdrop-blur-xl transition sm:p-6 ${

                  isSelected ? "border-blue-400/30" : "border-white/10"

                }`}

              >

                <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

                  <div className="min-w-0 flex-1">

                    <div className="flex flex-wrap items-center gap-2">

                      <span className="rounded-full border border-blue-300/15 bg-blue-400/10 px-3 py-1 text-[11px] font-semibold text-blue-300">

                        {intentLabel}

                      </span>

                      <span className="text-xs text-slate-600">

                        {formatHistoryDate(createdAt)}

                      </span>

                    </div>



                    <h3 className="mt-4 break-words text-base font-semibold text-slate-100">

                      {item.user_request || "Untitled conversation"}

                    </h3>

                  </div>



                  <div className="flex shrink-0 flex-wrap gap-2">

                    <button

                      type="button"

                      onClick={() =>

                        isSelected ? onClose() : onView(historyId)

                      }

                      disabled={detailLoading && isSelected}

                      className={`${buttonStyles.secondary} px-3 py-2 text-xs`}

                    >

                      {detailLoading && isSelected

                        ? "Loading..."

                        : isSelected

                          ? "Close"

                          : "View Conversation"}

                    </button>

                    <button

                      type="button"

                      onClick={() => onDelete(historyId)}

                      disabled={deleteLoading}

                      className={`${buttonStyles.danger} px-3 py-2 text-xs`}

                    >

                      {deleteLoading ? "Deleting..." : "Delete"}

                    </button>

                  </div>

                </div>



                {isSelected && (

                  <div className="mt-5 border-t border-white/10 pt-5">

                    {detailError && (

                      <p role="alert" className="text-sm text-red-300">

                        {detailError}

                      </p>

                    )}



                    {detailLoading ? (

                      <p className="text-sm text-slate-400">

                        Loading conversation...

                      </p>

                    ) : selectedHistory ? (

                      <div>

                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">

                          Response

                        </p>

                        <div className="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-slate-300">

                          {selectedHistory.answer || "No response was saved."}

                        </div>

                      </div>

                    ) : !detailError ? (

                      <p className="text-sm text-slate-500">

                        No conversation details are available.

                      </p>

                    ) : null}

                  </div>

                )}

              </article>

            );

          })}

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

            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-400/15 text-lg">

              ✓

            </span>

            <h3 className="text-lg font-bold sm:text-xl">

              Project Generation Complete

            </h3>

          </div>

          <p className="mt-2 text-sm text-slate-300">

            Your project has been successfully generated.

          </p>

          <p className="mt-3 text-xs text-slate-400">

            Project ID:{" "}

            <span className="break-all font-mono text-blue-300">

              {projectId}

            </span>

          </p>

        </div>



        <div className="flex flex-col gap-2 sm:min-w-64 sm:flex-row">

          <button

            type="button"

            onClick={onView}

            className={`${buttonStyles.primary} px-4 py-3 text-sm`}

          >

            View Project

          </button>

          <button

            type="button"

            onClick={onDownload}

            disabled={downloadLoading}

            className={`${buttonStyles.secondary} px-4 py-3 text-sm`}

          >

            {downloadLoading ? "Preparing ZIP..." : "Download ZIP"}

          </button>

        </div>

      </div>

      {error && (

        <p role="alert" className="mt-4 text-sm text-red-300">

          {error}

        </p>

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

        const projectUrl = apiEndpoint(

          `/projects/${encodeURIComponent(projectId)}`,

        );

        const projectResponse = await fetch(projectUrl, {

          signal: controller.signal,

        });

        if (!projectResponse.ok)

          throw new Error("Project could not be loaded.");



        const data = await projectResponse.json();

        if (!Array.isArray(data.files))

          throw new Error("Project response was invalid.");



        if (active) {

          setFiles(data.files);

          setSelectedPath(

            data.files.find((file) => !isHiddenProjectFile(file.path))?.path ||

              "",

          );

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



  const visibleFiles = files.filter((file) => !isHiddenProjectFile(file.path));

  const navigatorEntries = buildProjectNavigatorEntries(visibleFiles);

  const selectedFile = files.find((file) => file.path === selectedPath);



  return (

    <section className="mt-8 overflow-hidden rounded-2xl border border-white/10 bg-slate-900/80 shadow-2xl shadow-black/30">

      <div className="flex flex-col gap-3 border-b border-white/10 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5">

        <div className="min-w-0">

          <p className="text-xs font-semibold uppercase tracking-widest text-blue-400">

            Project Files

          </p>

          <h3 className="mt-1 break-all font-mono text-sm text-slate-200">

            {projectId}

          </h3>

        </div>

        <button

          type="button"

          onClick={onClose}

          className={`${buttonStyles.ghost} self-start px-3 py-2 text-sm sm:self-auto`}

        >

          Close Viewer

        </button>

      </div>



      {loading ? (

        <p className="p-6 text-sm text-slate-400">Loading project files...</p>

      ) : error ? (

        <p role="alert" className="p-6 text-sm text-red-300">

          {error}

        </p>

      ) : visibleFiles.length === 0 ? (

        <p className="p-6 text-sm text-slate-400">

          No previewable project files are available.

        </p>

      ) : (

        <div className="grid min-h-80 lg:grid-cols-[minmax(14rem,0.8fr)_minmax(0,2fr)]">

          <nav

            aria-label="Generated project files"

            className="border-b border-white/10 p-3 lg:border-b-0 lg:border-r"

          >

            <p className="px-2 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">

              Files

            </p>

            <ul className="max-h-[32rem] space-y-1 overflow-auto">

              {navigatorEntries.map((entry) => {

                const depth = Math.min(entry.depth, 8);

                const selected =

                  entry.type === "file" && selectedPath === entry.path;

                return (

                  <li key={`${entry.type}-${entry.path}`}>

                    {entry.type === "folder" ? (

                      <span

                        title={entry.path}

                        className="flex w-full items-center gap-2 truncate py-2 pr-2 font-mono text-xs text-slate-500"

                        style={{ paddingLeft: `${12 + depth * 12}px` }}

                      >

                        <FolderIcon className="h-4 w-4 shrink-0" />

                        <span className="truncate">{entry.name}</span>

                      </span>

                    ) : (

                      <button

                        type="button"

                        onClick={() => setSelectedPath(entry.path)}

                        title={entry.path}

                        aria-label={`Open ${entry.path}`}

                        className={`${buttonStyles.ghost} flex w-full items-center gap-2 truncate py-2 pr-2 text-left font-mono text-xs ${selected ? "bg-blue-400/15 text-blue-200" : "text-slate-400 hover:text-slate-200"}`}

                        style={{ paddingLeft: `${12 + depth * 12}px` }}

                      >

                        <FileIcon className="h-4 w-4 shrink-0" />

                        <span className="truncate">{entry.name}</span>

                      </button>

                    )}

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

              <p className="p-5 text-sm text-slate-400">

                This file cannot be previewed as text.

              </p>

            ) : (

              <pre className="max-h-[32rem] overflow-auto p-4 text-xs leading-5 text-slate-300 sm:p-5">

                <code>{selectedFile?.content ?? ""}</code>

              </pre>

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

            className={`${buttonStyles.secondary} px-4 py-2 text-sm`}

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

            <h3 className="font-bold">Generated Files</h3>



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

            <h3 className="font-bold">Test Results</h3>



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

              <span className="text-sm font-medium">Test Suite</span>



              <span

                className={

                  testSuite.status === "passed"

                    ? "text-emerald-400"

                    : "text-red-400"

                }

              >

                {testSuite.status === "passed" ? "PASSED" : "FAILED"}

              </span>

            </div>



            <div className="mt-4 grid grid-cols-3 gap-2">

              <MiniStat label="Passed" value={testSuite.passed ?? 0} />



              <MiniStat label="Failed" value={testSuite.failed ?? 0} />



              <MiniStat label="Errors" value={testSuite.errors ?? 0} />

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



            <h3 className="mt-1 text-lg font-bold">AI Code Reviewer</h3>

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

            <p className="mb-2 text-sm font-semibold">Suggestions</p>



            <div className="space-y-2">

              {review.suggestions.map((suggestion, index) => (

                <div

                  key={index}

                  className="rounded-lg bg-slate-950/50 px-3 py-2.5 text-xs leading-5 text-slate-400"

                >

                  💡 {suggestion}

                </div>

              ))}

            </div>

          </div>

        )}

      </div>



      {/* Requirements */}

      <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5 sm:p-6">

        <h3 className="font-bold">Requirements</h3>



        <div className="mt-4 grid gap-2 sm:grid-cols-2">

          {(response.requirements || []).map((requirement, index) => (

            <div

              key={index}

              className="flex gap-3 rounded-lg bg-slate-950/50 p-3"

            >

              <span className="text-blue-400">{index + 1}.</span>



              <span className="text-xs leading-5 text-slate-400">

                {requirement}

              </span>

            </div>

          ))}

        </div>

      </div>

    </section>

  );

}



function StatCard({ label, value, icon }) {

  return (

    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4">

      <div className="text-xl">{icon}</div>



      <p className="mt-3 text-2xl font-black">{value}</p>



      <p className="mt-1 text-xs text-slate-500">{label}</p>

    </div>

  );

}



function MiniStat({ label, value }) {

  return (

    <div className="rounded-lg bg-slate-950/60 p-3 text-center">

      <p className="text-lg font-bold">{value}</p>



      <p className="mt-1 text-[10px] uppercase tracking-wider text-slate-600">

        {label}

      </p>

    </div>

  );

}



export default App;



