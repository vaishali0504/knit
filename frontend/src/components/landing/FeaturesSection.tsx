import React from 'react'
import { motion } from 'framer-motion'
import {
  Inbox,
  Sparkles,
  Briefcase,
  CheckSquare,
  MessageSquare,
  BarChart3,
  ArrowRight,
} from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'

export const FeaturesSection: React.FC = () => {
  const features = [
    {
      id: 'smart-inbox',
      icon: Inbox,
      title: 'Smart Inbox Categorization',
      badge: 'Automatic Triage',
      description:
        'Automatically organizes incoming messages into dedicated buckets: Internship, Interview, College, Important, Personal, and Updates so you can focus on priority communications first.',
    },
    {
      id: 'ai-summaries',
      icon: Sparkles,
      title: 'AI Email Summaries',
      badge: 'Instant Clarity',
      description:
        'Converts dense threads and repetitive announcements into clear, concise 2-sentence summaries highlighting the main objective, key facts, and required follow-ups.',
    },
    {
      id: 'opportunity-extraction',
      icon: Briefcase,
      title: 'Opportunity Extraction',
      badge: 'Never Miss a Role',
      description:
        'Detects internship roles, recruiting contacts, eligibility criteria, required skills, and direct application links buried inside emails without hallucinating missing data.',
    },
    {
      id: 'tasks-deadlines',
      icon: CheckSquare,
      title: 'Tasks & Deadlines',
      badge: 'Actionable Workflow',
      description:
        'Converts commitments, submission requests, and calendar dates into manageable to-do tasks linked directly back to their source email for complete accountability.',
    },
    {
      id: 'contextual-replies',
      icon: MessageSquare,
      title: 'Contextual AI Reply Generation',
      badge: 'User Supervised',
      description:
        'Generates polite, professional replies using the context of the email conversation. You review, edit, and confirm before anything is saved as a draft or sent.',
    },
    {
      id: 'email-analytics',
      icon: BarChart3,
      title: 'Email Productivity Analytics',
      badge: 'Inbox Intelligence',
      description:
        'Gain visibility into your email volume, application pipeline status, upcoming weekly deadlines, and category distribution through clean, restrained visual metrics.',
    },
  ]

  return (
    <section id="features" className="py-20 md:py-28 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-surface border border-border text-xs font-semibold text-coral">
            Core Platform Capabilities
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
            Everything you need to master your inbox.
          </h2>
          <p className="text-base sm:text-lg text-foreground-secondary leading-relaxed">
            Engineered specifically for students, internship seekers, and professionals who regularly receive critical academic and career emails.
          </p>
        </div>

        {/* Feature Cards Grid (3x2) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.4, delay: index * 0.08 }}
              >
                <Card
                  variant="interactive"
                  className="h-full flex flex-col justify-between p-7 hover:border-coral/50"
                >
                  <div className="space-y-4">
                    {/* Top Icon & Badge Row */}
                    <div className="flex items-center justify-between">
                      <div className="w-12 h-12 rounded-xl bg-pink-surface flex items-center justify-center text-coral shadow-xs">
                        <Icon className="w-6 h-6" />
                      </div>
                      <Badge variant="pink" size="sm">
                        {feature.badge}
                      </Badge>
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-bold text-foreground tracking-tight pt-1">
                      {feature.title}
                    </h3>

                    {/* Description */}
                    <p className="text-sm text-foreground-secondary leading-relaxed">
                      {feature.description}
                    </p>
                  </div>

                  {/* Bottom Accent */}
                  <div className="pt-6 mt-4 border-t border-border flex items-center text-xs font-semibold text-coral group">
                    <span>Learn more</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 transition-transform group-hover:translate-x-1" />
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
