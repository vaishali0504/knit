import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles } from 'lucide-react'
import { Button } from '../ui/Button'

interface FinalCtaSectionProps {
  onGetStartedClick?: () => void
}

export const FinalCtaSection: React.FC<FinalCtaSectionProps> = ({
  onGetStartedClick,
}) => {
  return (
    <section className="py-20 md:py-28 bg-white">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="rounded-3xl bg-pink-surface border border-border p-8 sm:p-12 md:p-16 text-center space-y-6 max-w-4xl mx-auto shadow-coral-sm"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-border text-xs font-semibold text-coral">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Start Today with Zero Setup</span>
          </div>

          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-foreground max-w-2xl mx-auto leading-tight">
            Make every important email count.
          </h2>

          <p className="text-base sm:text-lg text-foreground-secondary max-w-xl mx-auto leading-relaxed">
            Never miss an internship application deadline or interview invitation again. Experience intelligent email management built for your career.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              variant="primary"
              size="lg"
              onClick={onGetStartedClick || (() => {
                window.scrollTo({ top: 0, behavior: 'smooth' })
              })}
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 ml-1" />
            </Button>
          </div>

          <p className="text-xs text-foreground-secondary pt-2">
            Free during public preview &bull; No credit card required &bull; Works alongside Gmail
          </p>
        </motion.div>
      </div>
    </section>
  )
}
