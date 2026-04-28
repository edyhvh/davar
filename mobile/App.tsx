import { useEffect } from "react";
import { ExpoRoot } from "expo-router";
import * as Updates from "expo-updates";

export default function App() {
  useEffect(() => {
    console.log("Expo Channel:", Updates.channel);
    console.log("Runtime Version:", Updates.runtimeVersion);
    Updates.checkForUpdateAsync()
      .then((result) => {
        console.log("Update available?", result.isAvailable);
      })
      .catch((error) => {
        console.log("Update check error:", error);
      });
  }, []);

  return <ExpoRoot context={require("./app")} />;
}
