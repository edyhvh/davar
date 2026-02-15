# Splash Screen Implementation

This document explains how the splash screen is implemented for both iOS and Android platforms.

---

## iOS Implementation

iOS uses a **full-screen native splash image** that covers the entire screen until the app is ready.

### Configuration (`app.json`)

```json
"ios": {
  "image": "./assets/images/splash-native-ios.png",
  "resizeMode": "cover",
  "backgroundColor": "#7AA0D6",
  "enableFullScreenImage_legacy": true
}
```

### Required Asset

| Asset | Size | Purpose |
|-------|------|---------|
| `splash-native-ios.png` | **1179×2556px** (iPhone 14 Pro Max) or **1284×2778px** | Full-screen splash image |

### How it works

1. iOS displays the full-screen image immediately on app launch
2. The image covers the entire screen with `resizeMode: "cover"`
3. Once fonts are loaded, `SplashScreen.hideAsync()` reveals the app

---

## Android Implementation

Android 12+ (API 31+) uses the **SplashScreen API** which has specific limitations:
- Only supports **background color** + **centered icon** (max 288dp)
- Does NOT support full-screen background images
- Logo is displayed centered in a circle mask

### Configuration (`app.json`)

```json
"android": {
  "image": "./assets/images/splash-logo-android.png",
  "resizeMode": "contain",
  "backgroundColor": "#7AA0D6"
}
```

### Required Asset

| Asset | Size | Purpose |
|-------|------|---------|
| `splash-logo-android.png` | **288×288dp** (576×576px recommended) | Centered logo on transparent background |

### How it works

1. Android displays a solid background color (`#7AA0D6`)
2. Your logo appears centered on the screen (contained within the display area)
3. Once fonts are loaded, `SplashScreen.hideAsync()` reveals the app

### Generated Resources

Expo prebuild generates these density-specific versions:

| Density | Generated Size | Path |
|---------|----------------|------|
| mdpi | 48×48px | `android/app/src/main/res/drawable-mdpi/splashscreen_logo.png` |
| hdpi | 72×72px | `android/app/src/main/res/drawable-hdpi/splashscreen_logo.png` |
| xhdpi | 96×96px | `android/app/src/main/res/drawable-xhdpi/splashscreen_logo.png` |
| xxhdpi | 144×144px | `android/app/src/main/res/drawable-xxhdpi/splashscreen_logo.png` |
| xxxhdpi | 192×192px | `android/app/src/main/res/drawable-xxxhdpi/splashscreen_logo.png` |

---

## Common Implementation (`_layout.tsx`)

Both platforms use the same React Native logic:

1. `SplashScreen.preventAutoHideAsync()` keeps the native splash visible
2. Fonts are loaded with `useFonts(...)`
3. `SplashScreen.hideAsync()` runs after fonts are ready
4. While loading, the layout returns `null` so the native splash stays visible

This prevents flash-of-unstyled-text and ensures a smooth transition.

---

## Platform Differences Summary

| Feature | iOS | Android 12+ |
|---------|-----|-------------|
| **Image type** | Full-screen | Centered logo only |
| **Background** | Image covers all | Solid color only |
| **Resize mode** | `cover` | `contain` |
| **Max logo size** | Full screen | 288dp diameter |

---

## Rebuilding After Changes

After modifying splash assets or configuration:

```bash
cd mobile

# Clean and regenerate native resources
bunx expo prebuild --clean --platform ios
bunx expo prebuild --clean --platform android

# Or both at once
bunx expo prebuild --clean
```

---

## Why Different Approaches?

- **iOS**: Supports full-screen splash images natively
- **Android 12+**: SplashScreen API is restrictive by design (performance/security)

The centered logo approach on Android is the standard pattern for modern Android apps and provides a consistent experience across the platform.
