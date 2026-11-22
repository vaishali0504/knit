import React from 'react'
import { motion } from 'framer-motion'
import {
  Link2,
  FolderTree,
  Sparkles,
  CheckCircle,
} from 'lucide-react'
import { Card } from '../ui/Card'

export const HowItWorksSection: React.FC = () => {
  const steps = [
    {
      step: '01',
      icon: Link2,
      title: 'Connect Your Gmail',
      description:
        'Authorize secure read access via official Google OAuth 2.0 with minimum required scopes. Your credentials stay strictly on the backend and are never exposed.',
    },
    {
      step: '02',
      icon: FolderTree,
      title: 'Smart Categorization',
      description:
        'KNIT normalizes raw message streams and classifies them into academic, interview, internship, important, and personal categories without touching your real mailbox.',
    },
    {
      step: '03',
      icon: Sparkles,
      title: 'Intelligence Extraction',
      description:
        'Deep natural-language analysis surfaces hard deadlines, interview dates, target roles, application links, and required attachments with zero data invention.',
    },
    {
      step: '04',
      icon: CheckCircle,
      title: 'Review & Take Action',
      description:
        'Track deadlines, convert commitments into tasks, and draft contextual replies. You stay in 100% control — emails are never sent without your explicit review.',
    },
  ]

  return (
    <section id="how-it-works" className="py-20 md:py-28 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-surface border border-border text-xs font-semibold text-coral">
            Simple 4-Step Process
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
            How KNIT transforms your email workflow
          </h2>
          <p className="text-base sm:text-lg text-foreground-secondary leading-relaxed">
            From inbox overwhelm to structured clarity in four clear, user-controlled steps.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative">
          {steps.map((item, index) => {
            const Icon = item.icon
            return (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
                className="relative"
              >
                <Card className="p-6 h-full flex flex-col justify-between border-border hover:border-coral/40 transition-colors">
                  <div className="space-y-4">
                    {/* Step Number & Icon */}
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-2xl text-coral/80">
                        {item.step}
                      </span>
                      <div className="w-10 h-10 rounded-xl bg-pink-surface flex items-center justify-center text-coral">
                        <Icon className="w-5 h-5" />
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-foreground">
                      {item.title}
                    </h3>

                    <p className="text-xs sm:text-sm text-foreground-secondary leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
