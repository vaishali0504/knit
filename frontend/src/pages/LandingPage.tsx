import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Navbar } from '../components/layout/Navbar'
import { HeroSection } from '../components/landing/HeroSection'
import { FeaturesSection } from '../components/landing/FeaturesSection'
import { EmailIntelligenceSection } from '../components/landing/EmailIntelligenceSection'
import { HowItWorksSection } from '../components/landing/HowItWorksSection'
import { GmailIntegrationSection } from '../components/landing/GmailIntegrationSection'
import { FinalCtaSection } from '../components/landing/FinalCtaSection'
import { Footer } from '../components/layout/Footer'

export const LandingPage: React.FC = () => {
  const navigate = useNavigate()

  const handleSignIn = () => {
    navigate('/login')
  }

  const handleGetStarted = () => {
    navigate('/register')
  }

  return (
    <div className="min-h-screen bg-background flex flex-col selection:bg-pink-surface selection:text-coral">
      {/* Section 1: Minimal Approved Navbar */}
      <Navbar
        onSignInClick={handleSignIn}
        onGetStartedClick={handleGetStarted}
      />

      {/* Main Content Sections */}
      <main className="flex-1">
        {/* Section 2: Hero Section */}
        <HeroSection
          onGetStartedClick={handleGetStarted}
          onSeeHowItWorksClick={() => {
            document.querySelector('#how-it-works')?.scrollIntoView({ behavior: 'smooth' })
          }}
        />

        {/* Section 3: Features Section */}
        <FeaturesSection />

        {/* Section 4: Email Intelligence Preview */}
        <EmailIntelligenceSection />

        {/* Section 5: How It Works */}
        <HowItWorksSection />

        {/* Section 6: Gmail Integration & Privacy */}
        <GmailIntegrationSection />

        {/* Section 7: Final CTA */}
        <FinalCtaSection
          onGetStartedClick={handleGetStarted}
        />
      </main>

      {/* Section 8: Approved Footer */}
      <Footer />
    </div>
  )
}
