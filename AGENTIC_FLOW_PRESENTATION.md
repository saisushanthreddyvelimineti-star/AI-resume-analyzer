# Agentic AI Flow

## 1. Problem

Traditional resume tools are static:
- upload resume
- get score
- manually decide next step

This project improves that by using an agentic workflow that can:
- understand the candidate context
- decide which tools to run
- combine multiple AI and utility steps
- verify the result
- return actionable next steps

---

## 2. What Makes It Agentic

The agentic part of this system is not just "AI output".

It performs:
- planning
- tool selection
- multi-step execution
- conditional branching
- verification
- final recommendation synthesis

Core file:
- `src/agentic_ai.py`

---

## 3. High-Level Flow

```text
User Uploads Resume / Adds Job Description
                |
                v
         Resume Intake Layer
                |
                v
        Planner Agent Creates Plan
                |
                v
      Tool Router Selects Needed Tools
                |
                v
  -----------------------------------------
  | Profile Analysis                      |
  | Target Role Inference                 |
  | ATS / Resume Builder Comparison       |
  | Job Search                            |
  | Course Recommendations                |
  | Interview Plan                        |
  | Interview Coaching                    |
  -----------------------------------------
                |
                v
          Verification Layer
                |
                v
      Final Recommendation + Next Steps
                |
                v
     UI Panels Update for the User
```

---

## 4. Detailed Agentic Flow

### Step 1: Input Collection

The user provides:
- resume
- optional job description
- optional target role
- location

If a real job description is missing, the system can still continue using a benchmark role description.

### Step 2: Planner Agent

The planner decides:
- what tools are needed
- what sequence should be followed
- whether ATS scoring should use a real JD or a benchmark

This is dynamic, not a fixed hardcoded path.

### Step 3: Tool Execution

The system runs relevant tools such as:
- `profile_analysis`
- `target_role_inference`
- `ats_score`
- `job_search`
- `course_recommendations`
- `interview_plan`
- `interview_coaching`

### Step 4: Verification

The verifier checks:
- missing inputs
- confidence level
- whether results are benchmark-based or user-specific
- whether the recommendations are safe to trust fully

### Step 5: Final Recommendation

The final response includes:
- primary target role
- priority actions
- job search keywords
- skill gaps
- learning resources
- interview next steps

---

## 5. Current Architecture Mapping

### Agentic Core

- `src/agentic_ai.py`

Responsibilities:
- build plan
- select tools
- run workflow
- verify outputs
- summarize next actions

### AI but Not Fully Agentic

- `src/resume_builder_ai.py`
- `src/interview_ai.py`
- `src/course_recommender.py`

These provide intelligent outputs, but each one is still a fixed-purpose module.

### Standard Application Layer

- `backend_app.py`
- `frontend/src/App.jsx`
- `frontend/src/components.jsx`

These handle:
- routing
- API calls
- rendering
- user interaction

---

## 6. Presentation Version

Use this short explanation:

> Our system is agentic because it does not just generate one AI response.  
> It plans the workflow, selects tools dynamically, executes multiple steps, verifies the result, and returns the next best action for the candidate.

---

## 7. Simple Slide Flow

### Slide 1
**Title:** Agentic AI Career Assistant

### Slide 2
**Problem:** Traditional resume tools are static and disconnected

### Slide 3
**Solution:** An agentic workflow that decides what to do next

### Slide 4
**Flow:**
- Input
- Planning
- Tool Selection
- Execution
- Verification
- Recommendation

### Slide 5
**Tools Used:**
- Resume analysis
- Role inference
- Resume builder / ATS comparison
- Job recommendation
- Learning plan
- Interview preparation

### Slide 6
**Why It Matters:**
- personalized
- multi-step
- adaptive
- explainable
- actionable

---

## 8. One-Line Demo Script

> The user uploads a resume, the agent plans the workflow, chooses the right tools, checks skill gaps, recommends jobs and learning resources, verifies confidence, and returns the next best action.

---

## 9. Future Agentic Enhancements

To make the project even more agentic later:
- make intake fully planner-driven
- add memory between sessions
- let the agent re-plan after each user action
- support long-running goal tracking
- allow the agent to prioritize among multiple career strategies

---

## 10. Final Summary

Best presentation label:

**AI-powered career platform with an agentic orchestration layer**

If you want a stronger claim later:

**Agentic career assistant with planning, tool routing, verification, and adaptive recommendations**
