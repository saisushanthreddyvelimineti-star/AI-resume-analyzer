import { motion } from "framer-motion";
import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const practiceModes = [
  {
    title: "Impact Story",
    prompt: "Coach me to explain my environmental or sustainability impact in an interview using a strong STAR answer.",
    tone: "mint",
  },
  {
    title: "Science Drill",
    prompt: "Start a technical interview focused on environmental science, sustainability analytics, and problem solving. Ask one question at a time.",
    tone: "blue",
  },
  {
    title: "Green Pitch",
    prompt: "Write and coach me through a strong 60-second introduction for an environmental science or sustainability role.",
    tone: "gold",
  },
];

function App() {
  const [status, setStatus] = useState({
    openai_ready: false,
    apify_ready: false,
    analysis_available: true,
    jobs_available: true,
    jarvis_chat_available: true,
    jarvis_voice_ready: false,
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [analysis, setAnalysis] = useState({
    summary: "Upload a PDF resume to unlock Jarvis analysis.",
    gaps: "Your skill gaps will appear here.",
    roadmap: "Your roadmap will appear here.",
    resume_text: "",
  });
  const [analysisReady, setAnalysisReady] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [jarvisBusy, setJarvisBusy] = useState(false);
  const [jobs, setJobs] = useState({ keywords: "", linkedin_jobs: [], naukri_jobs: [] });
  const [jarvisPrompt, setJarvisPrompt] = useState("");
  const [jarvisMessages, setJarvisMessages] = useState([
    {
      role: "assistant",
      content:
        "Gaia online. Upload your resume, then ask for sustainability interview coaching, project storytelling, green career targeting, or impact-focused answer rewrites.",
    },
  ]);
  const [jarvisAudio, setJarvisAudio] = useState(null);
  const [activeView, setActiveView] = useState("analysis");

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((response) => response.json())
      .then((data) => setStatus(data))
      .catch(() => {});
  }, []);

  const profileSignals = useMemo(
    () => [
      { label: "OpenAI", value: status.openai_ready ? "ONLINE" : "OFFLINE" },
      { label: "Apify", value: status.apify_ready ? "ONLINE" : "OFFLINE" },
      { label: "Resume", value: analysisReady ? "MAPPED" : "STANDBY" },
      { label: "Jarvis", value: jarvisBusy ? "SPEAKING" : "IDLE" },
    ],
    [status, analysisReady, jarvisBusy]
  );

  const handleAnalyze = async () => {
    if (!resumeFile) return;
    setLoadingAnalyze(true);
    const formData = new FormData();
    formData.append("resume", resumeFile);
    try {
      const response = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Resume analysis failed.");
      setAnalysis(data);
      setAnalysisReady(true);
      setJobs({ keywords: "", linkedin_jobs: [], naukri_jobs: [] });
      setActiveView("analysis");
      setJarvisMessages([
        {
          role: "assistant",
          content:
            "Profile mapped into the eco-intelligence deck. I can now tailor role targeting, impact storytelling, and interview coaching to your background.",
        },
      ]);
    } catch (error) {
      setJarvisMessages([{ role: "assistant", content: String(error.message || error) }]);
    } finally {
      setLoadingAnalyze(false);
    }
  };

  const handleJobs = async () => {
    setLoadingJobs(true);
    try {
      const response = await fetch(`${API_BASE}/api/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary: analysis.summary }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Job fetch failed.");
      setJobs(data);
      setActiveView("jobs");
    } catch (error) {
      setJobs({ keywords: String(error.message || error), linkedin_jobs: [], naukri_jobs: [] });
    } finally {
      setLoadingJobs(false);
    }
  };

  const playAudio = (audioBase64) => {
    if (!audioBase64) return;
    if (jarvisAudio) jarvisAudio.pause();
    const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
    setJarvisAudio(audio);
    audio.play().catch(() => {});
  };

  const sendJarvisPrompt = async (prompt) => {
    const cleanedPrompt = prompt.trim();
    if (!cleanedPrompt) return;
    setJarvisBusy(true);
    setActiveView("jarvis");
    setJarvisMessages((current) => [...current, { role: "user", content: cleanedPrompt }]);
    setJarvisPrompt("");
    try {
      const response = await fetch(`${API_BASE}/api/jarvis/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          summary: analysis.summary,
          prompt: cleanedPrompt,
          conversation: jarvisMessages,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Jarvis failed.");
      setJarvisMessages((current) => [...current, { role: "assistant", content: data.reply }]);
      playAudio(data.audio_base64);
    } catch (error) {
      setJarvisMessages((current) => [
        ...current,
        { role: "assistant", content: String(error.message || error) },
      ]);
    } finally {
      setJarvisBusy(false);
    }
  };

  const sendVoicePrompt = async (file) => {
    if (!file) return;
    setJarvisBusy(true);
    setActiveView("jarvis");
    const formData = new FormData();
    formData.append("audio", file);
    formData.append("summary", analysis.summary);
    formData.append("conversation", JSON.stringify(jarvisMessages));
    try {
      const response = await fetch(`${API_BASE}/api/jarvis/voice`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Voice coaching failed.");
      setJarvisMessages((current) => [
        ...current,
        { role: "user", content: data.transcript },
        { role: "assistant", content: data.reply },
      ]);
      playAudio(data.audio_base64);
    } catch (error) {
      setJarvisMessages((current) => [
        ...current,
        { role: "assistant", content: String(error.message || error) },
      ]);
    } finally {
      setJarvisBusy(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="grid-overlay" />

      <header className="hero-shell">
        <div className="hero-ambient ambient-a" />
        <div className="hero-ambient ambient-b" />
        <div className="hero-copy-block">
          <div className="eyebrow">GAIA FIELD LAB // ECO INTELLIGENCE STUDIO</div>
          <h1>Shape a cleaner future with an environmental science control deck.</h1>
          <p className="hero-copy">
            Resume intelligence, sustainability storytelling, green-role targeting, and a voice-enabled
            interview copilot inside an immersive eco systems dashboard.
          </p>

          <div className="hero-signal-board">
            <SignalPlate label="Biome Mode" value={activeView.toUpperCase()} />
            <SignalPlate label="Insight Engine" value={analysisReady ? "LIVE" : "SEEDING"} />
            <SignalPlate label="Voice Relay" value={status.jarvis_voice_ready ? "CANOPY" : "TEXT"} />
          </div>

          <div className="hero-command-row">
            <label className="upload-tile">
              <span className="tile-kicker">Field Resume</span>
              <strong>{resumeFile ? resumeFile.name : "Attach resume PDF"}</strong>
              <input type="file" accept=".pdf" onChange={(event) => setResumeFile(event.target.files?.[0] || null)} />
            </label>

            <div className="hero-actions">
              <button onClick={handleAnalyze} disabled={!resumeFile || loadingAnalyze}>
                {loadingAnalyze ? "Analyzing..." : "Analyze Resume"}
              </button>
              <button
                className="secondary"
                onClick={handleJobs}
                disabled={!analysisReady || loadingJobs}
              >
                {loadingJobs ? "Scanning..." : "Job Radar"}
              </button>
            </div>
          </div>

          <div className="hero-pills">
            <span>Climate career mapping</span>
            <span>Eco systems telemetry</span>
            <span>Voice field guide</span>
          </div>
        </div>

        <div className="hero-reactor-panel">
          <EcoMurals />
          <div className="reactor-stage">
            <div className="depth-disc depth-disc-a" />
            <div className="depth-disc depth-disc-b" />
            <div className="floating-cube cube-a" />
            <div className="floating-cube cube-b" />
            <div className="floating-shard shard-a" />
            <div className="floating-shard shard-b" />
          <motion.div
            className={`reactor-box ${jarvisBusy ? "talking" : ""}`}
            animate={{ rotate: jarvisBusy ? 360 : 0 }}
            transition={{ repeat: jarvisBusy ? Infinity : 0, duration: 14, ease: "linear" }}
          >
            <div className="reactor-shadow" />
            <div className="reactor-halo halo-a" />
            <div className="reactor-halo halo-b" />
            <div className="reactor-orbit orbit-a" />
            <div className="reactor-orbit orbit-b" />
            <div className="reactor-ring outer" />
            <div className="reactor-ring middle" />
            <div className="reactor-ring inner" />
            <div className="reactor-crosshair h" />
            <div className="reactor-crosshair v" />
            <motion.div
              className="reactor-core"
              animate={{ scale: jarvisBusy ? [1, 1.08, 1] : 1 }}
              transition={{ duration: 1.2, repeat: jarvisBusy ? Infinity : 0 }}
            >
              <span>{jarvisBusy ? "ACTIVE" : "STABLE"}</span>
            </motion.div>
            <div className="reactor-node node-a" />
            <div className="reactor-node node-b" />
            <div className="reactor-node node-c" />
            <div className="reactor-node node-d" />
          </motion.div>
          </div>

          <div className="telemetry-panel">
            {profileSignals.map((signal) => (
              <div key={signal.label} className="telemetry-tile">
                <span>{signal.label}</span>
                <strong>{signal.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </header>

      <section className="nav-shell">
        <div className="nav-tabs">
          {[
            ["analysis", "Impact Lab"],
            ["jobs", "Green Radar"],
            ["jarvis", "Gaia Guide"],
          ].map(([key, label]) => (
            <button
              key={key}
              className={`tab-button ${activeView === key ? "active" : ""}`}
              onClick={() => setActiveView(key)}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="status-strip">
          <span>PROFILE MAP {analysisReady ? "ROOTED" : "PENDING"}</span>
          <span>VOICE {status.jarvis_voice_ready ? "READY" : "TEXT ONLY"}</span>
          <span>CAREER FEEDS {status.apify_ready ? "LIVE" : "DEMO READY"}</span>
        </div>
      </section>

      <div className="dashboard-grid">
        <aside className="left-rail">
          <Panel title="Ecosystem Feed" subtitle="Live habitat state">
            <div className="rail-stack">
              <MetricCard label="OpenAI" value={status.openai_ready ? "Flowing" : "Fallback"} />
              <MetricCard label="Apify" value={status.apify_ready ? "Flowing" : "Seeded"} />
              <MetricCard label="Profile" value={analysisReady ? "Mapped" : "Waiting"} />
              <MetricCard label="Gaia" value={jarvisBusy ? "Guiding" : "Idle"} />
            </div>
          </Panel>

          <Panel title="Impact Layer" subtitle="What this deck emphasizes">
            <div className="signal-list">
              <div className="signal-item">
                <span className="signal-dot mint" />
                <div>
                  <strong>Resume stays rooted</strong>
                  <p>Your analysis remains visible while Gaia guides you.</p>
                </div>
              </div>
              <div className="signal-item">
                <span className="signal-dot blue" />
                <div>
                  <strong>Green role radar</strong>
                  <p>Career feeds stay separated from coaching and analysis.</p>
                </div>
              </div>
              <div className="signal-item">
                <span className="signal-dot gold" />
                <div>
                  <strong>Field guide coaching</strong>
                  <p>Upload voice, get transcript, critique, and spoken reply.</p>
                </div>
              </div>
            </div>
          </Panel>
        </aside>

        <main className="main-stage">
          {activeView === "analysis" && (
            <section className="stage-panel">
              <div className="section-head">
                <div>
                  <h2>Impact Intelligence Deck</h2>
                  <p>Three focused cards for your profile, growth areas, and future pathway.</p>
                </div>
              </div>
              <div className="cards-grid advanced">
                <InsightCard title="Eco Profile" copy={analysis.summary} tone="summary" />
                <InsightCard title="Growth Zones" copy={analysis.gaps} tone="gaps" />
                <InsightCard title="Future Pathway" copy={analysis.roadmap} tone="roadmap" />
              </div>
            </section>
          )}

          {activeView === "jobs" && (
            <section className="stage-panel">
              <div className="section-head">
                <div>
                  <h2>Green Opportunity Radar</h2>
                  <p>Targeted keywords and split role feeds for a cleaner, more focused search flow.</p>
                </div>
              </div>
              <div className="keywords-shell">
                <span>Generated Impact Keywords</span>
                <strong>{jobs.keywords || "No keyword sweep executed yet."}</strong>
              </div>
              <div className="jobs-grid">
                <JobsColumn title="LinkedIn Canopy" jobs={jobs.linkedin_jobs} linkKey="link" />
                <JobsColumn title="Naukri Current" jobs={jobs.naukri_jobs} linkKey="url" />
              </div>
            </section>
          )}

          {activeView === "jarvis" && (
            <section className="stage-panel">
              <div className="section-head">
                <div>
                  <h2>Gaia Guidance Deck</h2>
                  <p>Impact coaching, voice uploads, mission cards, and a calmer environmental UI language.</p>
                </div>
              </div>

              <div className="jarvis-grid advanced">
                <div className="console-shell">
                  <div className="console-header">
                    <span>Guidance Console</span>
                    <strong>{jarvisBusy ? "RESPONDING" : "LISTENING"}</strong>
                  </div>

                  <div className="chat-log">
                    {jarvisMessages.map((message, index) => (
                      <motion.div
                        key={`${message.role}-${index}`}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`chat-bubble ${message.role}`}
                      >
                        <span>{message.role === "assistant" ? "Gaia" : "You"}</span>
                        <p>{message.content}</p>
                      </motion.div>
                    ))}
                  </div>

                  <textarea
                    value={jarvisPrompt}
                    onChange={(event) => setJarvisPrompt(event.target.value)}
                    placeholder="Ask Gaia to coach your impact stories, prepare for sustainability interviews, or rewrite weak answers into stronger mission-driven responses."
                  />

                  <div className="actions advanced">
                    <button onClick={() => sendJarvisPrompt(jarvisPrompt)} disabled={jarvisBusy}>
                      Send Prompt
                    </button>
                    <label className={`voice-upload ${status.jarvis_voice_ready ? "" : "disabled"}`}>
                      <span>Upload Voice Prompt</span>
                      <input
                        type="file"
                        accept="audio/*"
                        disabled={!status.jarvis_voice_ready || jarvisBusy}
                        onChange={(event) => sendVoicePrompt(event.target.files?.[0])}
                      />
                    </label>
                  </div>
                </div>

                <div className="mission-shell">
                  <div className="mission-header">
                    <span>Mission Presets</span>
                    <strong>Gaia Ops</strong>
                  </div>

                  <div className="mission-grid">
                    {practiceModes.map((mode) => (
                      <button
                        key={mode.title}
                        className={`mission-card ${mode.tone}`}
                        onClick={() => sendJarvisPrompt(mode.prompt)}
                        disabled={jarvisBusy}
                      >
                        <small>Quick launch</small>
                        <strong>{mode.title}</strong>
                      </button>
                    ))}
                  </div>

                  <div className="tactical-note">
                    <span>Live field note</span>
                    <p>
                      Best results come after analysis, because Gaia then grounds each answer and critique in your actual profile.
                    </p>
                  </div>

                  <button
                    className="secondary wide"
                    onClick={() => {
                      if (jarvisAudio) jarvisAudio.pause();
                      setJarvisAudio(null);
                      setJarvisMessages([
                        {
                          role: "assistant",
                          content:
                            "Gaia online. Upload your resume, then ask for sustainability interview coaching, project storytelling, green career targeting, or impact-focused answer rewrites.",
                        },
                      ]);
                    }}
                  >
                    Clear Guidance
                  </button>
                </div>
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}

function Panel({ title, subtitle, children }) {
  return (
    <section className="panel">
      <div className="section-head compact">
        <div>
          <h3>{title}</h3>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="metric-card advanced">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}

function SignalPlate({ label, value }) {
  return (
    <div className="signal-plate">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function EcoMurals() {
  return (
    <div className="eco-murals">
      <svg className="eco-card eco-card-wide" viewBox="0 0 320 180" aria-hidden="true">
        <defs>
          <linearGradient id="skyGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#dff7e8" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#7dc3a6" stopOpacity="0.25" />
          </linearGradient>
          <linearGradient id="hillTone" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1d5c45" />
            <stop offset="100%" stopColor="#123e31" />
          </linearGradient>
        </defs>
        <rect width="320" height="180" rx="24" fill="rgba(8,27,19,0.9)" />
        <circle cx="250" cy="46" r="28" fill="url(#skyGlow)" />
        <path d="M0 132 C64 92, 122 100, 174 130 C214 152, 276 150, 320 126 L320 180 L0 180 Z" fill="url(#hillTone)" />
        <path d="M0 148 C56 118, 114 124, 164 148 C214 170, 270 168, 320 146 L320 180 L0 180 Z" fill="#0d2c23" />
        <path d="M160 60 L170 108" stroke="#9fe7b6" strokeWidth="4" strokeLinecap="round" />
        <path d="M170 84 C148 72, 146 56, 160 50 C170 50, 176 58, 170 84 Z" fill="#8fe09f" />
        <path d="M167 92 C188 82, 196 66, 186 52 C174 50, 166 60, 167 92 Z" fill="#74c888" />
      </svg>
      <svg className="eco-card eco-card-tall" viewBox="0 0 180 220" aria-hidden="true">
        <rect width="180" height="220" rx="24" fill="rgba(9,30,21,0.9)" />
        <circle cx="92" cy="86" r="46" fill="none" stroke="#7fd09a" strokeWidth="2" strokeDasharray="6 8" />
        <circle cx="92" cy="86" r="28" fill="rgba(153,231,181,0.15)" stroke="#bdebc7" strokeWidth="2" />
        <path d="M92 46 L92 126" stroke="#dff7e8" strokeOpacity="0.6" />
        <path d="M52 86 L132 86" stroke="#dff7e8" strokeOpacity="0.35" />
        <path d="M90 104 C70 82, 64 64, 84 50 C100 52, 104 70, 90 104 Z" fill="#7fd09a" />
        <path d="M95 116 C118 97, 124 72, 108 58 C88 58, 84 84, 95 116 Z" fill="#4b9c6b" />
        <path d="M36 178 C64 144, 118 144, 144 178" fill="none" stroke="#7fd09a" strokeWidth="3" />
      </svg>
    </div>
  );
}

function InsightCard({ title, copy, tone }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`insight-card ${tone}`}
    >
      <div className="insight-kicker">AI analysis</div>
      <h3>{title}</h3>
      <p>{copy}</p>
    </motion.div>
  );
}

function JobsColumn({ title, jobs, linkKey }) {
  return (
    <div className="jobs-column">
      <div className="jobs-column-head">
        <h3>{title}</h3>
      </div>
      {jobs?.length ? (
        jobs.map((job, index) => (
          <a className="job-card" key={`${job.title || "job"}-${index}`} href={job[linkKey] || "#"} target="_blank" rel="noreferrer">
            <small>Role lock</small>
            <strong>{job.title || "Untitled role"}</strong>
            <span>{job.companyName || "Unknown company"}</span>
            <span>{job.location || "Location not provided"}</span>
          </a>
        ))
      ) : (
        <div className="empty-state card-empty">No roles loaded yet.</div>
      )}
    </div>
  );
}

export default App;
