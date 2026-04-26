import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { useMagnetic, useScrollReveal } from "./hooks";
import aiPortraitReference from "./assets/ai-portrait-reference.png";

const reveal = {
  hidden: { opacity: 0, y: 34, scale: 0.98 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.72, ease: [0.16, 1, 0.3, 1] } },
};

export function CursorAura({ x, y }) {
  return (
    <motion.div
      style={{ x, y }}
      className="pointer-events-none fixed left-0 top-0 z-50 hidden h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border border-plasma/25 bg-plasma/5 blur-sm lg:block"
    />
  );
}

export function FloatingNavbar({ sections, theme, onThemeToggle }) {
  return (
    <motion.nav
      initial={false}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="fixed left-1/2 top-4 z-40 flex w-[min(92vw,980px)] -translate-x-1/2 items-center justify-between rounded-full border border-white/10 bg-white/[0.06] px-3 py-2 shadow-2xl shadow-black/30 backdrop-blur-2xl"
    >
      <a href="#home" className="flex items-center gap-3 rounded-full px-3 py-2">
        <span className="grid h-9 w-9 place-items-center rounded-full bg-plasma/15 text-plasma shadow-neon">AI</span>
        <span className="hidden font-display text-sm tracking-[0.22em] text-white sm:block">RESUME CORE</span>
      </a>
      <div className="hidden items-center gap-1 md:flex">
        {sections.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className="rounded-full px-4 py-2 text-sm font-semibold text-slate-300 transition hover:bg-white/10 hover:text-white"
          >
            {section.label}
          </a>
        ))}
      </div>
      <button
        type="button"
        onClick={onThemeToggle}
        className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-bold text-white transition hover:border-plasma/50 hover:shadow-neon"
      >
        {theme === "dark" ? "Light" : "Dark"}
      </button>
    </motion.nav>
  );
}

export function HeroSection() {
  const magneticRef = useMagnetic(0.18);
  const particles = useMemo(
    () =>
      Array.from({ length: 34 }, (_, index) => ({
        id: index,
        left: `${(index * 29) % 100}%`,
        top: `${(index * 47) % 100}%`,
        delay: index * 0.08,
        size: 3 + (index % 5),
      })),
    [],
  );

  return (
    <section id="home" className="relative grid min-h-[calc(100vh-96px)] items-center overflow-hidden py-12">
      {particles.map((particle) => (
        <motion.span
          key={particle.id}
          className="absolute rounded-full bg-plasma shadow-neon"
          style={{ left: particle.left, top: particle.top, width: particle.size, height: particle.size }}
          animate={{ y: [-18, 18, -18], opacity: [0.25, 1, 0.25], scale: [1, 1.8, 1] }}
          transition={{ duration: 4.5 + (particle.id % 6), delay: particle.delay, repeat: Infinity, ease: "easeInOut" }}
        />
      ))}

      <div className="grid items-center gap-10 lg:grid-cols-[1fr_0.9fr]">
        <div className="relative z-10">
          <motion.div
            variants={reveal}
            initial={false}
            animate="visible"
            className="mb-5 inline-flex rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 font-display text-xs tracking-[0.32em] text-plasma shadow-neon"
          >
            PERSONAL AI MOCK INTERVIEWER
          </motion.div>
          <motion.h1
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.08 }}
            className="max-w-4xl font-display text-5xl font-black uppercase leading-[0.92] tracking-[-0.06em] text-white sm:text-7xl lg:text-8xl"
          >
            AI Mock Interviewer
          </motion.h1>
          <motion.p
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.18 }}
            className="mt-7 max-w-2xl text-xl leading-8 text-slate-300"
          >
            Upload your resume, paste a target job description, and practise with a personalized voice interviewer that has a visible face.
          </motion.p>
          <motion.div
            initial={false}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.28 }}
            className="mt-9 flex flex-wrap gap-4"
          >
            <a
              ref={magneticRef}
              href="#upload"
              className="distort-button relative overflow-hidden rounded-full bg-gradient-to-r from-plasma via-cyan-200 to-ion px-7 py-4 font-display text-sm font-black uppercase tracking-[0.2em] text-slate-950 shadow-neon transition will-change-transform"
            >
              Upload Resume
            </a>
            <a href="#coach" className="rounded-full border border-white/15 bg-white/10 px-7 py-4 font-display text-sm font-black uppercase tracking-[0.2em] text-white backdrop-blur-xl transition hover:border-plasma/50 hover:shadow-neon">
              Start Interview
            </a>
          </motion.div>
        </div>

        <motion.div
          initial={false}
          animate={{ opacity: 1, rotateX: 0, rotateY: 0, scale: 1 }}
          transition={{ duration: 0.9, delay: 0.2 }}
          className="relative mx-auto w-full max-w-[620px]"
        >
          <ThirdPersonInterviewScene speaking={false} listening={false} candidateName="Candidate" />
        </motion.div>
      </div>
    </section>
  );
}

