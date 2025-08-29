# ⚠️ Brand Compliance Issues - Action Required

## Current Connect with Strava Button Issues

### 🚨 Non-Compliant Implementation Detected

Your current "Connect with Strava" button does **NOT** comply with Strava's brand guidelines and **MUST** be updated before submitting your Developer Program application.

### Issues Identified:

1. **Custom Button Design** ❌
   - Currently using: Custom styled button with manual Strava logo SVG
   - Required: Official Strava "Connect with Strava" button assets

2. **Incorrect Visual Specifications** ❌
   - Current: Custom dimensions and styling
   - Required: 48px @1x, 96px @2x official button

3. **Manual Logo Implementation** ❌
   - Current: Hand-coded SVG path in HTML
   - Required: Official Strava button graphics (EPS, SVG, PNG)

### Required Actions:

#### 1. Download Official Assets
- Visit: https://developers.strava.com/guidelines/
- Download official "Connect with Strava" button files
- Available formats: EPS, SVG, PNG
- Available colors: Orange and White

#### 2. Replace Current Implementation
**Current Code (lines 49-54 in index.html):**
```html
<button class="cta-button primary" onclick="connectStrava()" aria-label="Connect with Strava to start automatic workout descriptions">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.599h4.172L10.463 0l-7 14.828h4.172"/>
    </svg>
    Connect with Strava
</button>
```

**Required Replacement:**
```html
<!-- Use official Strava button image -->
<a href="[OAuth URL]" onclick="connectStrava(); return false;">
    <img src="/static/images/connect-with-strava-button.png" alt="Connect with Strava" width="193" height="48">
</a>
```

#### 3. Update Styling
- Remove all custom button styling for Strava connection
- Use official button dimensions: 48px height
- Ensure proper linking to OAuth endpoints

### Compliance Requirements:

✅ **Must Link To:**
- `https://www.strava.com/oauth/authorize` OR
- `https://www.strava.com/oauth/mobile/authorize`

✅ **Mandatory Text:**
- Exact text: "Connect with Strava"

✅ **Visual Specifications:**
- Height: 48px @1x, 96px @2x
- Use only official color variants (orange/white)
- No modifications or variations allowed

### Action Priority: CRITICAL

**This must be fixed BEFORE submitting your Developer Program application.**

Strava explicitly states: *"No variations or modifications are acceptable"* for the Connect with Strava button.

### Next Steps:

1. **Download Assets**: Get official button from https://developers.strava.com/guidelines/
2. **Update HTML**: Replace custom button with official asset
3. **Remove CSS**: Remove custom styling for Strava button
4. **Test Implementation**: Verify OAuth flow still works
5. **Take New Screenshots**: Update application screenshots with compliant button
6. **Submit Application**: Only after compliance is verified

---

**⚠️ WARNING:** Submitting with non-compliant branding may result in automatic application rejection.