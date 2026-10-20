---
name: testing-debugging
description: Guide for running the website and testing it locally
---

# Testing & Debugging Guide

## Local Testing

### Building and Serving

1. Build the site:
   ```bash
   python3 build.py
   ```

2. Serve locally:
   ```bash
   python3 -m http.server 8000
   ```

3. Open browser to `http://localhost:8000`

### What to Test After Building

- Verify `index.html` was generated
- Check console output for cache buster hash
- Ensure no Python errors during build
- Verify all Dicier codes rendered correctly
- Check TOC links navigate properly
- Test decorative headers appear after H1/H2

## Browser Compatibility Testing

Test on all modern browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Cross-Browser Issues to Watch For

- CSS grid/flexbox inconsistencies
- Font rendering differences
- JavaScript event handling
- Smooth scrolling behavior

## Responsive Testing

### Test Viewport Sizes

- **Mobile Portrait**: 320px, 375px, 414px width
- **Mobile Landscape**: 568px, 667px, 736px width
- **Tablet**: 768px, 1024px width
- **Desktop**: 1280px, 1440px, 1920px width

### Mobile-Specific Checks

- Burger menu appears at ≤768px
- Burger menu toggles sidebar correctly
- Sidebar hidden by default on mobile
- Clicking outside sidebar closes it
- Clicking TOC link closes sidebar
- No horizontal scroll at any size
- Touch targets are easily tappable (≥44×44px)
- Text remains readable on small screens

### Tools for Responsive Testing

- Browser DevTools device emulation
- Actual mobile devices (best option)
- BrowserStack or similar services
- Responsively App

## Accessibility Testing

### Screen Reader Testing

Test with these screen readers:
- **NVDA** (Windows) - Free
- **JAWS** (Windows) - Commercial
- **VoiceOver** (macOS/iOS) - Built-in
- **TalkBack** (Android) - Built-in

### Accessibility Checklist

- [ ] First tab reveals "Skip to main content" link
- [ ] Skip link navigates to main content
- [ ] All images have appropriate alt text
- [ ] Decorative images use `alt=""` + `aria-hidden="true"`
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible on all interactive elements
- [ ] Screen reader announces all content correctly
- [ ] ARIA labels present where needed
- [ ] Color contrast meets WCAG AA standards

### Keyboard Navigation Testing

Test these keyboard interactions:
- **Tab**: Move forward through interactive elements
- **Shift+Tab**: Move backward
- **Enter**: Activate links and buttons
- **Escape**: Close sidebar (should work)
- **Arrow keys**: Scroll page content

### Contrast Testing Tools

- Chrome DevTools (Lighthouse)
- WebAIM Contrast Checker
- axe DevTools browser extension

## Visual Regression Testing

### After Modifying styles.css

1. Run `python3 build.py` to regenerate with new cache buster
2. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Check new cache buster hash in console output
4. Verify styles applied correctly
5. Test all breakpoints (see Responsive Testing)
6. Check color contrast (see Accessibility Testing)

### Screenshot Comparison

For major style changes:
- Take "before" screenshots at key breakpoints
- Make changes and rebuild
- Take "after" screenshots
- Compare side-by-side for unintended changes

## Common Issues

### CSS Not Updating

If CSS changes aren't appearing:
1. Run `python build.py` to regenerate with new cache buster
2. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for 404 errors

### Dicier Codes Not Working

If `{dicier:CODE}` syntax isn't rendering:
1. Verify the syntax is correct: `{dicier:CODE}` not `{dicier: CODE}` (no spaces)
2. Check that the DicierPreprocessor is running in build.py
3. See dicier-user-guide skill for troubleshooting specific codes