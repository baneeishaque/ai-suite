// JS entry point for the Copilot hook commands (see
// hooks-config/copilot-hooks.example.json). Copilot runs `command` strings
// directly, so no launcher shims are needed — this file is the command target.
import { run } from "./router.js";
await run();
