import React from 'react'
import { motion } from 'framer-motion'
import {
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Calendar,
  Briefcase,
  Building2,
  FileText,
  Clock,
  Send,
  PlusCircle,
  Inbox,
  GraduationCap,
} from 'lucide-react'
import { Button } from '../ui/Button'
import { Badge } from '../ui/Badge'

interface HeroSectionProps {
  onGetStartedClick?: () => void
  onSeeHowItWorksClick?: () => void
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onGetStartedClick,
  onSeeHowItWorksClick,
}) => {
  return (
    <section className="relative overflow-hidden pt-12 pb-20 md:pt-18 md:pb-28 bg-gradient-to-b from-white via-background-secondary/40 to-white">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Headline, Copy & CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-6 space-y-6 text-left"
          >
            {/* Tagline Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-pink-surface border border-border text-xs font-semibold text-coral">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI-Powered Email Intelligence & Automation</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-foreground leading-[1.12]">
              Your inbox, <span className="text-coral">understood.</span>
            </h1>

            {/* Supporting Subtext */}
            <p className="text-lg sm:text-xl text-foreground-secondary leading-relaxed max-w-xl">
              Turn emails into clear summaries, opportunities and next steps. Built for students, internship applicants, and busy professionals who cannot afford to miss what matters.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-2">
              <Button
                variant="primary"
                size="lg"
                onClick={onGetStartedClick || (() => {
                  document.querySelector('#features')?.scrollIntoView({ behavior: 'smooth' })
                })}
              >
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-1" />
              </Button>

              <Button
                variant="secondary"
                size="lg"
                onClick={onSeeHowItWorksClick || (() => {
                  document.querySelector('#how-it-works')?.scrollIntoView({ behavior: 'smooth' })
                })}
              >
                See How It Works
              </Button>
            </div>

            {/* Trust Highlights */}
            <div className="pt-6 border-t border-border grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs font-medium text-foreground-secondary">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-coral flex-shrink-0" />
                <span>Zero Auto-Send Guarantee</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-coral flex-shrink-0" />
                <span>Official Gmail OAuth</span>
              </div>
              <div className="flex items-center gap-2 col-span-2 sm:col-span-1">
                <CheckCircle2 className="w-4 h-4 text-coral flex-shrink-0" />
                <span>User-Controlled Actions</span>
              </div>
            </div>
          </motion.div>

          {/* Right Column: Realistic KNIT Dashboard / Inbox Preview */}
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="lg:col-span-6 relative"
          >
            {/* Subtle decorative background glow */}
            <div className="absolute -inset-2 bg-gradient-to-r from-pink-surface to-coral-light rounded-3xl blur-xl opacity-70 -z-10" />

            <div className="bg-white border border-border rounded-2xl shadow-xl overflow-hidden">
              {/* Mock Window Top Bar */}
              <div className="bg-background-secondary border-b border-border px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-400/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-400/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400/80" />
                  <span className="ml-2 text-xs font-mono font-medium text-foreground-secondary">
                    knit.app/inbox
                  </span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Badge variant="coral" size="sm">
                    Live Demo
                  </Badge>
                </div>
              </div>

              {/* Mock Dashboard Body */}
              <div className="p-4 sm:p-5 space-y-4">
                {/* Category Pills Bar */}
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
                  <span className="px-3 py-1 rounded-full font-semibold bg-foreground text-white flex items-center gap-1">
                    <Inbox className="w-3.5 h-3.5" />
                    All (12)
                  </span>
                  <span className="px-3 py-1 rounded-full font-semibold bg-coral text-white flex items-center gap-1 shadow-coral-sm">
                    <Briefcase className="w-3.5 h-3.5" />
                    Internship (3)
                  </span>
                  <span className="px-3 py-1 rounded-full font-medium bg-background-secondary text-foreground-secondary hover:text-foreground border border-border flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    Interview (1)
                  </span>
                  <span className="px-3 py-1 rounded-full font-medium bg-background-secondary text-foreground-secondary hover:text-foreground border border-border flex items-center gap-1">
                    <GraduationCap className="w-3.5 h-3.5" />
                    College (4)
                  </span>
                </div>

                {/* Selected Active Email Preview Card */}
                <div className="border border-border rounded-xl p-4 bg-background-secondary/30 space-y-3 text-left">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-xl bg-coral flex items-center justify-center text-white font-bold text-sm shadow-coral-sm">
                        G
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-bold text-foreground">Google University Recruiting</h4>
                          <span className="text-[11px] text-foreground-secondary">2h ago</span>
                        </div>
                        <p className="text-xs text-foreground-secondary">
                          recruiting-swe-intern@google.com
                        </p>
                      </div>
                    </div>
                    <Badge variant="pink" size="sm">
                      Internship Opportunity
                    </Badge>
                  </div>

                  {/* Subject Line */}
                  <h3 className="text-sm font-bold text-foreground">
                    Action Required: Software Engineering Intern 2027 — Application Deadline
                  </h3>

                  {/* Soft Pink AI Summary Panel */}
                  <div className="rounded-xl bg-pink-surface border border-border/80 p-3.5 space-y-2">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-coral">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>KNIT AI Summary</span>
                    </div>
                    <p className="text-xs text-foreground leading-relaxed">
                      Google invites eligible candidates to submit applications for the <strong>Summer 2027 Software Engineer Internship</strong>. The firm deadline is <strong>December 15, 2026</strong>. Requires unofficial transcript and updated resume.
                    </p>
                  </div>

                  {/* Extracted Details Grid */}
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                    <div className="p-2.5 rounded-lg bg-white border border-border flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-coral" />
                      <div>
                        <span className="text-[10px] text-foreground-secondary block">Company</span>
                        <span className="font-semibold text-foreground">Google</span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-white border border-border flex items-center gap-2">
                      <Briefcase className="w-4 h-4 text-coral" />
                      <div>
                        <span className="text-[10px] text-foreground-secondary block">Position</span>
                        <span className="font-semibold text-foreground">Software Engineer Intern</span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-white border border-border flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-coral" />
                      <div>
                        <span className="text-[10px] text-foreground-secondary block">Application Deadline</span>
                        <span className="font-semibold text-coral">Dec 15, 2026</span>
                      </div>
                    </div>

                    <div className="p-2.5 rounded-lg bg-white border border-border flex items-center gap-2">
                      <FileText className="w-4 h-4 text-coral" />
                      <div>
                        <span className="text-[10px] text-foreground-secondary block">Required Docs</span>
                        <span className="font-semibold text-foreground">Resume & Transcript</span>
                      </div>
                    </div>
                  </div>

                  {/* Suggested Next Actions Bar */}
                  <div className="pt-2 flex items-center justify-between border-t border-border text-xs">
                    <span className="text-foreground-secondary font-medium">Suggested Next Actions:</span>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        className="px-2.5 py-1.5 rounded-lg bg-white border border-border text-foreground hover:bg-background-secondary font-medium flex items-center gap-1 transition-colors cursor-pointer"
                      >
                        <PlusCircle className="w-3.5 h-3.5 text-coral" />
                        Add to Tasks
                      </button>
                      <button
                        type="button"
                        className="px-2.5 py-1.5 rounded-lg bg-coral text-white hover:bg-coral-hover font-medium flex items-center gap-1 shadow-coral-sm transition-colors cursor-pointer"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Generate Reply Draft
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