export function ResumeUpload({
  uploadedFile,
  setUploadedFile,
  atsInput,
  onAtsInputChange,
  isAnalyzing,
  error,
  status,
  analysisStatus,
  analysisReady,
}) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);
  const { ref, controls } = useScrollReveal();
  const inputId = "resume-pdf-upload";

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) setUploadedFile(file);
  };

  const openPicker = () => {
    if (inputRef.current) {
      inputRef.current.value = "";
      inputRef.current.click();
    }
  };

  return (
    <motion.section id="upload" ref={ref} variants={reveal} initial="hidden" animate={controls} className="scroll-mt-28 py-14 lg:py-20">
      <SectionTitle kicker="Neural intake" title="Upload resume for instant signal extraction" />
      <div className="mt-6 grid gap-3 md:grid-cols-3">
        {[
          ["1", "Resume", "Drop a PDF, DOCX, or image resume to start the flow."],
          ["2", "Job description", "Paste the target role and JD before upload for one-pass builder guidance."],
          ["3", "Automatic output", "Analysis, resume builder guidance, and job recommendations are generated automatically."],
        ].map(([step, title, copy]) => (
          <div key={step} className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-4">
            <div className="flex items-center gap-3">
              <span className="grid h-9 w-9 place-items-center rounded-full bg-plasma/15 font-display text-sm font-black text-plasma">
                {step}
              </span>
              <div className="font-display text-sm font-black uppercase tracking-[0.16em] text-white">{title}</div>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-400">{copy}</p>
          </div>
        ))}
      </div>
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`relative mt-8 grid min-h-[340px] overflow-hidden rounded-[2rem] border bg-white/[0.055] p-4 text-center backdrop-blur-2xl transition sm:p-5 ${
          dragging ? "border-plasma shadow-neon" : "border-white/10"
        }`}
      >
        <div className="absolute inset-0 opacity-70">
          <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-plasma to-transparent" />
          <div className="absolute bottom-0 left-0 h-px w-full bg-gradient-to-r from-transparent via-ion to-transparent" />
        </div>
        <div className="relative z-10 mx-auto w-full max-w-[72rem] rounded-[1.8rem] border border-white/10 bg-slate-950/55 p-4 sm:p-6 lg:p-7">
          <div className="grid gap-4 lg:grid-cols-[1.35fr_0.65fr] lg:items-center">
            <div className="text-left">
              <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Resume intake</div>
              <h3 className="mt-3 font-display text-2xl font-black uppercase tracking-[-0.03em] text-white">
                One upload flow from resume and JD to recommendation
              </h3>
              <p className="mt-3 max-w-xl text-sm leading-6 text-slate-400">
                Paste the target job description here before uploading if you want the resume builder to align itself to the exact role in the same pass. If you skip it, the system falls back to a benchmark automatically.
              </p>
            </div>
            <div className="rounded-[1.5rem] border border-plasma/20 bg-plasma/10 p-4 text-left">
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">Accepted files</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {["PDF", "DOCX", "PNG", "JPG"].map((item) => (
                  <span key={item} className="rounded-full border border-white/10 bg-white/[0.06] px-3 py-1 text-xs font-bold uppercase tracking-[0.14em] text-slate-200">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <input
            id={inputId}
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.png,.jpg,.jpeg,.webp,.bmp,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,image/*"
            className="relative z-10 mt-5 w-full rounded-2xl border border-plasma/30 bg-slate-950/70 p-4 text-sm font-bold text-slate-100 file:mr-4 file:rounded-full file:border-0 file:bg-gradient-to-r file:from-plasma file:to-ion file:px-5 file:py-3 file:font-display file:text-xs file:font-black file:uppercase file:tracking-[0.18em] file:text-slate-950 hover:border-plasma/60"
            onChange={(event) => {
              setUploadedFile(event.target.files?.[0] || null);
              event.target.value = "";
            }}
          />
          <div className="mt-5 grid gap-3 text-left">
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                Target role and job description for one-pass builder guidance
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-400">
                Paste the real role and JD here before uploading the resume if you want the system to analyze, build role-ready guidance, and recommend jobs automatically in one run.
              </p>
            </div>
            <input
              value={atsInput.targetRole}
              onChange={(event) => onAtsInputChange((current) => ({ ...current, targetRole: event.target.value }))}
              placeholder="Target role, e.g. Data Analyst, Backend Developer"
              className="rounded-2xl border border-white/10 bg-slate-950/65 px-4 py-3 text-slate-100 outline-none transition focus:border-plasma/60"
            />
            <textarea
              value={atsInput.jobDescription}
              onChange={(event) => onAtsInputChange((current) => ({ ...current, jobDescription: event.target.value }))}
              placeholder="Paste the job description here so the resume builder targets the real role as soon as the resume is uploaded."
              className="min-h-36 rounded-3xl border border-white/10 bg-slate-950/65 p-4 text-sm leading-7 text-slate-100 outline-none transition focus:border-plasma/60"
            />
          </div>
        </div>
        <AnimatePresence mode="wait">
          {uploadedFile ? (
            <motion.div key="success" initial={{ opacity: 0, scale: 0.88 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }} className="mt-8">
              <motion.div
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                className="mx-auto grid h-24 w-24 place-items-center rounded-full border border-plasma/40 bg-plasma/10 shadow-neon"
              >
                <svg viewBox="0 0 64 64" className="h-12 w-12 text-plasma">
                  <motion.path d="M18 33 L28 43 L47 20" fill="none" stroke="currentColor" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.55 }} />
                </svg>
              </motion.div>
              <h3 className="mt-6 font-display text-2xl font-black text-white">{uploadedFile.name}</h3>
              <p className="mt-2 text-slate-400">
                {isAnalyzing
                  ? "Automatic analysis is running now. Resume-builder guidance and job recommendations will load in the dashboard."
                  : analysisReady
                    ? "Automatic analysis completed. Review the builder match, skill gaps, and job recommendations below."
                    : "File selected. Processing starts automatically."}
              </p>
              <div className="mt-7 flex flex-wrap justify-center gap-3">
                <label
                  htmlFor={inputId}
                  className="cursor-pointer rounded-full border border-white/15 bg-white/10 px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-white hover:border-plasma/50"
                >
                  Change Resume
                </label>
              </div>
            </motion.div>
          ) : (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mt-8">
              <div className="mx-auto grid h-24 w-24 place-items-center rounded-3xl border border-white/10 bg-white/10 text-4xl shadow-ion">+</div>
              <h3 className="mt-6 font-display text-2xl font-black text-white">Drag and drop your resume</h3>
              <p className="mt-2 text-slate-400">
                Upload PDF, DOCX, or image resumes. Add the target job description above if you want the system to analyze, build role-ready guidance, and recommend jobs in one automatic pass.
              </p>
              <label
                htmlFor={inputId}
                className="mt-7 inline-flex cursor-pointer rounded-full bg-gradient-to-r from-plasma to-ion px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-slate-950 shadow-neon"
              >
                Choose Resume
              </label>
              <button
                type="button"
                onClick={openPicker}
                className="ml-3 mt-7 rounded-full border border-white/15 bg-white/10 px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-white hover:border-plasma/50"
              >
                Open File Browser
              </button>
              <p className="mt-4 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                If the button does not open, use the native file field above or drag your resume onto this box.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/[0.055] p-4 text-sm text-slate-300">
          Backend:{" "}
          <span className={status ? "font-bold text-plasma" : "font-bold text-ember"}>
            {status ? "Connected" : "Not detected"}
          </span>
        </div>
        <div
          className={`rounded-2xl border p-4 text-sm font-bold ${
            analysisReady
              ? "border-plasma/40 bg-plasma/10 text-plasma"
              : isAnalyzing
                ? "border-solar/40 bg-solar/10 text-yellow-100"
                : "border-white/10 bg-white/[0.055] text-slate-300"
          }`}
        >
          Status: {analysisStatus}
        </div>
        {error && (
          <div className="rounded-2xl border border-ember/40 bg-ember/10 p-4 text-sm font-bold text-orange-100 md:col-span-2">
            {error}
          </div>
        )}
      </div>
    </motion.section>
  );
}

export function AnalysisDashboard({
  uploadedFile,
  isAnalyzing,
  analysisReady,
  analysis,
  error,
  jobs,
  isLoadingJobs,
  resumeBuilderReport,
  autoTarget,
  atsInput,
  builderContext,
  onAtsInputChange,
  isBuildingResume,
}) {
  const { ref, controls } = useScrollReveal();
  const resumeLines = analysis?.resume_text
    ? analysis.resume_text.split(/\r?\n/).filter(Boolean).slice(0, 12)
    : [
        uploadedFile ? uploadedFile.name : "No resume analyzed yet",
        "Upload a PDF resume to start the automatic intake flow.",
        "The extracted resume text will appear here after analysis.",
      ];

  return (
    <motion.section id="dashboard" ref={ref} variants={reveal} initial="hidden" animate={controls} className="scroll-mt-28 py-14 lg:py-20">
      <SectionTitle kicker="Analysis cockpit" title="Split-screen resume preview and AI insight cards" />
      <div className="mt-6 rounded-[1.8rem] border border-white/10 bg-white/[0.04] p-4 sm:p-5">
        <div className="grid gap-3 md:grid-cols-4">
          {[
            ["Analysis", analysisReady ? "Ready" : isAnalyzing ? "Running" : "Pending"],
            ["Builder", resumeBuilderReport ? `${resumeBuilderReport.score}%` : isBuildingResume ? "Building" : "Waiting"],
            ["Jobs", jobs?.linkedin_jobs?.length || jobs?.indeed_jobs?.length ? "Loaded" : isLoadingJobs ? "Loading" : "Waiting"],
            ["Target role", autoTarget?.target_role || "Not set"],
          ].map(([label, value]) => (
            <div key={label} className="rounded-[1.25rem] border border-white/10 bg-slate-950/45 p-4">
              <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</div>
              <div className="mt-2 text-sm font-bold text-white">{value}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-6 grid gap-6 xl:grid-cols-[0.82fr_1.18fr]">
        <GlassCard className="min-h-[620px]">
          <div className="mb-5 flex items-center justify-between">
            <span className="font-display text-xs tracking-[0.28em] text-plasma">RESUME PREVIEW</span>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">{uploadedFile?.name || "No file loaded"}</span>
          </div>
          <div className="space-y-4 rounded-3xl border border-white/10 bg-slate-950/50 p-5">
            {(isAnalyzing ? Array.from({ length: 11 }) : resumeLines).map((line, index) => (
              <div key={`${line || "line"}-${index}`} className="relative overflow-hidden rounded-2xl bg-white/10">
                <div className={`min-h-4 ${isAnalyzing ? "w-full" : "w-full"} rounded-2xl bg-white/15 px-3 py-2 text-left text-sm text-slate-300`}>
                  {!isAnalyzing && line}
                </div>
                {isAnalyzing && <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />}
              </div>
            ))}
          </div>
          <ResumeAiArtwork analysisReady={analysisReady} isAnalyzing={isAnalyzing} jobs={jobs} />
        </GlassCard>
        <ResumeBuilderPanel
          analysisReady={analysisReady}
          autoTarget={autoTarget}
          atsInput={atsInput}
          builderContext={builderContext}
          onAtsInputChange={onAtsInputChange}
          resumeBuilderReport={resumeBuilderReport}
          isBuildingResume={isBuildingResume}
        />
        <GlassCard>
          <div className="rounded-3xl border border-white/10 bg-white/[0.055] p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-display text-lg font-black text-white">Job Recommendations</h3>
                <p className="mt-1 text-slate-400">
                  {jobs?.keywords || "Matching roles will load automatically after resume analysis."}
                </p>
              </div>
              <div className="rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma">
                {isLoadingJobs ? "Smart matching..." : jobs?.mode ? `${jobs.mode} mode` : "Recommendations"}
              </div>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              <JobList title="LinkedIn" jobs={jobs?.linkedin_jobs || []} linkKey="link" />
              <JobList title="Indeed" jobs={jobs?.indeed_jobs || []} linkKey="url" />
            </div>
          </div>
          {error && (
            <div className="mt-5 rounded-2xl border border-ember/40 bg-ember/10 p-4 text-sm font-bold text-orange-100">
              {error}
            </div>
          )}
        </GlassCard>
      </div>
    </motion.section>
  );
}

function ResumeAiArtwork({ analysisReady, isAnalyzing, jobs }) {
  return (
    <div className="mt-5 overflow-hidden rounded-[2rem] border border-white/10 bg-[linear-gradient(180deg,rgba(6,10,26,0.98)_0%,rgba(6,10,26,0.94)_38%,rgba(5,8,19,0.98)_100%)] shadow-[0_28px_90px_rgba(2,6,23,0.45)]">
      <div className="px-5 py-6">
        <div className="overflow-hidden rounded-[1.8rem] border border-white/10 bg-slate-950/60">
          <img
            src={aiPortraitReference}
            alt="AI visual reference"
            className="block h-auto w-full object-cover"
          />
        </div>
      </div>
    </div>
  );
}

function AgenticIntakePanel({ report }) {
  const plan = report?.planner?.plan || [];
  const finalRecommendation = report?.final_recommendation || {};
  const verification = report?.verification || {};
  const primaryRole = finalRecommendation?.primary_role || finalRecommendation?.north_star || "Role direction pending";
  const toolsUsedCount = Array.isArray(finalRecommendation?.tools_used) ? finalRecommendation.tools_used.length : 0;

  return (
    <GlassCard className="mt-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-2xl">
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Agentic Intake</div>
          <h3 className="mt-3 font-display text-2xl font-black uppercase tracking-[-0.03em] text-white">
            The upload flow is now planned by an agent
          </h3>
          <p className="mt-3 text-sm leading-7 text-slate-400">
            Instead of running a fixed sequence only, the planner chooses tools, executes them, verifies missing inputs, and returns the next best actions for the candidate.
          </p>
        </div>
        <span className="rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma">
          {report?.mode || "agentic"}
        </span>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-4">
        {[
          ["Primary role", primaryRole],
          ["Confidence", verification?.confidence || "pending"],
          ["Tools executed", `${toolsUsedCount}`],
          ["Next step", finalRecommendation?.next_best_step || "Waiting for agent output"],
        ].map(([label, value]) => (
          <div key={label} className="rounded-[1.25rem] border border-white/10 bg-slate-950/45 p-4">
            <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</div>
            <div className="mt-2 text-sm font-bold leading-6 text-white">{value}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
        <div className="rounded-[1.6rem] border border-white/10 bg-slate-950/40 p-5">
          <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Planner Route</div>
          <div className="mt-4 grid gap-3">
            {plan.map((step, index) => (
              <div key={`${step.tool}-${index}`} className="rounded-[1.25rem] border border-white/10 bg-white/[0.04] p-4">
                <div className="flex items-center gap-3">
                  <span className="grid h-8 w-8 place-items-center rounded-full bg-plasma/15 text-xs font-black text-plasma">
                    {index + 1}
                  </span>
                  <div className="font-display text-sm font-black uppercase tracking-[0.16em] text-white">
                    {step.tool.replaceAll("_", " ")}
                  </div>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-400">{step.reason}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <MiniList title="Priority Actions" items={finalRecommendation.priority_actions} />
          <MiniList title="Input Gaps" items={verification.input_gaps} />
          <MiniList title="Tools Used" items={finalRecommendation.tools_used} />
          <MiniList title="Job Search Keywords" items={finalRecommendation.job_search_keywords} />
        </div>
      </div>
    </GlassCard>
  );
}

function ResumeBuilderPanel({
  analysisReady,
  autoTarget,
  atsInput,
  builderContext,
  onAtsInputChange,
  resumeBuilderReport,
  isBuildingResume,
}) {
  const downloadReport = (format) => {
    if (!resumeBuilderReport) return;

    const rows = [
      `Resume Builder Match: ${resumeBuilderReport.score}%`,
      `Match Level: ${resumeBuilderReport.match_level}`,
      `Target Role: ${resumeBuilderReport.target_role}`,
      "",
      `Matched Skills: ${(resumeBuilderReport.matched_skills || []).join(", ")}`,
      `Missing Skills: ${(resumeBuilderReport.missing_skills || []).join(", ")}`,
      "",
      "Suggested Roles:",
      ...(resumeBuilderReport.suggested_roles || []).map((item) => `- ${item}`),
      "",
      "Improvement Tips:",
      ...(resumeBuilderReport.improvement_tips || []).map((item) => `- ${item}`),
      "",
      "Interview Questions:",
      ...(resumeBuilderReport.interview_questions || []).map((item) => `- ${item}`),
      "",
      `LinkedIn Headline: ${resumeBuilderReport.linkedin_headline || ""}`,
      "",
      "Cover Letter:",
      resumeBuilderReport.cover_letter || "",
    ];

    let content = rows.join("\n");
    let mime = "text/plain";
    let extension = "txt";

    if (format === "json") {
      content = JSON.stringify(resumeBuilderReport, null, 2);
      mime = "application/json";
      extension = "json";
    }

    if (format === "csv") {
      const csvRows = [
        ["Resume Builder Match", resumeBuilderReport.score],
        ["Match Level", resumeBuilderReport.match_level],
        ["Target Role", resumeBuilderReport.target_role],
        ["Matched Skills", (resumeBuilderReport.matched_skills || []).join("; ")],
        ["Missing Skills", (resumeBuilderReport.missing_skills || []).join("; ")],
        ["Suggested Roles", (resumeBuilderReport.suggested_roles || []).join("; ")],
        [],
        ["Improvement Tips"],
        ...(resumeBuilderReport.improvement_tips || []).map((item) => [item]),
        [],
        ["Interview Questions"],
        ...(resumeBuilderReport.interview_questions || []).map((item) => [item]),
      ];
      content = csvRows.map((row) => row.map((cell) => `"${String(cell || "").replaceAll('"', '""')}"`).join(",")).join("\n");
      mime = "text/csv";
      extension = "csv";
    }

    if (format === "html") {
      content = `<!doctype html><html><head><meta charset="utf-8"><title>Resume Builder Report</title><style>body{font-family:Arial;padding:32px;line-height:1.55}h1{color:#0f766e}.score{font-size:42px;font-weight:800}</style></head><body><h1>Resume Builder Report</h1><div class="score">${resumeBuilderReport.score}%</div><p><strong>${resumeBuilderReport.match_level}</strong> for ${resumeBuilderReport.target_role}</p><h2>Matched Skills</h2><p>${(resumeBuilderReport.matched_skills || []).join(", ")}</p><h2>Missing Skills</h2><p>${(resumeBuilderReport.missing_skills || []).join(", ")}</p><h2>Improvement Tips</h2><ul>${(resumeBuilderReport.improvement_tips || []).map((item) => `<li>${item}</li>`).join("")}</ul><h2>Interview Questions</h2><ul>${(resumeBuilderReport.interview_questions || []).map((item) => `<li>${item}</li>`).join("")}</ul><h2>LinkedIn Headline</h2><p>${resumeBuilderReport.linkedin_headline || ""}</p><h2>Cover Letter</h2><p>${(resumeBuilderReport.cover_letter || "").replaceAll("\n", "<br/>")}</p></body></html>`;
      mime = "text/html";
      extension = "html";
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `resume-builder-report.${extension}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const manualWordCount = atsInput?.jobDescription?.trim()
    ? atsInput.jobDescription.trim().split(/\s+/).filter(Boolean).length
    : 0;
  const matchedCount = resumeBuilderReport?.matched_skills?.length || 0;
  const missingCount = resumeBuilderReport?.missing_skills?.length || 0;
  const scoreSourceLabel = builderContext?.source === "manual" ? "Manual job description" : "Benchmark job description";
  const activeTargetRole = builderContext?.targetRole || resumeBuilderReport?.target_role || autoTarget?.target_role || "No role selected";
  const benchmarkRole =
    autoTarget?.target_role || (isBuildingResume ? "Deriving best-fit role..." : "Target role will be generated automatically.");
  const benchmarkDescription =
    autoTarget?.job_description ||
    (isBuildingResume ? "Generating role-aligned resume-builder benchmark..." : "A matching job description will appear automatically after resume analysis.");

  return (
    <GlassCard className="xl:row-span-2">
      <div className="grid gap-7">
        <div className="rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.06] via-white/[0.03] to-transparent p-6 sm:p-7">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div className="max-w-2xl">
              <div className="font-display text-[11px] uppercase tracking-[0.3em] text-plasma">Resume Builder AI</div>
              <h3 className="mt-3 font-display text-[2rem] font-black uppercase tracking-[-0.05em] text-white sm:text-[2.4rem]">
              Build role-ready resume guidance
              </h3>
              <p className="mt-4 max-w-xl text-sm leading-7 text-slate-300 sm:text-[15px]">
                This section turns the uploaded resume and job description into a practical builder report: matched skills, missing skills, role suggestions, interview prompts, and reusable application copy.
              </p>
            </div>
            <div className="grid w-full gap-3 sm:w-auto sm:grid-cols-3">
              {[
                ["Benchmark", autoTarget?.target_role ? "Ready" : "Pending"],
                ["Job Description", manualWordCount ? `${manualWordCount} words` : "Add real JD"],
                ["Latest Match", resumeBuilderReport ? `${resumeBuilderReport.score}%` : "Not built"],
              ].map(([label, value]) => (
                <div key={label} className="rounded-[1.25rem] border border-white/10 bg-slate-950/55 px-4 py-3 shadow-[0_16px_40px_rgba(2,6,23,0.28)]">
                  <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">{label}</div>
                  <div className="mt-2 text-sm font-bold leading-6 text-white">{value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-5">
          <div className="rounded-[1.9rem] border border-plasma/15 bg-gradient-to-br from-plasma/12 via-plasma/8 to-transparent p-6">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="font-display text-[10px] uppercase tracking-[0.24em] text-plasma">Step 1</div>
                  <h4 className="mt-2 font-display text-2xl font-black uppercase tracking-[-0.04em] text-white">
                    Auto-generated role benchmark
                  </h4>
                </div>
                <span className="rounded-full border border-plasma/20 bg-slate-950/55 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-plasma">
                  Fallback
                </span>
              </div>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">
                This gives the builder a clean baseline right after upload. Use it when you do not have a real target job description yet.
              </p>
              <div className="mt-5 grid gap-4 lg:grid-cols-[0.38fr_0.62fr]">
                <div className="rounded-[1.45rem] border border-white/10 bg-slate-950/55 p-5">
                  <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Suggested target role</div>
                  <div className="mt-3 text-base font-bold leading-7 text-white">{benchmarkRole}</div>
                </div>
                <div className="rounded-[1.45rem] border border-white/10 bg-slate-950/55 p-5">
                  <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Generated benchmark description</div>
                  <p className="mt-3 max-h-56 overflow-y-auto pr-2 text-sm leading-7 text-slate-300">
                    {benchmarkDescription}
                  </p>
                </div>
              </div>
          </div>

          <div className="rounded-[1.95rem] border border-white/10 bg-gradient-to-br from-slate-950/72 via-slate-950/58 to-slate-950/44 p-6">
            {resumeBuilderReport ? (
              <div>
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">Step 2</div>
                    <h4 className="mt-2 font-display text-[1.9rem] font-black uppercase tracking-[-0.04em] text-white">
                      Resume builder results
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {["txt", "json", "csv", "html"].map((format) => (
                      <button
                        key={format}
                        type="button"
                        onClick={() => downloadReport(format)}
                        className="rounded-full border border-plasma/30 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma"
                      >
                        {format}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mt-6 grid gap-4 lg:grid-cols-[0.4fr_0.6fr]">
                  <div className="rounded-[1.7rem] border border-plasma/20 bg-gradient-to-br from-plasma/14 via-ion/8 to-transparent p-6">
                    <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">Match score</div>
                    <div className="mt-3 font-display text-7xl font-black leading-none text-white">{resumeBuilderReport.score}</div>
                    <div className="mt-3 text-sm font-bold uppercase tracking-[0.18em] text-plasma">
                      {resumeBuilderReport.match_level} / {resumeBuilderReport.target_role}
                    </div>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    {[
                      ["Scored against", activeTargetRole],
                      ["Score source", scoreSourceLabel],
                      ["Required skills", `${resumeBuilderReport.required_skills?.length || 0}`],
                      ["Suggested roles", `${resumeBuilderReport.suggested_roles?.length || 0}`],
                      ["Matched skills", `${matchedCount}`],
                      ["Missing skills", `${missingCount}`],
                    ].map(([label, value]) => (
                      <div key={label} className="rounded-[1.35rem] border border-white/10 bg-white/[0.05] p-4">
                        <div className="text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">{label}</div>
                        <div className="mt-2 text-sm font-bold leading-6 text-white">{value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
                  <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-5">
                    <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">Builder Comparison</div>
                    <div className="mt-4 space-y-4">
                      <KeywordChipGroup title="Job Description Skills" items={resumeBuilderReport.job_description_keywords} variant="neutral" />
                      <KeywordChipGroup title="Matched In Resume" items={resumeBuilderReport.matched_skills} variant="match" />
                      <KeywordChipGroup title="Missing From Resume" items={resumeBuilderReport.missing_skills} variant="missing" />
                      <KeywordChipGroup title="Suggested Roles" items={resumeBuilderReport.suggested_roles} variant="neutral" />
                    </div>
                  </div>
                  <div className="grid gap-4 md:grid-cols-2">
                    <MiniList title="Improvement Tips" items={resumeBuilderReport.improvement_tips} />
                    <MiniList title="Required Skills" items={resumeBuilderReport.required_skills} />
                    <MiniList title="Interview Questions" items={resumeBuilderReport.interview_questions} />
                    <MiniList title="Resume Skills Detected" items={resumeBuilderReport.user_skills} />
                  </div>
                </div>

                  <div className="mt-6 grid gap-4">
                    <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-5">
                      <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">LinkedIn Headline</div>
                      <p className="mt-3 text-sm leading-7 text-slate-200">{resumeBuilderReport.linkedin_headline}</p>
                    </div>
                    <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-5">
                    <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">Cover Letter Draft</div>
                    <p className="mt-3 whitespace-pre-line text-sm leading-7 text-slate-300">{resumeBuilderReport.cover_letter}</p>
                  </div>
                </div>

                  <div className="mt-6 rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-5">
                    <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">Learning Plan</div>
                    <div className="mt-3 grid max-h-[48rem] gap-3 overflow-y-auto pr-2">
                      {(resumeBuilderReport.learning_plan || []).map((resource) => (
                        <div
                          key={resource.skill}
                          className="rounded-[1.35rem] border border-white/10 bg-white/[0.055] p-4"
                        >
                          <div className="font-bold text-white">{resource.skill}</div>
                          <div className="mt-3 grid gap-2">
                            {(resource.courses || []).map((course) => (
                              <a
                                key={`${resource.skill}-${course.url}`}
                                href={course.url}
                                target="_blank"
                              rel="noreferrer"
                              className="rounded-xl border border-white/10 bg-slate-950/45 p-3 transition hover:border-plasma/40"
                            >
                              <div className="text-sm font-bold text-white">{course.title}</div>
                              <div className="mt-1 text-xs uppercase tracking-[0.14em] text-plasma">{course.provider}</div>
                              <div className="mt-2 text-sm text-slate-400">{course.cost}</div>
                            </a>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="grid min-h-[480px] place-items-center text-center">
                <div className="max-w-md">
                  <div className="font-display text-5xl font-black text-plasma">Builder</div>
                  <p className="mt-4 text-sm leading-7 text-slate-400">
                    Upload a resume first, then paste the real job description here to generate a resume-builder report around an actual target role.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </GlassCard>
  );
}

export function AgenticConsole({ analysis, analysisReady, apiBase }) {
  const { ref, controls } = useScrollReveal();
  const [goal, setGoal] = useState("Find suitable jobs, identify gaps, recommend courses, and prepare me for interviews.");
  const [targetRole, setTargetRole] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [location, setLocation] = useState("United Kingdom");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState(null);

  const runAgent = async () => {
    setBusy(true);
    setError("");

    try {
      const response = await fetch(`${apiBase}/api/agentic/workflow`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          summary: analysis?.summary || "",
          resume_text: analysis?.resume_text || "",
          prompt: goal,
          target_role: targetRole,
          job_description: jobDescription,
          location,
          conversation: [],
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Agentic workflow failed.");
      }
      setReport(data);
    } catch (caught) {
      setError(caught.message || "Agentic workflow failed.");
    } finally {
      setBusy(false);
    }
  };

  const trace = report?.tool_trace || [];
  const finalRecommendation = report?.final_recommendation || {};
  const verification = report?.verification || {};

  return (
    <motion.section id="agentic" ref={ref} variants={reveal} initial="hidden" animate={controls} className="scroll-mt-28 py-16">
      <div className="mt-8 grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
        <GlassCard>
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Agent Goal</div>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            This controller plans the workflow, chooses tools, runs them, verifies assumptions, and returns a trace.
          </p>
          <div className="mt-5 grid gap-3">
            <textarea
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              className="min-h-32 rounded-3xl border border-white/10 bg-slate-950/60 p-4 text-slate-100 outline-none focus:border-plasma/60"
            />
            <input
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              placeholder="Target role, or leave open for any job"
              className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-slate-100 outline-none focus:border-plasma/60"
            />
            <input
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="Location"
              className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-slate-100 outline-none focus:border-plasma/60"
            />
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder="Optional: paste a job description so the agent can run ATS scoring."
              className="min-h-40 rounded-3xl border border-white/10 bg-slate-950/60 p-4 text-slate-100 outline-none focus:border-plasma/60"
            />
            <button
              type="button"
              onClick={runAgent}
              disabled={busy}
              className="rounded-full bg-gradient-to-r from-plasma to-ion px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-slate-950 shadow-neon disabled:cursor-not-allowed disabled:opacity-50"
            >
              {busy ? "Agents Running..." : "Run Agentic AI"}
            </button>
            {!analysisReady && (
              <div className="rounded-2xl border border-solar/30 bg-solar/10 p-3 text-sm text-yellow-100">
                Resume analysis is recommended. The agent can still run, but evidence will be weaker.
              </div>
            )}
            {error && <div className="rounded-2xl border border-ember/40 bg-ember/10 p-3 text-sm text-orange-100">{error}</div>}
          </div>
        </GlassCard>

        <GlassCard>
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Agentic Run Trace</div>
              <h3 className="mt-2 font-display text-2xl font-black text-white">
                {report ? finalRecommendation.north_star : "No agent run yet"}
              </h3>
            </div>
            {report && (
              <span className="rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma">
                {report.mode}
              </span>
            )}
          </div>

          {report ? (
            <div className="grid gap-5">
              <div className="rounded-3xl border border-white/10 bg-slate-950/45 p-4">
                <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Planner</div>
                <div className="mt-3 grid gap-2">
                  {(report.planner?.plan || []).map((step, index) => (
                    <div key={`${step.tool}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">
                      <div className="text-xs font-black uppercase tracking-[0.16em] text-plasma">{index + 1}. {step.tool}</div>
                      <p className="mt-1 text-sm leading-6 text-slate-300">{step.reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                {trace.map((item, index) => (
                  <div key={`${item.tool}-${index}`} className="rounded-3xl border border-white/10 bg-white/[0.055] p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-display text-xs uppercase tracking-[0.2em] text-plasma">{item.tool}</div>
                      <div className={`text-xs font-black uppercase ${item.status === "completed" ? "text-plasma" : "text-yellow-100"}`}>
                        {item.status}
                      </div>
                    </div>
                    <p className="mt-3 line-clamp-5 text-sm leading-6 text-slate-300">
                      {item.reason || JSON.stringify(item.output || {}).slice(0, 320)}
                    </p>
                  </div>
                ))}
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <MiniList title="Priority Actions" items={finalRecommendation.priority_actions} />
                <MiniList title="Verification Checks" items={verification.checks} />
                <MiniList title="Input Gaps" items={verification.input_gaps} />
                <MiniList title="Tools Used" items={finalRecommendation.tools_used} />
              </div>

              <div className="rounded-3xl border border-solar/30 bg-solar/10 p-4">
                <div className="font-display text-xs uppercase tracking-[0.22em] text-yellow-100">Next Interview Question</div>
                <p className="mt-2 text-sm leading-6 text-slate-200">{finalRecommendation.interview_next_question}</p>
              </div>
            </div>
          ) : (
            <div className="grid min-h-[480px] place-items-center text-center">
              <div>
                <div className="font-display text-5xl font-black text-plasma">AGENT</div>
                <p className="mt-3 max-w-md text-slate-400">
                  Run the agent to see planner decisions, executed tools, verification, and next actions.
                </p>
              </div>
            </div>
          )}
        </GlassCard>
      </div>
    </motion.section>
  );
}

export function OpenSourceStack({ apiBase }) {
  const { ref, controls } = useScrollReveal();
  const [stack, setStack] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${apiBase}/api/local-voice/stack`)
      .then((response) => response.json())
      .then((data) => setStack(data))
      .catch((caught) => setError(caught.message || "Unable to load local stack status."));
  }, [apiBase]);

  const configured = stack?.configured || {};
  const recommended = stack?.recommended_stack || {};
  const optionalKeys = stack?.api_keys?.optional || [];

  return (
    <motion.section id="local-stack" ref={ref} variants={reveal} initial="hidden" animate={controls} className="scroll-mt-28 py-16">
      <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <GlassCard>
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Free Open-Source Stack</div>
          <h3 className="mt-3 font-display text-3xl font-black uppercase tracking-[-0.04em] text-white">
            Jarvis-style mock interviewer pipeline
          </h3>
          <p className="mt-3 leading-7 text-slate-400">
            {stack?.goal || "Voice, wake word, local LLM, local TTS, webcam cues, scoring, and memory."}
          </p>
          <div className="mt-5 rounded-3xl border border-plasma/20 bg-plasma/10 p-4">
            <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">API Key Requirement</div>
            <p className="mt-2 text-sm leading-6 text-slate-200">
              {stack?.api_key_answer || "No API key is required for the fully local free stack."}
            </p>
          </div>
          {error && <div className="mt-4 rounded-2xl border border-ember/40 bg-ember/10 p-3 text-sm text-orange-100">{error}</div>}
        </GlassCard>

        <GlassCard>
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Pipeline Components</div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {Object.entries(recommended).map(([key, value]) => (
              <div key={key} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4">
                <div className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">{key.replaceAll("_", " ")}</div>
                <div className="mt-2 text-sm font-bold text-slate-100">{value}</div>
              </div>
            ))}
          </div>
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {Object.entries(configured).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-slate-950/45 p-3">
                <span className="text-sm capitalize text-slate-300">{key.replaceAll("_", " ")}</span>
                <span className={`text-xs font-black uppercase tracking-[0.14em] ${value ? "text-plasma" : "text-yellow-100"}`}>
                  {value ? "Ready" : "Setup"}
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Build Phases</div>
          <div className="mt-4 grid gap-4">
            {(stack?.phases || []).map((phase) => (
              <div key={phase.name} className="rounded-3xl border border-white/10 bg-white/[0.055] p-4">
                <div className="font-display text-sm font-black uppercase tracking-[0.18em] text-white">{phase.name}</div>
                <MiniList title="Tasks" items={phase.items} />
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard>
          <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Optional API Keys</div>
          <div className="mt-4 grid gap-3">
            {optionalKeys.map((item) => (
              <div key={item.name} className="rounded-2xl border border-white/10 bg-slate-950/45 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="font-bold text-white">{item.name}</div>
                  <span className={`text-xs font-black uppercase tracking-[0.14em] ${item.currently_configured ? "text-plasma" : "text-slate-400"}`}>
                    {item.currently_configured ? "Configured" : "Optional"}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-400">{item.needed_for}</p>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </motion.section>
  );
}

export function InterviewCoach({
  analysis,
  analysisReady,
  apiBase,
  autoTarget,
  atsContext,
  messages,
  isCoachBusy,
  onAppError,
  onSendPrompt,
  onSendVoice,
  voiceReady,
}) {
  const { ref, controls } = useScrollReveal();
  const [prompt, setPrompt] = useState("");
  const [candidateName, setCandidateName] = useState("Candidate");
  const [targetRole, setTargetRole] = useState("");
  const [interviewStyle, setInterviewStyle] = useState("Balanced");
  const [difficulty, setDifficulty] = useState("Medium");
  const [jobDescription, setJobDescription] = useState("");
  const [interviewProfile, setInterviewProfile] = useState(null);
  const [profileBusy, setProfileBusy] = useState(false);
  const [scoreBusy, setScoreBusy] = useState(false);
  const [answerScores, setAnswerScores] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [voiceError, setVoiceError] = useState("");
  const voiceInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const speechSupported = typeof window !== "undefined" && ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);
  const lastAssistantMessage = [...messages].reverse().find((message) => message.role !== "user")?.content || "";
  const activeRole = targetRole.trim() || atsContext?.targetRole || autoTarget?.target_role || "Your target role";
  const latestScore = answerScores[0] || null;

  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    const seededRole = atsContext?.targetRole || autoTarget?.target_role || "";
    const seededJobDescription = atsContext?.jobDescription || autoTarget?.job_description || "";

    setTargetRole((current) => (current.trim() ? current : seededRole));
    setJobDescription((current) => (current.trim() ? current : seededJobDescription));
  }, [
    autoTarget?.job_description,
    autoTarget?.target_role,
    atsContext?.jobDescription,
    atsContext?.targetRole,
  ]);

  const buildPersonalizedPrompt = (rawPrompt) => {
    const name = candidateName.trim() || "Candidate";
    return [
      `Personalize this mock interview for ${name}, targeting this job: ${targetRole.trim() || "any job role"}.`,
      `Interviewer style: ${interviewStyle}.`,
      `Difficulty: ${difficulty}.`,
      interviewProfile?.realtime_instructions ? `Session instructions: ${interviewProfile.realtime_instructions}` : "",
      "Behave like a voice assistant: concise, conversational, one question at a time, and wait for my next answer before moving on.",
      rawPrompt,
    ].filter(Boolean).join("\n");
  };

  const interviewActions = [
    {
      label: "Next Question",
      prompt: "Continue the mock interview. Ask the next question only, adapted to my previous answer and resume gaps.",
    },
    {
      label: "Evaluate Answer",
      prompt: "Evaluate my latest interview answer. Score clarity, technical depth, confidence, STAR structure, and give a stronger rewritten answer.",
    },
    {
      label: "Hard Mode",
      prompt: "Run a high-pressure round. Ask one difficult follow-up question that tests depth, tradeoffs, and real project ownership.",
    },
  ];

  const sendPreset = (presetPrompt) => {
    onSendPrompt(buildPersonalizedPrompt(presetPrompt));
  };

  const sendPrompt = () => {
    onSendPrompt(buildPersonalizedPrompt(prompt));
    setPrompt("");
  };

  const generateInterviewProfile = async () => {
    setProfileBusy(true);
    onAppError?.("");

    try {
      const response = await fetch(`${apiBase}/api/interview/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_summary: analysis?.summary || "",
          resume_text: analysis?.resume_text || "",
          target_role: targetRole,
          job_description: jobDescription,
          difficulty,
          interviewer_style: interviewStyle,
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Interview plan generation failed.");
      }

      setInterviewProfile(data);
      return data;
    } catch (error) {
      onAppError?.(error.message || "Interview plan generation failed.");
      return null;
    } finally {
      setProfileBusy(false);
    }
  };

  const startPlannedInterview = async () => {
    const profile = interviewProfile || (await generateInterviewProfile());
    if (!profile) return;
    const firstQuestion = profile.question_bank?.[0]?.question || "Walk me through your background for this role.";
    onSendPrompt(
      buildPersonalizedPrompt(
        [
          "Start the live mock interview using this structured interview profile.",
          JSON.stringify(profile).slice(0, 2600),
          `Ask this first question only: ${firstQuestion}`,
        ].join("\n"),
      ),
    );
  };

  const scoreLatestAnswer = async () => {
    const latestUserAnswer = [...messages].reverse().find((message) => message.role === "user")?.content || "";
    const latestQuestion = [...messages].reverse().find((message) => message.role !== "user")?.content || "";

    if (!latestUserAnswer.trim()) {
      onAppError?.("No candidate answer found to score yet.");
      return;
    }

    const profile = interviewProfile || (await generateInterviewProfile());
    if (!profile) return;

    setScoreBusy(true);
    onAppError?.("");

    try {
      const response = await fetch(`${apiBase}/api/interview/score-answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interview_profile: profile,
          question: latestQuestion,
          answer: latestUserAnswer,
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Answer scoring failed.");
      }

      setAnswerScores((current) => [data, ...current].slice(0, 4));
    } catch (error) {
      onAppError?.(error.message || "Answer scoring failed.");
    } finally {
      setScoreBusy(false);
    }
  };

  const startLiveVoice = () => {
    setVoiceError("");
    setLiveTranscript("");

    if (!speechSupported) {
      setVoiceError("Live microphone dictation is not supported in this browser. Use Chrome or Edge, or upload an audio file.");
      return;
    }

    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new Recognition();
    recognition.lang = "en-GB";
    recognition.interimResults = true;
    recognition.continuous = false;

    let finalTranscript = "";
    recognition.onstart = () => setIsListening(true);
    recognition.onerror = () => {
      setVoiceError("Microphone capture failed. Check browser microphone permission and try again.");
      setIsListening(false);
    };
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript || "")
        .join(" ")
        .trim();
      finalTranscript = transcript;
      setLiveTranscript(transcript);
    };
    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
      if (finalTranscript.trim()) {
        onSendPrompt(buildPersonalizedPrompt(`My spoken answer or request: ${finalTranscript.trim()}`));
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopLiveVoice = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  return (
    <motion.section id="coach" ref={ref} variants={reveal} initial="hidden" animate={controls} className="scroll-mt-28 py-16 lg:py-24">
      <SectionTitle kicker="Personal Interview AI" title="Human avatar interviewer with live confidence coaching" />
      <div className="mt-8 grid gap-3 md:grid-cols-4">
        {[
          ["Human avatar", "A speaking face reacts while the interviewer listens, asks questions, and coaches your answers."],
          ["Role-aware prep", "Resume signals, target role, and job description shape the question flow automatically."],
          ["Answer scoring", "Score each answer for clarity, confidence, structure, technical depth, and examples."],
          ["Confidence coaching", "Live camera review gives posture, eye-contact, calmness, and presence suggestions."],
        ].map(([title, copy]) => (
          <div key={title} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4">
            <div className="font-display text-xs uppercase tracking-[0.18em] text-plasma">{title}</div>
            <p className="mt-2 text-sm leading-6 text-slate-400">{copy}</p>
          </div>
        ))}
      </div>
      <div className="mt-8 grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
        <GlassCard className="grid place-items-center">
          <div className="w-full rounded-[1.85rem] border border-plasma/20 bg-[linear-gradient(160deg,rgba(8,18,36,0.92),rgba(4,8,18,0.98))] p-4 sm:p-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="max-w-xl">
                <div className="font-display text-xs uppercase tracking-[0.26em] text-plasma">Live Interviewer</div>
                <h3 className="mt-3 font-display text-2xl font-black uppercase tracking-[-0.03em] text-white">
                  Your personal human-style coach
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-400">
                  The interviewer face reacts live while your role, job description, and resume shape the session.
                </p>
              </div>
              <div className="rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma">
                {isListening ? "Listening" : isCoachBusy ? "Responding" : "Ready"}
              </div>
            </div>
            <div className="mt-5 overflow-hidden rounded-[1.7rem] border border-white/10 bg-slate-950/55">
              <ThirdPersonInterviewScene
                speaking={isCoachBusy}
                listening={isListening}
                candidateName={candidateName}
                compact
              />
              <div className="grid gap-3 border-t border-white/10 bg-slate-950/75 p-4 md:grid-cols-3">
                {[
                  ["Coach Voice", voiceReady ? "Speech ready" : "Text only"],
                  ["Interview Brief", interviewProfile ? "Role tailored" : "Build a brief"],
                  ["Latest Score", latestScore ? `${latestScore.overall}/5` : "Waiting"],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">
                    <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</div>
                    <div className="mt-2 text-sm font-bold leading-6 text-white">{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-6 grid w-full gap-4 md:grid-cols-2">
            <div>
              <label className="font-display text-xs uppercase tracking-[0.24em] text-plasma" htmlFor="candidate-name">
                Candidate Name
              </label>
              <input
                id="candidate-name"
                value={candidateName}
                onChange={(event) => setCandidateName(event.target.value)}
                className="mt-3 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 font-bold text-white outline-none focus:border-plasma/60"
              />
            </div>
            <div>
              <label className="font-display text-xs uppercase tracking-[0.24em] text-plasma" htmlFor="target-role">
                Job Title
              </label>
              <input
                id="target-role"
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
                placeholder="Type any job title, e.g. Nurse, Teacher, Accountant, Chef, Data Analyst"
                className="mt-3 w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 font-bold text-white outline-none focus:border-plasma/60"
              />
            </div>
            <div className="md:col-span-2 grid gap-4">
              <div className="grid grid-cols-3 gap-2">
                {["Friendly", "Balanced", "Strict"].map((style) => (
                  <button
                    key={style}
                    type="button"
                    onClick={() => setInterviewStyle(style)}
                    className={`rounded-2xl border px-3 py-2 text-xs font-black uppercase tracking-[0.12em] transition ${
                      interviewStyle === style
                        ? "border-plasma/60 bg-plasma/20 text-plasma shadow-neon"
                        : "border-white/10 bg-white/[0.055] text-slate-300 hover:border-plasma/40"
                    }`}
                  >
                    {style}
                  </button>
                ))}
              </div>
              <div className="grid grid-cols-3 gap-2">
                {["Easy", "Medium", "Hard"].map((level) => (
                  <button
                    key={level}
                    type="button"
                    onClick={() => setDifficulty(level)}
                    className={`rounded-2xl border px-3 py-2 text-xs font-black uppercase tracking-[0.12em] transition ${
                      difficulty === level
                        ? "border-solar/60 bg-solar/20 text-yellow-100 shadow-ember"
                        : "border-white/10 bg-white/[0.055] text-slate-300 hover:border-solar/40"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
              <textarea
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the target job description here for role-specific questions and missing keyword detection."
                className="min-h-28 rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm text-slate-100 outline-none focus:border-plasma/60"
              />
            </div>
          </div>
          <div className="mt-5 grid w-full grid-cols-2 gap-3">
            {[
              ["Readiness", analysisReady ? "Resume-linked" : "Generic mode"],
              ["Mic", speechSupported ? "Browser live" : "Upload only"],
              ["Mode", isListening ? "Listening" : isCoachBusy ? "Responding" : "Ready"],
              ["Role", activeRole],
            ].map(([label, value]) => (
              <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.055] p-3 text-center">
                <div className="font-display text-[10px] uppercase tracking-[0.2em] text-slate-400">{label}</div>
                <div className="mt-1 text-sm font-black text-plasma">{value}</div>
              </div>
            ))}
          </div>
          <div className="mt-5 grid w-full gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={generateInterviewProfile}
              disabled={profileBusy}
              className="rounded-full border border-plasma/30 bg-plasma/10 px-5 py-4 font-display text-xs font-black uppercase tracking-[0.18em] text-plasma shadow-neon disabled:cursor-not-allowed disabled:opacity-50"
            >
              {profileBusy ? "Building Brief..." : "Build Interview Brief"}
            </button>
            <button
              type="button"
              onClick={startPlannedInterview}
              disabled={isCoachBusy || profileBusy}
              className="rounded-full bg-gradient-to-r from-plasma to-ion px-5 py-4 font-display text-xs font-black uppercase tracking-[0.18em] text-slate-950 shadow-neon disabled:cursor-not-allowed disabled:opacity-50"
            >
              Start Mock Interview
            </button>
            <button
              type="button"
              onClick={isListening ? stopLiveVoice : startLiveVoice}
              disabled={isCoachBusy}
              className="rounded-full border border-white/10 bg-white/[0.055] px-5 py-4 font-display text-xs font-black uppercase tracking-[0.18em] text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isListening ? "Stop Listening" : "Talk To Coach"}
            </button>
            <button
              type="button"
              onClick={() => voiceInputRef.current?.click()}
              disabled={!voiceReady || isCoachBusy}
              className="rounded-full border border-solar/30 bg-solar/10 px-5 py-4 font-display text-xs font-black uppercase tracking-[0.18em] text-yellow-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Upload Voice Clip
            </button>
          </div>
          <input
            ref={voiceInputRef}
            hidden
            type="file"
            accept="audio/*"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onSendVoice(file);
              event.target.value = "";
            }}
          />
          {(liveTranscript || voiceError) && (
            <div className={`mt-4 max-w-sm rounded-2xl border p-4 text-center text-sm ${voiceError ? "border-ember/40 bg-ember/10 text-orange-100" : "border-plasma/25 bg-plasma/10 text-slate-200"}`}>
              {voiceError || liveTranscript}
            </div>
          )}
        </GlassCard>
        <GlassCard>
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="font-display text-xs uppercase tracking-[0.28em] text-plasma">Coach Console</div>
              <h3 className="mt-2 font-display text-2xl font-black uppercase tracking-[-0.03em] text-white">
                Personalized interview session
              </h3>
            </div>
            <div className="rounded-full border border-plasma/25 bg-plasma/10 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-plasma">
              {analysisReady ? "Resume linked" : "General prep"}
            </div>
          </div>
          <div className="mb-5 grid gap-3 md:grid-cols-3">
            <InterviewMetricCard label="Style" value={interviewStyle} accent="plasma" />
            <InterviewMetricCard label="Difficulty" value={difficulty} accent="solar" />
            <InterviewMetricCard label="Latest Score" value={latestScore ? `${latestScore.overall}/5` : "Waiting"} accent={latestScore ? "ion" : "neutral"} />
          </div>
          <div className="mb-5 grid gap-3 md:grid-cols-4">
            {interviewActions.map((action) => (
              <button
                key={action.label}
                type="button"
                onClick={() => sendPreset(action.prompt)}
                disabled={isCoachBusy}
                className="rounded-2xl border border-plasma/20 bg-plasma/10 px-3 py-4 text-center font-display text-xs font-black uppercase tracking-[0.16em] text-plasma transition hover:border-plasma/60 hover:shadow-neon disabled:cursor-not-allowed disabled:opacity-50"
              >
                {action.label}
              </button>
            ))}
          </div>
          {interviewProfile && (
            <div className="mb-5 grid gap-4 xl:grid-cols-[1fr_1fr]">
              <div className="rounded-3xl border border-plasma/20 bg-plasma/10 p-4">
                <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Interview Brief</div>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  <MiniList title="Strengths" items={interviewProfile.strengths} />
                  <MiniList title="Gaps" items={interviewProfile.gaps} />
                  <MiniList title="Focus" items={interviewProfile.focus_areas} />
                  <MiniList title="Missing Keywords" items={interviewProfile.missing_keywords} />
                </div>
              </div>
              <div className="rounded-3xl border border-white/10 bg-slate-950/45 p-4">
                <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Question Bank</div>
                <div className="mt-3 max-h-48 space-y-3 overflow-auto pr-2">
                  {(interviewProfile.question_bank || []).slice(0, 5).map((item, index) => {
                    const question = typeof item === "string" ? item : item.question;
                    const round = typeof item === "string" ? `Round ${index + 1}` : item.round || `Round ${index + 1}`;
                    return (
                    <div key={`${question}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">
                      <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">{round}</div>
                      <p className="mt-1 text-sm leading-6 text-slate-200">{question}</p>
                    </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
          <div className="mb-5 rounded-3xl border border-white/10 bg-slate-950/45 p-4">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <div className="font-display text-xs uppercase tracking-[0.24em] text-plasma">Interviewer Signal</div>
                <p className="mt-1 text-sm text-slate-400">Lead with ownership, keep answers specific, and connect each example back to {activeRole}.</p>
              </div>
              <motion.span
                animate={{ opacity: [0.4, 1, 0.4] }}
                transition={{ duration: 1.2, repeat: Infinity }}
                className="h-3 w-3 rounded-full bg-plasma shadow-neon"
              />
            </div>
            <p className="line-clamp-3 text-sm leading-6 text-slate-300">
              {lastAssistantMessage || "Start a mock interview to receive the first adaptive question."}
            </p>
          </div>
          <div className="max-h-[380px] space-y-4 overflow-auto pr-2">
            {messages.map((message, index) => (
              <ChatBubble
                key={`${message.role}-${index}`}
                role={message.role === "user" ? "You" : "AI Coach"}
                text={message.content}
                user={message.role === "user"}
              />
            ))}
            <div className="rounded-3xl border border-plasma/20 bg-plasma/10 p-5">
              <div className="mb-3 text-xs font-bold uppercase tracking-[0.22em] text-plasma">AI Coach</div>
              {isCoachBusy ? (
                <div className="flex gap-2">
                  {[0, 1, 2].map((dot) => (
                    <motion.span key={dot} animate={{ y: [0, -8, 0] }} transition={{ delay: dot * 0.12, duration: 0.6, repeat: Infinity }} className="h-3 w-3 rounded-full bg-plasma" />
                  ))}
                </div>
              ) : (
                <p className="text-slate-200">
                  {analysisReady
                    ? "Ask a question about your resume, interviews, job targeting, or answer rewrites."
                    : "Analyze your resume first for personalized coaching."}
                </p>
              )}
            </div>
          </div>
          <div className="mt-5 grid gap-3">
            <textarea
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder={`Example: Interview me for ${targetRole.trim() || "my chosen job"}. Ask one question, wait, then score my answer.`}
              className="min-h-28 rounded-3xl border border-white/10 bg-slate-950/60 p-4 text-slate-100 outline-none focus:border-plasma/60"
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={sendPrompt}
                disabled={isCoachBusy || !prompt.trim()}
                className="rounded-full bg-gradient-to-r from-plasma to-ion px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-slate-950 shadow-neon disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isCoachBusy ? "Thinking..." : "Send To Coach"}
              </button>
              <button
                type="button"
                onClick={scoreLatestAnswer}
                disabled={scoreBusy || profileBusy}
                className="rounded-full border border-solar/30 bg-solar/10 px-6 py-3 font-display text-sm font-black uppercase tracking-[0.2em] text-yellow-100 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {scoreBusy ? "Scoring..." : "Score Latest Answer"}
              </button>
            </div>
            {latestScore && (
              <div className="rounded-3xl border border-solar/30 bg-solar/10 p-5">
                <div className="mb-3 font-display text-xs uppercase tracking-[0.22em] text-yellow-100">Latest Scorecard</div>
                <Scorecard score={latestScore} />
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </motion.section>
  );
}

function CameraInterviewMonitor({ apiBase, jobTitle }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const recognitionRef = useRef(null);
  const transcriptRef = useRef("");
  const [cameraActive, setCameraActive] = useState(false);
  const [faceStatus, setFaceStatus] = useState("Camera off");
  const [mood, setMood] = useState("neutral");
  const [score, setScore] = useState(0);
  const [eyeContact, setEyeContact] = useState("Good");
  const [confidence, setConfidence] = useState(30);
  const [transcript, setTranscript] = useState("");
  const [currentQ, setCurrentQ] = useState(0);
  const [micError, setMicError] = useState("");
  const [presenceReport, setPresenceReport] = useState(null);
  const [presenceBusy, setPresenceBusy] = useState(false);
  const [presenceError, setPresenceError] = useState("");

  const role = jobTitle?.trim() || "your chosen job";
  const questions = useMemo(
    () => [
      `Tell me about yourself for a ${role} interview.`,
      `Why should we hire you for this ${role} role?`,
      `What strengths make you suitable for ${role}?`,
      `Describe a challenge you faced that is relevant to ${role}.`,
      `Where do you see yourself in 5 years as a ${role}?`,
    ],
    [role],
  );

  useEffect(() => {
    transcriptRef.current = transcript;
  }, [transcript]);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
      recognitionRef.current?.abort?.();
    };
  }, []);

  useEffect(() => {
    if (!cameraActive) return undefined;

    let cancelled = false;
    let interval = null;
    let faceapi = null;

    const calculateConfidence = (detectedMood, eye) => {
      const wordCount = transcriptRef.current.trim().split(/\s+/).filter(Boolean).length;
      let speechScore = 0.4;
      if (wordCount > 3) speechScore = 0.6;
      if (wordCount > 8) speechScore = 0.8;
      if (wordCount > 15) speechScore = 1;

      const moodScore = detectedMood === "happy" ? 1 : detectedMood === "neutral" ? 0.6 : 0.3;
      const eyeScore = eye === "Good" ? 1 : eye === "Slightly Off" ? 0.6 : 0.3;
      setConfidence(Math.max(10, Math.round((moodScore * 0.35 + eyeScore * 0.25 + speechScore * 0.4) * 100)));
    };

    const runDetection = async () => {
      try {
        try {
          const moduleName = "face-api.js";
          const module = await import(/* @vite-ignore */ moduleName);
          faceapi = module;
          await Promise.all([
            faceapi.nets.tinyFaceDetector.loadFromUri("/models"),
            faceapi.nets.faceExpressionNet.loadFromUri("/models"),
            faceapi.nets.faceLandmark68Net.loadFromUri("/models"),
          ]);
          if (!cancelled) setFaceStatus("Face tracking active");
        } catch {
          if (!cancelled) setFaceStatus("Camera active. Add face-api.js models in /models for mood and eye-contact tracking.");
        }

        interval = window.setInterval(async () => {
          const video = videoRef.current;
          const canvas = canvasRef.current;
          if (!video || video.readyState < 2) return;

          if (!faceapi) {
            const fallbackConfidence = transcriptRef.current.trim() ? 62 : 35;
            setMood("neutral");
            setEyeContact("Camera Active");
            setConfidence(fallbackConfidence);
            setScore((previous) => previous + 1);
            return;
          }

          const detections = await faceapi
            .detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
            .withFaceExpressions()
            .withFaceLandmarks();

          if (!detections) {
            setEyeContact("No Face");
            setConfidence(20);
            return;
          }

          const expressions = detections.expressions;
          const currentMood = Object.keys(expressions).reduce((a, b) => (expressions[a] > expressions[b] ? a : b));
          setMood(currentMood);

          const landmarks = detections.landmarks;
          const jaw = landmarks.getJawOutline();
          const nose = landmarks.getNose();
          const leftEye = landmarks.getLeftEye();
          const rightEye = landmarks.getRightEye();

          const leftFaceX = jaw[0].x;
          const rightFaceX = jaw[16].x;
          const faceWidth = Math.max(rightFaceX - leftFaceX, 1);
          const faceCenter = (leftFaceX + rightFaceX) / 2;
          const noseX = nose[3].x;
          const noseY = nose[3].y;
          const eyeY = (leftEye[1].y + rightEye[1].y) / 2;
          const horizontal = (noseX - faceCenter) / faceWidth;
          const vertical = (noseY - eyeY) / faceWidth;
          const sizeRatio = detections.detection.box.height / Math.max(video.videoHeight, 1);

          let eye = "Good";
          if (sizeRatio < 0.25) eye = "Too Far";
          else if (vertical > 0.04) eye = "Looking Down";
          else if (horizontal > 0.07) eye = "Looking Right";
          else if (horizontal < -0.07) eye = "Looking Left";
          else if (Math.abs(horizontal) > 0.03) eye = "Slightly Off";

          setEyeContact(eye);
          setScore((previous) => previous + 1);
          calculateConfidence(currentMood, eye);

          if (canvas) {
            const dims = faceapi.matchDimensions(canvas, video, true);
            const resized = faceapi.resizeResults(detections, dims);
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            faceapi.draw.drawDetections(canvas, resized);
          }
        }, 700);
      } catch (error) {
        if (!cancelled) setFaceStatus(error.message || "Camera analysis failed.");
      }
    };

    runDetection();

    return () => {
      cancelled = true;
      if (interval) window.clearInterval(interval);
    };
  }, [cameraActive]);

  const startCamera = async () => {
    setFaceStatus("Starting camera...");
    setMicError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraActive(true);
    } catch (error) {
      setFaceStatus(error.message || "Camera permission failed.");
    }
  };

  const stopCamera = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    const canvas = canvasRef.current;
    canvas?.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
    setCameraActive(false);
    setFaceStatus("Camera off");
  };

  const startMic = () => {
    setMicError("");
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      setMicError("Live speech recognition needs Chrome or Edge.");
      return;
    }

    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      const text = Array.from(event.results)
        .map((result) => result[0]?.transcript || "")
        .join(" ")
        .trim();
      setTranscript(text);
    };
    recognition.onerror = () => setMicError("Mic capture failed. Check browser permission.");
    recognitionRef.current = recognition;
    recognition.start();
  };

  const reset = () => {
    setScore(0);
    setConfidence(30);
    setMood("neutral");
    setEyeContact("Good");
    setTranscript("");
    setPresenceReport(null);
    setPresenceError("");
  };

  const analyzePresence = async () => {
    setPresenceBusy(true);
    setPresenceError("");

    const eyeScore =
      eyeContact === "Good" || eyeContact === "Camera Active"
        ? 0.85
        : eyeContact === "Slightly Off"
          ? 0.62
          : eyeContact === "No Face"
            ? 0.15
            : 0.35;
    const faceDetected = eyeContact !== "No Face" && faceStatus !== "Camera off";
    const confidenceRatio = confidence / 100;
    const wordCount = transcript.trim().split(/\s+/).filter(Boolean).length;

    try {
      const response = await fetch(`${apiBase}/api/interview/presence`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: "browser-camera",
          question_id: `camera-q-${currentQ + 1}`,
          answer_id: `camera-answer-${Date.now()}`,
          frame_window_start: 0,
          frame_window_end: score,
          face_detected: faceDetected,
          face_centered_score: eyeContact === "Good" ? 0.85 : 0.55,
          face_visibility_score: faceDetected ? 0.78 : 0.1,
          eye_contact_score: eyeScore,
          gaze_away_frequency: 1 - eyeScore,
          blink_rate_score: 0.7,
          head_stability_score: eyeContact === "Good" || eyeContact === "Slightly Off" ? 0.75 : 0.45,
          posture_score: faceDetected ? 0.72 : 0.3,
          shoulder_tension_score: confidenceRatio > 0.6 ? 0.72 : 0.48,
          fidget_score: confidenceRatio > 0.6 ? 0.7 : 0.5,
          expression_consistency_score: mood === "neutral" || mood === "happy" ? 0.78 : 0.48,
          smile_naturalness_score: mood === "happy" ? 0.8 : 0.62,
          attention_score: Math.max(0.2, Math.min(0.95, confidenceRatio)),
          stress_signal_score: confidenceRatio < 0.45 ? 0.65 : 0.28,
          calmness_signal_score: confidenceRatio > 0.65 ? 0.78 : 0.52,
          dominant_emotion: mood,
          emotion_distribution: { [mood]: 1 },
          recovery_after_hesitation_score: wordCount > 8 ? 0.72 : 0.5,
          speaking_alignment_score: wordCount > 3 ? 0.72 : 0.45,
          pacing_support_signal: wordCount > 15 ? "Enough speech for presence review" : "Short answer window",
          notable_events: [
            faceStatus,
            `Eye contact: ${eyeContact}`,
            transcript ? "Speech detected" : "No speech transcript yet",
          ],
        }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || "Presence analysis failed.");
      }
      setPresenceReport(data);
    } catch (error) {
      setPresenceError(error.message || "Presence analysis failed.");
    } finally {
      setPresenceBusy(false);
    }
  };

  return (
    <div className="mt-7 w-full rounded-3xl border border-white/10 bg-slate-950/45 p-4">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Confidence And Sentiment Coach</div>
          <h3 className="mt-2 font-display text-xl font-black text-white">{questions[currentQ]}</h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Use your camera and mic to check whether you look calm, centered, and confident while answering.
          </p>
        </div>
        <div className="rounded-full border border-plasma/25 bg-plasma/10 px-3 py-2 text-xs font-bold text-plasma">
          {confidence}%
        </div>
      </div>

      <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-black">
        <video ref={videoRef} autoPlay muted playsInline className="aspect-video w-full object-cover" />
        <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" />
      </div>

      <div className="mt-4 grid gap-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">{faceStatus}</div>
        <div>
          Eye Contact:{" "}
          <span className={eyeContact === "Good" || eyeContact === "Camera Active" ? "font-black text-plasma" : eyeContact === "Slightly Off" ? "font-black text-yellow-100" : "font-black text-orange-100"}>
            {eyeContact}
          </span>
        </div>
        <div className="h-3 overflow-hidden rounded-full bg-white/10">
          <div className="h-full rounded-full bg-gradient-to-r from-plasma to-ion transition-all" style={{ width: `${confidence}%` }} />
        </div>
        <div className="font-bold text-slate-200">
          Mood: {mood} | Score: {score}
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">
          {transcript || "Start speaking to capture your answer..."}
        </div>
        {micError && <div className="rounded-2xl border border-ember/40 bg-ember/10 p-3 text-orange-100">{micError}</div>}
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        <button type="button" onClick={cameraActive ? stopCamera : startCamera} className="rounded-full bg-gradient-to-r from-plasma to-ion px-4 py-3 font-display text-xs font-black uppercase tracking-[0.16em] text-slate-950">
          {cameraActive ? "Stop Camera Review" : "Start Camera Review"}
        </button>
        <button type="button" onClick={startMic} className="rounded-full border border-plasma/30 bg-plasma/10 px-4 py-3 font-display text-xs font-black uppercase tracking-[0.16em] text-plasma">
          Capture Answer
        </button>
        <button type="button" onClick={reset} className="rounded-full border border-white/10 bg-white/[0.055] px-4 py-3 font-display text-xs font-black uppercase tracking-[0.16em] text-white">
          Reset
        </button>
        <button type="button" onClick={() => setCurrentQ((previous) => (previous + 1) % questions.length)} className="rounded-full border border-solar/30 bg-solar/10 px-4 py-3 font-display text-xs font-black uppercase tracking-[0.16em] text-yellow-100">
          Next Prompt
        </button>
      </div>
      <button
        type="button"
        onClick={analyzePresence}
        disabled={presenceBusy}
        className="mt-3 w-full rounded-full border border-solar/30 bg-solar/10 px-4 py-3 font-display text-xs font-black uppercase tracking-[0.16em] text-yellow-100 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {presenceBusy ? "Analyzing Confidence..." : "Analyze Confidence And Sentiment"}
      </button>
      {presenceError && <div className="mt-3 rounded-2xl border border-ember/40 bg-ember/10 p-3 text-sm text-orange-100">{presenceError}</div>}
      {presenceReport && (
        <div className="mt-4 rounded-3xl border border-plasma/20 bg-plasma/10 p-4">
          <div className="flex items-center justify-between gap-3">
            <div className="font-display text-xs uppercase tracking-[0.22em] text-plasma">Interview Presence AI</div>
            <div className="font-display text-2xl font-black text-white">{presenceReport.score_total}/100</div>
          </div>
          {presenceReport.real_time_tip && (
            <div className="mt-3 rounded-2xl border border-solar/30 bg-solar/10 p-3 text-sm font-bold text-yellow-100">
              {presenceReport.real_time_tip}
            </div>
          )}
          <p className="mt-3 text-sm leading-6 text-slate-300">{presenceReport.summary}</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <MiniList title="Strengths" items={presenceReport.strengths} />
            <MiniList title="Improve" items={presenceReport.improvement_areas} />
          </div>
          <div className="mt-3 text-xs leading-5 text-slate-400">{presenceReport.safety_note}</div>
        </div>
      )}
    </div>
  );
}

