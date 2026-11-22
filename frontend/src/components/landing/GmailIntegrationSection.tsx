import React from 'react'
import { motion } from 'framer-motion'
import {
  ShieldCheck,
  Lock,
  Eye,
  KeyRound,
  FileCheck2,
  CheckCircle2,
} from 'lucide-react'
import { Card } from '../ui/Card'

export const GmailIntegrationSection: React.FC = () => {
  const securityPoints = [
    {
      icon: Eye,
      title: 'Read-Only Permissions First',
      description: 'Starts with minimum required read scopes. KNIT only requests permissions necessary for organizing and summarizing.',
    },
    {
      icon: Lock,
      title: 'Zero Auto-Sending Policy',
      description: 'KNIT will never send an email automatically. Any outgoing communication requires explicit review and confirmation from you.',
    },
    {
      icon: KeyRound,
      title: 'Backend-Encrypted Tokens',
      description: 'OAuth tokens and credentials are securely encrypted on the backend and never exposed to client-side browser JavaScript.',
    },
    {
      icon: FileCheck2,
      title: 'Independent Sample Sandbox First',
      description: 'Explore all AI classification, extraction, and drafting features using our realistic sample sandbox before connecting your live account.',
    },
  ]

  return (
    <section id="gmail-integration" className="py-20 md:py-28 bg-background-secondary/40 border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Copy & Messaging */}
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="lg:col-span-5 space-y-6 text-left"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-surface border border-border text-xs font-semibold text-coral">
              <ShieldCheck className="w-3.5 h-3.5" />
              Security & Privacy Architecture
            </div>

            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground leading-tight">
              Built securely on official Google standards.
            </h2>

            <p className="text-base text-foreground-secondary leading-relaxed">
              KNIT functions as an intelligent layer over Gmail, not a replacement. We adhere strictly to Google API Services User Data Policies and enterprise-grade privacy boundaries.
            </p>

            <div className="p-4 rounded-xl bg-pink-surface border border-border/80 space-y-2">
              <div className="flex items-center gap-2 text-xs font-bold text-coral">
                <CheckCircle2 className="w-4 h-4" />
                <span>Transparent Staging Commitment</span>
              </div>
              <p className="text-xs text-foreground leading-relaxed">
                Live Gmail authorization is part of <strong>Phase 10</strong>. You can test every AI summarization and extraction capability immediately in our isolated demo inbox without linking external accounts.
              </p>
            </div>
          </motion.div>

          {/* Right Column: 4 Security Cards */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-4">
            {securityPoints.map((point, index) => {
              const Icon = point.icon
              return (
                <motion.div
                  key={point.title}
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: index * 0.08 }}
                >
                  <Card className="p-5 h-full bg-white border-border hover:border-coral/40 transition-colors">
                    <div className="w-9 h-9 rounded-xl bg-pink-surface flex items-center justify-center text-coral mb-3">
                      <Icon className="w-4.5 h-4.5" />
                    </div>
                    <h3 className="text-sm font-bold text-foreground mb-1">
                      {point.title}
                    </h3>
                    <p className="text-xs text-foreground-secondary leading-relaxed">
                      {point.description}
                    </p>
                  </Card>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
