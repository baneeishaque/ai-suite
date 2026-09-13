// JS entry point for the Cline hook launchers (the extensionless shims in the
// parent directory). Split out because Cline requires extensionless hook files
// while node needs an explicit entry it can resolve as ESM.
import { run } from "./router.js";
await run();