function KeywordChipGroup({ title, items = [], variant = "neutral" }) {
  const cleanItems = Array.isArray(items) ? items.filter(Boolean).slice(0, 18) : [];
  const toneClass =
    variant === "match"
      ? "border-plasma/25 bg-plasma/10 text-plasma"
      : variant === "missing"
        ? "border-ember/30 bg-ember/10 text-orange-100"
        : "border-white/10 bg-slate-950/45 text-slate-200";

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-3">
      <div className="font-display text-[10px] uppercase tracking-[0.18em] text-slate-400">{title}</div>
      <div className="mt-3 flex flex-wrap gap-2">
        {cleanItems.length ? (
          cleanItems.map((item, index) => (
            <span
              key={`${title}-${item}-${index}`}
              className={`rounded-full border px-3 py-1 text-xs font-bold leading-5 ${toneClass}`}
            >
              {String(item)}
            </span>
          ))
        ) : (
          <span className="text-sm text-slate-500">No keywords captured yet.</span>
        )}
      </div>
    </div>
  );
}

function MiniList({ title, items = [] }) {
  const cleanItems = Array.isArray(items) ? items.filter(Boolean).slice(0, 4) : [];
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-3">
      <div className="font-display text-[10px] uppercase tracking-[0.18em] text-slate-400">{title}</div>
      <div className="mt-2 space-y-2">
        {cleanItems.length ? (
          cleanItems.map((item, index) => (
            <div key={`${title}-${item}-${index}`} className="text-sm leading-5 text-slate-200">
              {String(item)}
            </div>
          ))
        ) : (
          <div className="text-sm text-slate-500">Generate a plan to load this layer.</div>
        )}
      </div>
    </div>
  );
}

