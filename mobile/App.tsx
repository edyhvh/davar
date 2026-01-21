import { ExpoRoot } from "expo-router";
export default function App() {
  return <ExpoRoot context={require("./app")} />;
}
