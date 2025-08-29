# LapLogic - Strava Developer Program Application Guide

## Application Overview
**App Name:** LapLogic  
**Client ID:** 151103  
**Current Status:** Single Player Mode (1 athlete capacity)  
**Target:** Developer Program approval for 99+ athlete capacity  

## Required Screenshots Checklist

### ✅ Screenshot 1: Landing Page
- **What to capture:** Full homepage showing LapLogic branding and "Connect with Strava" button
- **Location:** http://localhost:8000
- **Key elements to highlight:**
  - Clean, professional interface
  - Clear value proposition
  - Prominent Strava connection button
  - Workout capability examples

### ✅ Screenshot 2: OAuth Flow
- **What to capture:** Strava authorization page
- **How to get it:** Click "Connect with Strava" button
- **Key elements to highlight:**
  - Standard OAuth flow
  - Requested permissions clearly shown
  - Professional app presentation

### ✅ Screenshot 3: Data Usage Example
- **What to capture:** Generated workout description on Strava
- **Requirements:** Show how LapLogic adds value to Strava activities
- **Key elements to highlight:**
  - Professional workout descriptions
  - Interval detection results
  - Enhanced activity information

### ✅ Screenshot 4: Mobile Interface (Optional)
- **What to capture:** Mobile-responsive design
- **Device:** iPhone or Android
- **Key elements to highlight:**
  - Mobile-optimised layout
  - Touch-friendly interface

## Application Description Template

### App Purpose
LapLogic is an intelligent workout analysis tool that automatically generates professional descriptions for Strava activities. The application uses sophisticated interval detection algorithms to identify training patterns and creates detailed, readable summaries that enhance athletes' training logs.

### Key Features
- **Automated Analysis:** Real-time processing of Strava activity data upon completion
- **Intelligent Detection:** Recognises time-based intervals, distance intervals, and complex training patterns
- **Professional Descriptions:** Generates clean, readable workout summaries (e.g., "8 x 400m", "Pyramid: 200m-400m-800m-400m-200m")
- **Seamless Integration:** One-time connection with automatic processing of all future workouts

### Technical Implementation
- **OAuth 2.0 Authentication:** Standard Strava authentication flow
- **Webhook Integration:** Processes activities immediately upon completion
- **Minimal API Usage:** Efficient data processing to respect rate limits
- **Australian-based Development:** Developed with attention to international athlete community

### Target Audience
- **Serious Athletes:** Track training progression with detailed logs
- **Coaches:** Monitor athlete workouts with comprehensive summaries
- **Training Groups:** Standardise workout documentation across teams

### Data Usage Justification
LapLogic accesses Strava activity data solely to provide enhanced descriptions. The app:
- Analyses lap times and distances for interval detection
- Reads activity metadata for context
- Writes back professional descriptions to improve user experience
- Does not store sensitive personal data beyond necessary OAuth tokens

### Compliance Statement
- Fully compliant with Strava Brand Guidelines
- Implements standard "Connect with Strava" branding
- Respects API rate limits and best practices
- Provides clear value addition to the Strava ecosystem

## Submission Checklist

### Before Submitting
- [ ] Test OAuth flow thoroughly
- [ ] Verify "Connect with Strava" button styling matches guidelines
- [ ] Take all required screenshots
- [ ] Prepare detailed app description
- [ ] Review Strava API Terms of Service
- [ ] Confirm webhook endpoint is properly configured

### Screenshots Required
- [ ] Homepage with Connect button
- [ ] OAuth authorization flow
- [ ] Example of generated workout descriptions
- [ ] (Optional) Mobile interface

### Application Details
- [ ] App name: LapLogic
- [ ] Category: Fitness/Training Analysis
- [ ] Description: Comprehensive explanation of functionality
- [ ] Authorization Callback Domain: Currently localhost (will update for production)

### Post-Submission
- [ ] Monitor for Strava team response
- [ ] Be prepared to answer follow-up questions
- [ ] Update callback domain when approved
- [ ] Test with increased athlete capacity

## Contact Information for Follow-up

**Primary Contact:** developers@strava.com  
**Subject:** Developer Program Application - LapLogic (Client ID: 151103)  
**Response Time:** Typically 1-2 weeks

## Next Steps After Approval

1. **Update Callback Domain:** Change from localhost to production domain
2. **Implement Rate Limit Monitoring:** Track API usage against new limits
3. **Scale Infrastructure:** Prepare for increased user load
4. **Monitor Webhook Performance:** Ensure reliable activity processing
5. **User Onboarding:** Prepare for athlete community access

---

**Application Date:** [To be filled when submitting]  
**Status:** Pending Submission  
**Expected Approval Timeframe:** 1-2 weeks