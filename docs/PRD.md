# KNIT — Product Requirements Document (PRD)

**Product Name:** KNIT  
**Tagline:** Connect. Understand. Act.  
**Product Type:** AI-Powered Email Intelligence & Automation Platform  
**Version:** 1.0

## 1. Product Overview

KNIT is an AI-powered email management platform that helps users understand, organize and manage their emails intelligently.

It reduces the effort of manually reading emails by using AI to classify messages, generate summaries, extract tasks and deadlines, identify opportunities and assist with email replies.

KNIT initially focuses on students, job seekers and professionals who regularly receive academic, internship, interview and work-related emails.

KNIT works as an intelligent layer over Gmail, not as a replacement for Gmail.

## 2. Problem Statement

Users receive large numbers of emails every day. Important information is often buried among promotions, notifications and general messages.

Users struggle to:

- Find important emails quickly.
- Identify internship and interview opportunities.
- Remember application deadlines.
- Understand long email conversations.
- Track tasks mentioned in emails.
- Write professional replies.
- Manage repetitive email activities.

KNIT aims to solve these problems through AI-powered email intelligence.

## 3. Target Users

- College students.
- Internship and job seekers.
- Working professionals.
- People who manage multiple email conversations.

## 4. Core Features

### 4.1 Smart Inbox

Organize emails into categories:

- Internship
- Interview
- College
- Important
- Personal
- Promotions
- Updates
- Suspicious
- Other

Users should be able to search, filter and open emails.

### 4.2 AI Email Summarization

Generate concise summaries of emails.

Display:
- Main purpose.
- Important information.
- Required actions.
- Important dates.

### 4.3 Smart Information Extraction

Extract useful information from emails, including:

- Tasks.
- Deadlines.
- Interview schedules.
- Application links.
- Company names.
- Job or internship roles.
- Required skills.
- Eligibility criteria.
- Required documents.

Do not invent missing information.

### 4.4 AI Email Assistant

Provide a conversational assistant that can answer questions about the user's authorized email data.

Example:
- Show my latest important emails.
- Find internship opportunities.
- Which emails contain deadlines?
- Summarize my interview invitations.
- Find emails from my college.

### 4.5 AI Reply Generator

Generate context-aware email replies.

Users can:
- Select an email.
- Choose a reply tone.
- Generate a reply.
- Edit the generated content.
- Save it as a draft.

Never send generated replies without explicit user confirmation.

### 4.6 Task Management

Convert relevant email information into manageable tasks.

Users can:
- View extracted tasks.
- View deadlines.
- Mark tasks as completed.
- Edit tasks.
- Delete tasks.

### 4.7 Dashboard and Analytics

Display useful information such as:

- Total emails.
- Category distribution.
- Important emails.
- Pending tasks.
- Upcoming deadlines.
- Recent email activity.

### 4.8 Gmail Integration

Connect the user's Gmail account through official Google OAuth 2.0 and Gmail API.

The integration should support:
- Authorized email retrieval.
- Email synchronization.
- Reading email details.
- Creating drafts.
- Approved email actions.

Gmail integration will be implemented after the sample inbox MVP.

## 5. MVP Scope

The first working MVP must include:

1. Landing page.
2. User authentication.
3. Dashboard.
4. Sample inbox.
5. Email categorization.
6. AI email summaries.
7. Information and deadline extraction.
8. AI assistant.
9. Reply generation.
10. Task management.
11. Basic analytics.

Use sample email data initially.

The sample inbox must be clearly separated from real Gmail data.

## 6. User Workflow

1. User opens KNIT.
2. User signs in.
3. User enters the dashboard.
4. User explores the sample inbox.
5. Emails are categorized and analyzed.
6. User opens an email to view its summary and extracted information.
7. User can ask the AI assistant questions.
8. User can create tasks or generate replies.
9. User reviews and confirms supported actions.

After the sample-data experience works, users can connect their real Gmail account.

## 7. Safety Requirements

- AI must not send emails automatically.
- Sending an email requires explicit confirmation.
- Users must review recipients and message content before sending.
- AI cannot perform unrestricted Gmail or database operations.
- Users can access only their own data.
- Sensitive credentials must remain on the backend.
- Suspicious email classification is an AI assessment, not a guarantee that an email is malicious.

## 8. Future Enhancements

These features are not required for the initial MVP:

- Advanced automation rules.
- Smart follow-up reminders.
- Calendar integration.
- Multiple email providers.
- Advanced opportunity tracking.
- More advanced analytics.

## 9. Success Criteria

The MVP will be considered functional when:

- Users can navigate the application.
- Sample emails display correctly.
- Email classification works.
- Summaries are generated.
- Tasks and deadlines are extracted.
- The AI assistant can answer questions using available email data.
- Reply drafts can be generated and edited.
- Tasks can be managed.
- User data and actions are protected.

## 10. Product Principle

**Connect. Understand. Act.**

KNIT should make email management intelligent, organized and user-controlled.

**End of PRD.**