# 🚀 Strava Developer Program Application - Quick Start Guide

## Step-by-Step Process (Estimated Time: 2-3 hours)

### Phase 1: Fix Compliance Issues (30 minutes)
**⚠️ CRITICAL - Must complete before application**

1. **Download Official Button** (10 mins)
   - Visit: https://developers.strava.com/guidelines/
   - Download official "Connect with Strava" button
   - Save to `/static/images/`

2. **Update HTML** (10 mins)
   - Replace custom button in `static/index.html:49-54`
   - Use official button image
   - Keep existing `onclick="connectStrava()"` functionality

3. **Test Implementation** (10 mins)
   - Start server: `uvicorn app.main:app --reload`
   - Visit: http://localhost:8000
   - Verify button works and looks official

### Phase 2: Gather Screenshots (45 minutes)

4. **Homepage Screenshot** (10 mins)
   - Open: http://localhost:8000
   - Take full-page screenshot
   - Save as: `strava-application-screenshot-1-homepage.png`

5. **OAuth Flow Screenshot** (15 mins)
   - Click "Connect with Strava" button
   - Screenshot the Strava authorisation page
   - Save as: `strava-application-screenshot-2-oauth.png`

6. **Working Example Screenshot** (20 mins)
   - Connect your own Strava account (if not already)
   - Complete a test workout or find existing activity
   - Screenshot the generated description on Strava
   - Save as: `strava-application-screenshot-3-description.png`

### Phase 3: Submit Application (60 minutes)

7. **Prepare Application Materials** (30 mins)
   - Review: `STRAVA_APPLICATION_GUIDE.md` (already created)
   - Customise email template: `STRAVA_SUBMISSION_EMAIL.md` (already created)
   - Organise all screenshots

8. **Submit via Strava Settings** (20 mins)
   - Visit: https://www.strava.com/settings/api
   - Find your app (Client ID: 151103)
   - Submit for Developer Program review
   - Include all prepared materials

9. **Send Follow-up Email** (10 mins)
   - Email: developers@strava.com
   - Use template from: `STRAVA_SUBMISSION_EMAIL.md`
   - Attach all screenshots
   - Include client ID: 151103

### Phase 4: Monitor and Follow-up (Ongoing)

10. **Track Application Status**
    - Monitor email for Strava responses
    - Expected timeline: 1-2 weeks
    - Check spam/junk folders

11. **Prepare for Approval**
    - Update callback domain from localhost to production
    - Prepare infrastructure for increased users
    - Monitor API usage patterns

---

## Quick Reference

### Files Created for You:
- ✅ `STRAVA_APPLICATION_GUIDE.md` - Complete application guide
- ✅ `STRAVA_SUBMISSION_EMAIL.md` - Email templates
- ⚠️ `BRAND_COMPLIANCE_ISSUES.md` - Critical fixes needed
- ✅ `SUBMISSION_QUICK_START.md` - This guide

### Key Information:
- **App Name:** LapLogic
- **Client ID:** 151103
- **Current Capacity:** 1 athlete (Single Player Mode)
- **Target Capacity:** 99 athletes (Developer Program)
- **Submission URL:** https://www.strava.com/settings/api
- **Contact Email:** developers@strava.com

### Critical Requirements:
- 🚨 Fix Connect with Strava button (see BRAND_COMPLIANCE_ISSUES.md)
- 📸 Take 3-4 application screenshots
- 📝 Complete Developer Program form
- 📧 Send follow-up email with materials

---

## Troubleshooting

### If OAuth Button Doesn't Work After Changes:
```javascript
// Ensure this function exists in static/js/main.js
function connectStrava() {
    // Your existing OAuth logic
    window.location.href = '/auth/login';
}
```

### If Application Gets Rejected:
1. Review rejection reasons carefully
2. Address specific feedback
3. Update materials accordingly
4. Resubmit with improvements

### If No Response After 2 Weeks:
- Use follow-up email template
- Reference original submission date
- Provide additional context if needed

---

**🎯 Goal:** Transform from 1 athlete capacity to 99+ athlete capacity through Developer Program approval.