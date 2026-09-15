// JS entry point for the Claude hook commands (see
// settings-snippet.json). Each event's command invokes this file directly;
// it prints nothing and exits 0 so the session log never disturbs Claude.
import { run } from "./router.js";
await run();
