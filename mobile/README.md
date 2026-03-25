# Welcome to your Expo app 👋

This is an [Expo](https://expo.dev) project created with [`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

## Get started

1. Install dependencies

   ```bash
   bun install
   ```

   (Bun creates/updates a `bun.lockb` lockfile — much faster than npm!)

2. Start the app

   ```bash
   bun expo start
   ```

   In the output, you'll find options to open the app in a

   - [development build](https://docs.expo.dev/develop/development-builds/introduction/)
   - [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
   - [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
   - [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

   You can also run platform-specific commands directly:

   ```bash
   bun run ios     # or: bun expo run:ios
   bun run android # or: bun expo run:android
   ```

   You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
bun run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Learn more

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.
- [Using Bun with Expo](https://docs.expo.dev/guides/using-bun): Official guide for Bun + Expo workflows

## Join the community

Join our community of developers creating universal apps.

- [Expo on GitHub](https://github.com/expo/expo): View our open source platform and contribute.
- [Discord community](https://chat.expo.dev): Chat with Expo users and ask questions.


### Quick notes
- Use `bun expo install <package>` (instead of `npx expo install`) when adding Expo-managed libraries — it picks the right compatible version automatically.
- If you ever need to force Bun explicitly: `bun expo start --bun`
- Bun is usually 4–25× faster than npm for installs, so you'll notice the difference right away.

## Formatting

- This repository uses Biome as the formatter/linter source of truth for JS/TS files.
- Use `bunx biome format --write .` from this `mobile/` directory when you want to format files manually.
- Prettier is intentionally not configured at project level in this workspace.

