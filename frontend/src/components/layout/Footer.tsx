import React from 'react'
import { Mail, ShieldCheck, Lock } from 'lucide-react'

export const Footer: React.FC = () => {
  return (
    <footer id="about" className="border-t border-border bg-white pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 pb-12 border-b border-border">
          {/* Brand Column */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-coral flex items-center justify-center text-white shadow-coral-sm">
                <Mail className="w-5 h-5" />
              </div>
              <span className="font-extrabold text-2xl tracking-tight text-foreground">
                KNIT
              </span>
            </div>
            <p className="text-sm font-medium text-coral tracking-wide">
              Connect. Understand. Act.
            </p>
            <p className="text-sm text-foreground-secondary leading-relaxed max-w-sm">
              KNIT is an intelligent email productivity platform that operates as a secure companion layer over Gmail. Designed for students, job applicants, and professionals managing critical communications.
            </p>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-pink-surface border border-border text-xs text-foreground font-medium">
              <ShieldCheck className="w-4 h-4 text-coral" />
              <span>Official Google OAuth 2.0 & Gmail API Compliance</span>
            </div>
          </div>

          {/* Product Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Product
            </h4>
            <ul className="space-y-2 text-sm text-foreground-secondary">
              <li>
                <a href="#features" className="hover:text-coral transition-colors">
                  Smart Inbox
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-coral transition-colors">
                  AI Summaries
                </a>
              </li>
              <li>
                <a href="#preview" className="hover:text-coral transition-colors">
                  Opportunity Extraction
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-coral transition-colors">
                  Tasks & Deadlines
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-coral transition-colors">
                  Contextual Replies
                </a>
              </li>
            </ul>
          </div>

          {/* Workflow & Architecture */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Architecture
            </h4>
            <ul className="space-y-2 text-sm text-foreground-secondary">
              <li>
                <a href="#how-it-works" className="hover:text-coral transition-colors">
                  How KNIT Works
                </a>
              </li>
              <li>
                <a href="#gmail-integration" className="hover:text-coral transition-colors">
                  Gmail Security & Privacy
                </a>
              </li>
              <li>
                <span className="text-foreground-secondary/70">
                  Modular Monolith
                </span>
              </li>
              <li>
                <span className="text-foreground-secondary/70">
                  SQLite to PostgreSQL
                </span>
              </li>
            </ul>
          </div>

          {/* Trust & Legal */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-foreground">
              Trust & Legal
            </h4>
            <ul className="space-y-2 text-sm text-foreground-secondary">
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-coral" />
                <span>Zero Auto-Sending Rule</span>
              </li>
              <li>
                <span className="text-foreground-secondary">
                  Explicit User Confirmation
                </span>
              </li>
              <li>
                <span className="text-foreground-secondary">
                  Read-Only Scopes by Default
                </span>
              </li>
              <li>
                <span className="text-foreground-secondary">
                  Encrypted Token Storage
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-foreground-secondary gap-4">
          <p>© 2026 KNIT. All rights reserved. Built with pride for intelligent email management.</p>
          <div className="flex items-center gap-6">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Security</span>
            <span>Status</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
