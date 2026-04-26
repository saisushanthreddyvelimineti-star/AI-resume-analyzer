import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { Component, useEffect, useState } from "react";
import {
  FloatingNavbar,
  HeroSection,
  ResumeUpload,
  AnalysisDashboard,
  InterviewCoach,
  CursorAura,
} from "./components";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const sections = [
  { id: "home", label: "Home" },
  { id: "upload", label: "Upload" },
  { id: "dashboard", label: "Dashboard" },
  { id: "coach", label: "Interview AI" },
];

function App() {
  const [theme, setTheme] = useState("dark");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);
  const [isBuildingResume, setIsBuildingResume] = useState(false);
  const [isCoachBusy, setIsCoachBusy] = useState(false);
  const [analysisStatus, setAnalysisStatus] = useState("Waiting for resume upload.");
  const [analysisReady, setAnalysisReady] = useState(false);
  const [appError, setAppError] = useState("");
  const [status, setStatus] = useState(null);
  const [autoTarget, setAutoTarget] = useState({
    target_role: "",
    job_description: "",
    location: "United Kingdom",
  });
  const [atsInput, setAtsInput] = useState({
    targetRole: "",
    jobDescription: "",
  });
  const [builderContext, setBuilderContext] = useState({
    targetRole: "",
    jobDescription: "",
    source: "benchmark",
  });
  const [analysis, setAnalysis] = useState({
    summary: "Upload a PDF resume to generate a real profile summary automatically.",
    gaps: "Skill gaps will appear here after the backend processes your resume.",
    roadmap: "Your personalized roadmap will appear here after automatic analysis.",
    resume_text: "",
    mode: "idle",
  });
  const [agenticReport, setAgenticReport] = useState(null);
  const [jobs, setJobs] = useState({ keywords: "", linkedin_jobs: [], indeed_jobs: [], mode: "idle" });
  const [resumeBuilderReport, setResumeBuilderReport] = useState(null);
  const [coachMessages, setCoachMessages] = useState([
    {
      role: "assistant",
      content:
        "Upload and analyze your resume first, then ask for mock interviews, answer rewrites, or role-specific coaching.",
    },
  ]);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 80, damping: 18 });
  const springY = useSpring(mouseY, { stiffness: 80, damping: 18 });
  const orbX = useTransform(springX, [0, 1400], [-22, 22]);
  const orbY = useTransform(springY, [0, 900], [-22, 22]);

  useEffect(() => {
    const handleMove = (event) => {
      mouseX.set(event.clientX);
      mouseY.set(event.clientY);
    };
    window.addEventListener("pointermove", handleMove);
    return () => window.removeEventListener("pointermove", handleMove);
  }, [mouseX, mouseY]);

  useEffect(() => {
    document.documentElement.classList.toggle("light-mode", theme === "light");
  }, [theme]);

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((response) => response.json())
      .then((data) => setStatus(data))
      .catch(() => setStatus(null));
  }, []);

  useEffect(() => {
    setAtsInput((current) => {
      if (current.targetRole.trim() || current.jobDescription.trim()) {
        return current;
      }
      return {
        targetRole: autoTarget?.target_role || "",
        jobDescription: autoTarget?.job_description || "",
      };
    });
  }, [autoTarget]);

  const selectResumeFile = async (file) => {
    if (!file) return;

    const intakeTargetRole = atsInput.targetRole.trim();
    const intakeJobDescription = atsInput.jobDescription.trim();
    const benchmarkTargetRole = autoTarget.target_role.trim();
    const benchmarkJobDescription = autoTarget.job_description.trim();
    const hasManualAtsInput = Boolean(intakeJobDescription) && (
      builderContext.source === "manual" ||
      intakeJobDescription !== benchmarkJobDescription ||
      intakeTargetRole !== benchmarkTargetRole
    );

    const allowedExtensions = [".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp", ".bmp"];
    if (!allowedExtensions.some((extension) => file.name.toLowerCase().endsWith(extension))) {
      setUploadedFile(null);
      setAnalysisReady(false);
      setAnalysisStatus("Rejected file. Upload a PDF, DOCX, or image resume.");
      setAppError("Please select a PDF, DOCX, or image resume file.");
      return;
    }

    setUploadedFile(file);
    setAppError("");
    setAnalysisReady(false);
    setResumeBuilderReport(null);
    setAgenticReport(null);
    setJobs({ keywords: "", linkedin_jobs: [], indeed_jobs: [], mode: "idle" });
    setAutoTarget({ target_role: "", job_description: "", location: "United Kingdom" });
    if (!hasManualAtsInput) {
      setAtsInput({ targetRole: "", jobDescription: "" });
    }
    setBuilderContext({ targetRole: "", jobDescription: "", source: "benchmark" });
    setIsAnalyzing(true);
    setIsBuildingResume(true);
    setIsLoadingJobs(true);
    setAnalysisStatus(
      hasManualAtsInput
        ? `${file.name} selected. Running resume analysis, builder match, and job matching...`
        : `${file.name} selected. Running resume analysis, resume builder, and job matching...`,
    );
    setJobs({ keywords: "", linkedin_jobs: [], indeed_jobs: [], mode: "idle" });

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("location", "United Kingdom");
    if (hasManualAtsInput) {
      formData.append("target_role", intakeTargetRole);
      formData.append("job_description", intakeJobDescription);
    }

    try {
      const response = await fetch(`${API_BASE}/api/intake/auto`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Automatic resume intake failed.");
      }

      setAnalysis(data.analysis);
      setResumeBuilderReport(data.resume_builder_report);
      setAgenticReport(data.agentic_report || null);
      setJobs(data.jobs);
      setAutoTarget(data.auto_target || { target_role: "", job_description: "", location: "United Kingdom" });
      setBuilderContext({
        targetRole: data.ats_context?.target_role || data.auto_target?.target_role || "",
        jobDescription: data.ats_context?.job_description || data.auto_target?.job_description || "",
        source: data.ats_context?.source || "benchmark",
      });
      setAnalysisReady(true);
      setAnalysisStatus(
        data.ats_context?.source === "manual"
          ? `Automatic intake complete for ${data.analysis?.filename || file.name}. The resume builder is aligned to your uploaded job description.`
          : `Automatic intake complete for ${data.analysis?.filename || file.name}. The resume builder is ready with a benchmark role and job matches.`,
      );
      setCoachMessages([
        {
          role: "assistant",
          content:
            "Resume analysis, resume builder guidance, and job recommendations are ready. I can now coach you using your actual resume summary, gaps, roadmap, and target role.",
        },
      ]);
      document.querySelector("#dashboard")?.scrollIntoView({ behavior: "smooth" });
    } catch (error) {
      setAnalysisStatus("Automatic intake failed. Read the error message below.");
      setAppError(error.message || "Automatic resume intake failed. Check that the backend is running and reachable.");
      setAnalysisReady(false);
      setAgenticReport(null);
    } finally {
      setIsAnalyzing(false);
      setIsLoadingJobs(false);
      setIsBuildingResume(false);
    }
  };

  const speakAssistantReply = (reply, audioBase64) => {
    const duixSpeak = typeof window !== "undefined" ? window.__careerDuixSpeak : null;
    if (reply && typeof duixSpeak === "function") {
      window.speechSynthesis?.cancel?.();
      duixSpeak(reply);
      return;
    }

    if (audioBase64) {
      window.speechSynthesis?.cancel?.();
      const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
      audio.play().catch(() => {});
      return;
    }

    if (!("speechSynthesis" in window) || !reply) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(reply.replace(/\s+/g, " ").slice(0, 900));
    utterance.rate = 0.94;
    utterance.pitch = 1.03;
    window.speechSynthesis.speak(utterance);
  };

  const sendCoachPrompt = async (prompt) => {
    const cleanedPrompt = prompt.trim();
    if (!cleanedPrompt) return;

    setIsCoachBusy(true);
    setAppError("");
    setCoachMessages((current) => [...current, { role: "user", content: cleanedPrompt }]);

    try {
      const response = await fetch(`${API_BASE}/api/jarvis/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          summary: analysis.summary,
          prompt: cleanedPrompt,
          conversation: coachMessages,
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Interview coach failed.");
      }

      setCoachMessages((current) => [...current, { role: "assistant", content: data.reply }]);
      speakAssistantReply(data.reply, data.audio_base64);
    } catch (error) {
      const message = error.message || "Interview coach failed.";
      setAppError(message);
      setCoachMessages((current) => [...current, { role: "assistant", content: message }]);
    } finally {
      setIsCoachBusy(false);
    }
  };

  const sendVoicePrompt = async (audioFile) => {
    if (!audioFile) return;

    setIsCoachBusy(true);
    setAppError("");
    setCoachMessages((current) => [
      ...current,
      { role: "user", content: `Voice prompt uploaded: ${audioFile.name}` },
    ]);

    const formData = new FormData();
    formData.append("audio", audioFile);
    formData.append("summary", analysis.summary);
    formData.append("conversation", JSON.stringify(coachMessages));

    try {
      const response = await fetch(`${API_BASE}/api/jarvis/voice`, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Voice coaching failed.");
      }

      setCoachMessages((current) => [
        ...current,
        { role: "user", content: data.transcript || `Voice prompt uploaded: ${audioFile.name}` },
        { role: "assistant", content: data.reply },
      ]);

      if (data.audio_base64) {
        speakAssistantReply(data.reply, data.audio_base64);
      } else {
        speakAssistantReply(data.reply);
      }
    } catch (error) {
      const message = error.message || "Voice coaching failed.";
      setAppError(message);
      setCoachMessages((current) => [...current, { role: "assistant", content: message }]);
    } finally {
      setIsCoachBusy(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-void text-slate-100 transition-colors duration-700">
      <CursorAura x={springX} y={springY} />
      <div className="fixed inset-0 -z-30 bg-[radial-gradient(circle_at_18%_12%,rgba(68,247,255,0.2),transparent_24%),radial-gradient(circle_at_80%_20%,rgba(139,92,246,0.18),transparent_26%),linear-gradient(180deg,#02040d_0%,#07111f_44%,#050712_100%)]" />
      <div className="fixed inset-0 -z-20 bg-radial-grid bg-[length:100%_100%,42px_42px,42px_42px] opacity-70" />
      <motion.div
        style={{ x: orbX, y: orbY }}
        className="pointer-events-none fixed right-[-120px] top-20 -z-10 h-[520px] w-[520px] rounded-full bg-plasma/10 blur-3xl"
      />
      <motion.div
        style={{ x: orbY, y: orbX }}
        className="pointer-events-none fixed bottom-[-160px] left-[-140px] -z-10 h-[520px] w-[520px] rounded-full bg-ion/15 blur-3xl"
      />

      <FloatingNavbar
        sections={sections}
        theme={theme}
        onThemeToggle={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
      />

      <FrontendErrorBoundary>
        <AnimatePresence mode="wait">
        <motion.main
          key={theme}
          initial={false}
          animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -16, scale: 0.985 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="relative mx-auto w-full max-w-7xl px-4 pb-20 pt-24 sm:px-6 lg:px-8"
          >
            <HeroSection />
            <ResumeUpload
              uploadedFile={uploadedFile}
              setUploadedFile={selectResumeFile}
              atsInput={atsInput}
              onAtsInputChange={setAtsInput}
              isAnalyzing={isAnalyzing}
              error={appError}
              status={status}
              analysisStatus={analysisStatus}
              analysisReady={analysisReady}
            />
            <AnalysisDashboard
              uploadedFile={uploadedFile}
              isAnalyzing={isAnalyzing}
              analysisReady={analysisReady}
              analysis={analysis}
              error={appError}
              jobs={jobs}
              isLoadingJobs={isLoadingJobs}
              resumeBuilderReport={resumeBuilderReport}
              autoTarget={autoTarget}
              atsInput={atsInput}
              builderContext={builderContext}
              onAtsInputChange={setAtsInput}
              isBuildingResume={isBuildingResume}
            />
            <InterviewCoach
              analysis={analysis}
              analysisReady={analysisReady}
              apiBase={API_BASE}
              autoTarget={autoTarget}
              atsContext={builderContext}
              messages={coachMessages}
              isCoachBusy={isCoachBusy}
              onAppError={setAppError}
              onSendPrompt={sendCoachPrompt}
              onSendVoice={sendVoicePrompt}
              voiceReady={Boolean(status?.jarvis_voice_ready)}
            />
          </motion.main>
        </AnimatePresence>
      </FrontendErrorBoundary>
    </div>
  );
}

class FrontendErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (this.state.error) {
      return (
        <main className="mx-auto grid min-h-screen max-w-3xl place-items-center px-6 text-center">
          <div className="rounded-[2rem] border border-ember/40 bg-ember/10 p-8 text-white shadow-ember">
            <p className="font-display text-xs uppercase tracking-[0.3em] text-ember">Frontend error</p>
            <h1 className="mt-4 font-display text-3xl font-black">The interface failed to mount.</h1>
            <p className="mt-4 text-slate-200">{this.state.error.message}</p>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}

export default App;