function InterviewMetricCard({ label, value, accent = "neutral" }) {
  const accentClass =
    accent === "plasma"
      ? "border-plasma/25 bg-plasma/10 text-plasma"
      : accent === "solar"
        ? "border-solar/25 bg-solar/10 text-yellow-100"
        : accent === "ion"
          ? "border-ion/25 bg-ion/10 text-cyan-100"
          : "border-white/10 bg-white/[0.055] text-slate-200";

  return (
    <div className={`rounded-[1.25rem] border p-4 ${accentClass}`}>
      <div className="text-[10px] font-bold uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-2 text-sm font-bold leading-6 text-white">{value}</div>
    </div>
  );
}

function Scorecard({ score }) {
  const scoreEntries = Object.entries(score?.scores || {});
  return (
    <div>
      <div className="mb-4 flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/45 p-3">
        <span className="text-sm font-bold text-slate-300">Overall</span>
        <span className="font-display text-2xl font-black text-yellow-100">{score?.overall || "0"}/5</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {scoreEntries.map(([label, value]) => (
          <div key={label} className="rounded-xl border border-white/10 bg-white/[0.055] p-3">
            <div className="flex justify-between gap-3 text-sm">
              <span className="capitalize text-slate-300">{label.replaceAll("_", " ")}</span>
              <span className="font-black text-plasma">{value}/5</span>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <MiniList title="Strengths" items={score?.strengths} />
        <MiniList title="Improvements" items={score?.improvements} />
      </div>
      <p className="mt-4 rounded-2xl border border-white/10 bg-slate-950/40 p-4 text-sm leading-6 text-slate-300">
        {score?.model_answer}
      </p>
      <p className="mt-3 text-sm font-bold text-yellow-100">Follow-up: {score?.follow_up_question}</p>
    </div>
  );
}

function ThirdPersonInterviewScene({ speaking, listening, candidateName = "Candidate", compact = false }) {
  const displayName = (candidateName || "Candidate").trim() || "Candidate";

  return (
    <div className={`third-person-scene ${compact ? "third-person-scene-compact" : ""}`}>
      <div className="scene-wall" />
      <div className="scene-floor">
        {Array.from({ length: 7 }, (_, index) => (
          <span key={`floor-line-${index}`} className="floor-line" style={{ top: `${18 + index * 10}%` }} />
        ))}
        {Array.from({ length: 7 }, (_, index) => (
          <span key={`floor-ray-${index}`} className="floor-ray" style={{ left: `${10 + index * 13}%` }} />
        ))}
      </div>

      <div className="room-hud room-hud-left">
        <span>3RD PERSON CAMERA</span>
        <strong>{listening ? "LISTENING" : speaking ? "INTERVIEWER SPEAKING" : "READY"}</strong>
      </div>
      <div className="room-hud room-hud-right">
        <span>SESSION</span>
        <strong>MOCK INTERVIEW</strong>
      </div>

      <div className="interviewer-platform">
        <motion.div
          animate={{ y: [-7, 7, -7] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          className="interviewer-face-frame"
        >
          <AiInterviewerAvatar active={speaking || listening} speaking={speaking} listening={listening} name="Interviewer" />
        </motion.div>
      </div>

      <div className="interview-table">
        <div className="table-screen">
          <span>Question feed</span>
          <strong>Adaptive follow-up ready</strong>
        </div>
        <div className="table-mic">
          <motion.span
            animate={{ scale: listening ? [1, 1.35, 1] : 1, opacity: listening ? [0.45, 1, 0.45] : 0.8 }}
            transition={{ duration: 1.1, repeat: listening ? Infinity : 0 }}
          />
        </div>
      </div>

      <div className="candidate-seat">
        <div className="candidate-head" />
        <div className="candidate-body" />
        <div className="candidate-label">{displayName}</div>
      </div>
    </div>
  );
}

function AiInterviewerAvatar({ active, speaking, listening, name }) {
  const displayName = (name || "Candidate").trim() || "Candidate";
  return (
    <div className="relative grid min-h-[290px] place-items-center">
      <motion.span
        animate={{ scale: listening ? [1, 1.08, 1] : active ? [1, 1.04, 1] : 1, opacity: listening ? [0.28, 0.65, 0.28] : [0.2, 0.4, 0.2] }}
        transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
        className="absolute inset-6 rounded-full border border-plasma/20 bg-plasma/5 blur-sm"
      />
      <motion.span
        animate={{ rotate: [0, 360], opacity: active ? [0.18, 0.4, 0.18] : 0.18 }}
        transition={{ duration: 16, repeat: Infinity, ease: "linear" }}
        className="absolute inset-10 rounded-full border border-dashed border-ion/30"
      />
      <motion.div
        animate={{
          y: [-8, 8, -8],
          boxShadow: listening
            ? "0 0 72px rgba(255,107,53,0.42)"
            : active
              ? "0 0 60px rgba(68,247,255,0.45)"
              : "0 0 30px rgba(68,247,255,0.22)",
        }}
        transition={{ y: { duration: 4, repeat: Infinity, ease: "easeInOut" }, boxShadow: { duration: 0.3 } }}
        className="relative h-64 w-56 overflow-hidden rounded-[2.5rem] border border-plasma/35 bg-[radial-gradient(circle_at_50%_10%,rgba(255,255,255,0.18),rgba(15,23,42,0.92)_38%,rgba(8,16,32,0.98)_100%)] shadow-neon"
      >
        <motion.div
          animate={{ opacity: listening ? [0.2, 0.75, 0.2] : [0.15, 0.35, 0.15] }}
          transition={{ duration: 1.2, repeat: Infinity }}
          className="absolute inset-0 bg-[linear-gradient(120deg,transparent,rgba(255,255,255,0.2),transparent)]"
        />
        <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-slate-950 via-slate-900/75 to-transparent" />
        <div className="absolute left-1/2 top-5 h-6 w-28 -translate-x-1/2 rounded-full border border-plasma/25 bg-plasma/10 blur-[1px]" />
        <div className="absolute left-1/2 top-8 h-[150px] w-[118px] -translate-x-1/2 rounded-[2.6rem] border border-plasma/25 bg-[linear-gradient(180deg,rgba(11,23,48,0.96),rgba(7,15,32,0.98))] shadow-[0_0_28px_rgba(68,247,255,0.16)]" />
        <div className="absolute left-1/2 top-[34px] h-[138px] w-[106px] -translate-x-1/2 rounded-[2.2rem] border border-white/8 bg-[radial-gradient(circle_at_50%_18%,rgba(68,247,255,0.18),rgba(6,12,26,0.98)_60%)]" />
        <motion.div
          animate={{ opacity: active ? [0.18, 0.3, 0.18] : 0.16 }}
          transition={{ duration: 2.8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-1/2 top-[56px] h-12 w-12 -translate-x-1/2 rounded-full border border-plasma/20 bg-plasma/10 shadow-[0_0_18px_rgba(68,247,255,0.2)]"
        />
        <div className="absolute left-1/2 top-[74px] h-[2px] w-14 -translate-x-1/2 bg-gradient-to-r from-transparent via-plasma/60 to-transparent" />
        <motion.span
          animate={{ scaleX: speaking ? [1, 1.16, 1] : 1, opacity: listening ? [0.7, 1, 0.7] : [0.85, 1, 0.85] }}
          transition={{ duration: 0.45, repeat: speaking || listening ? Infinity : 0 }}
          className="absolute left-[calc(50%-31px)] top-[88px] h-[10px] w-7 rounded-full border border-plasma/25 bg-plasma/80 shadow-[0_0_12px_rgba(68,247,255,0.5)]"
        />
        <motion.span
          animate={{ scaleX: speaking ? [1, 1.16, 1] : 1, opacity: listening ? [0.7, 1, 0.7] : [0.85, 1, 0.85] }}
          transition={{ duration: 0.45, repeat: speaking || listening ? Infinity : 0, delay: 0.05 }}
          className="absolute right-[calc(50%-31px)] top-[88px] h-[10px] w-7 rounded-full border border-plasma/25 bg-plasma/80 shadow-[0_0_12px_rgba(68,247,255,0.5)]"
        />
        <div className="absolute left-1/2 top-[108px] h-6 w-[2px] -translate-x-1/2 rounded-full bg-gradient-to-b from-plasma/80 to-transparent" />
        <motion.div
          animate={{
            width: speaking ? [34, 48, 34] : listening ? [34, 40, 34] : 34,
            opacity: active ? [0.72, 1, 0.72] : 0.68,
          }}
          transition={{ duration: 0.32, repeat: speaking || listening ? Infinity : 0 }}
          className="absolute left-1/2 top-[126px] h-[8px] -translate-x-1/2 rounded-full bg-gradient-to-r from-cyan-300 via-plasma to-cyan-300 shadow-[0_0_18px_rgba(68,247,255,0.62)]"
        />
        <div className="absolute left-1/2 top-[146px] h-4 w-10 -translate-x-1/2 rounded-full border border-plasma/15 bg-plasma/10" />
        <div className="absolute left-1/2 bottom-0 h-24 w-40 -translate-x-1/2 rounded-t-[3rem] border border-white/8 bg-[linear-gradient(180deg,rgba(26,38,60,0.96),rgba(10,17,30,0.98))]" />
        <div className="absolute left-1/2 bottom-[74px] h-12 w-10 -translate-x-1/2 rounded-b-[1.5rem] rounded-t-[1rem] border border-plasma/15 bg-[linear-gradient(180deg,rgba(15,25,42,0.95),rgba(9,15,28,0.98))]" />
        <div className="absolute left-[calc(50%-62px)] bottom-7 h-[2px] w-20 rotate-[18deg] rounded-full bg-gradient-to-r from-transparent via-plasma/40 to-transparent" />
        <div className="absolute right-[calc(50%-62px)] bottom-7 h-[2px] w-20 -rotate-[18deg] rounded-full bg-gradient-to-r from-transparent via-plasma/40 to-transparent" />
        <div className="absolute left-1/2 top-4 -translate-x-1/2 font-display text-[10px] font-black uppercase tracking-[0.28em] text-plasma">
          INTERVIEW AI
        </div>
        <div className="absolute bottom-5 left-1/2 w-36 -translate-x-1/2 truncate text-center text-xs font-bold uppercase tracking-[0.16em] text-slate-200">
          {displayName}
        </div>
      </motion.div>
      <div className="absolute bottom-0 rounded-full border border-plasma/20 bg-plasma/10 px-4 py-2 font-display text-xs font-black uppercase tracking-[0.22em] text-plasma">
        {listening ? "Listening" : active ? "Interviewing" : "Ready"}
      </div>
    </div>
  );
}

function SectionTitle({ kicker, title }) {
  return (
    <div>
      <div className="font-display text-xs uppercase tracking-[0.34em] text-plasma">{kicker}</div>
      <h2 className="mt-3 max-w-4xl font-display text-3xl font-black uppercase tracking-[-0.04em] text-white sm:text-5xl">{title}</h2>
    </div>
  );
}

function GlassCard({ children, className = "" }) {
  const rotateX = useMotionValue(0);
  const rotateY = useMotionValue(0);
  const springX = useSpring(rotateX, { stiffness: 150, damping: 18 });
  const springY = useSpring(rotateY, { stiffness: 150, damping: 18 });

  return (
    <motion.div
      style={{ rotateX: springX, rotateY: springY }}
      onPointerMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        rotateX.set(((event.clientY - rect.top) / rect.height - 0.5) * -5);
        rotateY.set(((event.clientX - rect.left) / rect.width - 0.5) * 5);
      }}
      onPointerLeave={() => {
        rotateX.set(0);
        rotateY.set(0);
      }}
      className={`relative overflow-hidden rounded-[2rem] border border-white/10 bg-white/[0.06] p-6 shadow-2xl shadow-black/30 backdrop-blur-2xl ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.08] via-transparent to-plasma/[0.04]" />
      <div className="relative">{children}</div>
    </motion.div>
  );
}

function ScoreCircle({ ready }) {
  const score = ready ? 92 : 67;
  const circumference = 2 * Math.PI * 68;
  return (
    <div className="grid place-items-center">
      <svg viewBox="0 0 180 180" className="h-56 w-56 -rotate-90">
        <circle cx="90" cy="90" r="68" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="14" />
        <motion.circle
          cx="90"
          cy="90"
          r="68"
          fill="none"
          stroke="url(#scoreGradient)"
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          whileInView={{ strokeDashoffset: circumference - (score / 100) * circumference }}
          viewport={{ once: true }}
          transition={{ duration: 1.4, ease: "easeOut" }}
        />
        <defs>
          <linearGradient id="scoreGradient">
            <stop stopColor="#44f7ff" />
            <stop offset="1" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute text-center">
        <div className="font-display text-5xl font-black text-white">{score}</div>
        <div className="mt-1 text-xs uppercase tracking-[0.26em] text-plasma">Match Score</div>
      </div>
    </div>
  );
}

function ProgressBar({ label, value, color, delay }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm font-bold text-slate-200">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-white/10">
        <motion.div
          initial={{ width: 0 }}
          whileInView={{ width: `${value}%` }}
          viewport={{ once: true }}
          transition={{ duration: 1.1, delay, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r ${color} shadow-neon`}
        />
      </div>
    </div>
  );
}

function InsightTile({ title, copy, blinking = false }) {
  return (
    <motion.div initial={{ opacity: 0, x: 24 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="rounded-3xl border border-white/10 bg-white/[0.055] p-5">
      <h3 className={`font-display text-lg font-black text-white ${blinking ? "animate-blink" : ""}`}>{title}</h3>
      <p className="mt-2 leading-7 text-slate-400">{copy}</p>
    </motion.div>
  );
}

function ChatBubble({ role, text, user = false }) {
  return (
    <div className={`rounded-3xl border p-5 ${user ? "ml-auto max-w-[84%] border-ion/25 bg-ion/10" : "max-w-[88%] border-plasma/20 bg-plasma/10"}`}>
      <div className="mb-2 text-xs font-bold uppercase tracking-[0.22em] text-plasma">{role}</div>
      <p className="leading-7 text-slate-200">{text}</p>
    </div>
  );
}

function JobList({ title, jobs, linkKey }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/40 p-4">
      <h4 className="font-display text-sm font-black text-plasma">{title}</h4>
      <div className="mt-3 grid gap-3">
        {jobs.length ? (
          jobs.slice(0, 8).map((job, index) => (
            <a
              key={`${title}-${job.title || "job"}-${index}`}
              href={job[linkKey] || "#"}
              target="_blank"
              rel="noreferrer"
              className="rounded-xl border border-white/10 bg-white/[0.055] p-3 text-left transition hover:border-plasma/40"
            >
              <div className="font-bold text-white">{job.title || "Untitled role"}</div>
              <div className="text-sm text-slate-400">{job.companyName || "Unknown company"}</div>
              <div className="text-sm text-slate-400">{job.location || "Location not provided"}</div>
            </a>
          ))
        ) : (
          <p className="text-sm text-slate-400">No jobs loaded yet.</p>
        )}
      </div>
    </div>
  );
}
