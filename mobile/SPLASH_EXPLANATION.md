# Splash Screen Implementation (How We Show the Splash)

This app shows splash in **two phases** so users never see an unstyled or blank transition:

1. **Native Expo splash** (configured in `app.json`)
2. **Custom in-app splash route** (`app/splash.tsx`)

---

## 1) Native splash setup (Expo config)

In `mobile/app.json`, the `expo-splash-screen` plugin defines:

- splash image (`./assets/images/davar_nobackground.png`)
- background color (`#7AA0D6`)
- platform-specific iOS override (`./assets/images/splash-native-ios.png`)

This guarantees the app has a branded native splash before React Native UI mounts.

---

## 2) Keep native splash visible until fonts are ready

In `mobile/app/_layout.tsx`:

- `SplashScreen.preventAutoHideAsync()` is called at startup
- Custom fonts are loaded with `useFonts(...)`
- `SplashScreen.hideAsync()` runs only after fonts are loaded (or if there is a font load error)
- While loading, the layout returns `null`, so native splash stays visible

This prevents flash-of-unstyled-text and avoids a jumpy first frame.

---

## 3) Start app on custom splash route

In `mobile/app/_layout.tsx`, stack navigation uses:

- `<Stack initialRouteName="splash">`
- `<Stack.Screen name="splash" options={{ headerShown: false }} />`

So once native splash is hidden, the first JS screen shown is our custom `app/splash.tsx`.

---

## 4) Render visual splash and animate logo

In `mobile/app/splash.tsx`:

- Multiple full-screen `LinearGradient` layers create the dreamy background
- A grain/noise texture overlays the gradients
- Center logo (`davar_nobackground.png`) is animated with Reanimated:
  - pulse scale loop (`1 -> 1.05 -> 1`)
  - fade out after ~1600ms

This gives a smooth branded handoff from native splash into app content.

---

## 5) Navigate automatically to content

Also in `mobile/app/splash.tsx`:

- waits for router navigation readiness (`useRootNavigationState`) before starting flow
- after ~2100ms total, calls `router.replace("/verse")`

`/verse` resolves to `mobile/app/(tabs)/verse.tsx`, so users land directly in the reading experience.

---

## Why this works well

- No visual gap between app launch and first meaningful screen
- Fonts are guaranteed before UI display
- Branded transition feels intentional instead of abrupt
- `replace()` avoids keeping splash in back stack

This is the exact mechanism currently used in the codebase to show splash reliably and smoothly.