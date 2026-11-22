import React from 'react'
import { motion } from 'framer-motion'
import {
  Sparkles,
  Building2,
  Briefcase,
  Calendar,
  ExternalLink,
  Code,
  ShieldCheck,
  UserCheck,
} from 'lucide-react'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'

export const EmailIntelligenceSection: React.FC = () => {
  return (
    <section id="preview" className="py-20 md:py-28 bg-background-secondary/60 border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-surface border border-border text-xs font-semibold text-coral">
            <Sparkles className="w-3.5 h-3.5" />
            Live Extraction Demonstration
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
            Raw email chaos in. Structured clarity out.
          </h2>
          <p className="text-base sm:text-lg text-foreground-secondary leading-relaxed">
            See how KNIT extracts the crucial facts, deadlines, and requirements buried across lengthy academic and corporate emails.
          </p>
        </div>

        {/* Side-by-side Comparison Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          {/* Left Column: Raw Unformatted Email */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-6 bg-white border border-border rounded-2xl p-6 sm:p-7 shadow-soft flex flex-col justify-between"
          >
            <div>
              {/* Header Label */}
              <div className="flex items-center justify-between pb-4 mb-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-foreground-secondary/40" />
                  <span className="text-xs font-bold uppercase tracking-wider text-foreground-secondary">
                    Raw Incoming Email (Untrusted Data)
                  </span>
                </div>
                <Badge variant="neutral" size="sm">
                  1,420 words
                </Badge>
              </div>

              {/* Email Envelope Details */}
              <div className="space-y-1.5 text-xs text-foreground-secondary mb-4 pb-4 border-b border-border font-mono">
                <div><span className="font-semibold text-foreground">From:</span> Google University Programs &lt;recruiting-swe@google.com&gt;</div>
                <div><span className="font-semibold text-foreground">To:</span> Student Candidate &lt;student@university.edu&gt;</div>
                <div><span className="font-semibold text-foreground">Subject:</span> Update Regarding 2027 Software Engineering Internship Applications</div>
              </div>

              {/* Dense Email Body */}
              <div className="text-xs text-foreground-secondary leading-relaxed space-y-3 font-serif sm:text-sm">
                <p>
                  Dear Candidate, Thank you for expressing an interest in engineering career pathways at Google. We are pleased to announce that recruitment for our <strong>Summer 2027 Software Engineer Intern</strong> cohort is now actively underway across our engineering campuses.
                </p>
                <p>
                  To be considered for technical review, candidates must be currently enrolled in an accredited Bachelor&apos;s or Master&apos;s degree program in Computer Science, Electrical Engineering, or related fields with an expected graduation date between December 2026 and June 2028. Proficiency in core foundational competencies including Data Structures, Algorithms, and at least one general-purpose programming language such as Python, Java, C++, or Go is required.
                </p>
                <p className="bg-amber-50/70 p-2 rounded-lg border border-amber-200/50 text-amber-900">
                  Please be advised that the final application window will officially close on <strong>December 15, 2026 at 11:59 PM PST</strong>. Late submissions, incomplete transcripts, or supplementary portfolios sent via email cannot be processed after this cutoff date...
                </p>
              </div>
            </div>

            <div className="pt-4 mt-6 border-t border-border flex items-center justify-between text-xs text-foreground-secondary">
              <span>Time spent reading manually: ~4 minutes</span>
              <span className="text-red-500 font-medium">Risk of missing deadline: High</span>
            </div>
          </motion.div>

          {/* Right Column: KNIT Extracted Intelligence */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="lg:col-span-6 bg-white border-2 border-coral/30 rounded-2xl p-6 sm:p-7 shadow-coral-sm flex flex-col justify-between"
          >
            <div className="space-y-5">
              {/* Header Label */}
              <div className="flex items-center justify-between pb-4 border-b border-border">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-coral animate-pulse" />
                  <span className="text-xs font-bold uppercase tracking-wider text-coral">
                    KNIT Email Intelligence (Validated)
                  </span>
                </div>
                <Badge variant="coral" size="sm">
                  Processed in 180ms
                </Badge>
              </div>

              {/* AI Summary Highlight */}
              <div className="rounded-xl bg-pink-surface border border-border p-4">
                <div className="flex items-center gap-2 text-xs font-bold text-coral mb-1">
                  <Sparkles className="w-4 h-4" />
                  <span>Executive Summary</span>
                </div>
                <p className="text-xs sm:text-sm text-foreground font-medium leading-relaxed">
                  Google SWE Internship (Summer 2027) application is open. Requires transcript and resume submission before the strict deadline of <strong>December 15, 2026</strong>.
                </p>
              </div>

              {/* Extracted Entity Cards */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-background-secondary border border-border flex items-start gap-2.5">
                  <Building2 className="w-4 h-4 text-coral mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-[11px] text-foreground-secondary block">Company</span>
                    <span className="font-bold text-foreground text-sm">Google</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-background-secondary border border-border flex items-start gap-2.5">
                  <Briefcase className="w-4 h-4 text-coral mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-[11px] text-foreground-secondary block">Target Role</span>
                    <span className="font-bold text-foreground text-sm">Software Engineer Intern</span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-coral/5 border border-coral/20 flex items-start gap-2.5 col-span-2">
                  <Calendar className="w-4 h-4 text-coral mt-0.5 flex-shrink-0" />
                  <div className="flex-1 flex items-center justify-between">
                    <div>
                      <span className="text-[11px] text-foreground-secondary block">Application Deadline</span>
                      <span className="font-bold text-coral text-sm">December 15, 2026 &bull; 11:59 PM PST</span>
                    </div>
                    <Badge variant="coral" size="sm">
                      Urgent Action
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Skills & Eligibility Tags */}
              <div className="space-y-2 pt-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-foreground">
                  <Code className="w-3.5 h-3.5 text-coral" />
                  <span>Required Skills Extracted:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="neutral" size="sm">Data Structures</Badge>
                  <Badge variant="neutral" size="sm">Algorithms</Badge>
                  <Badge variant="neutral" size="sm">Python / Java / C++</Badge>
                  <Badge variant="neutral" size="sm">Problem Solving</Badge>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-foreground">
                  <UserCheck className="w-3.5 h-3.5 text-coral" />
                  <span>Eligibility & Required Docs:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="pink" size="sm">BS/MS in Computer Science</Badge>
                  <Badge variant="pink" size="sm">Graduating 2026 - 2028</Badge>
                  <Badge variant="pink" size="sm">Unofficial Transcript</Badge>
                  <Badge variant="pink" size="sm">PDF Resume</Badge>
                </div>
              </div>
            </div>

            {/* Direct Action Toolbar */}
            <div className="pt-5 mt-6 border-t border-border flex items-center justify-between gap-3">
              <span className="text-xs font-medium text-emerald-700 flex items-center gap-1">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Zero Hallucinations Verified
              </span>
              <Button variant="primary" size="sm">
                Add to KNIT Tasks
                <ExternalLink className="w-3.5 h-3.5 ml-1" />
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
