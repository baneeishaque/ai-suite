// n8n workflow: OpenCode Test Workflow
// Workflow ID: D3KPmTaFtCSCjUxO
// Project: personal
//
// Git is the source of truth. Deploy a new workflow with
// n8n_create_workflow_from_code, or apply changes to the existing one with
// n8n_update_workflow. Keep the workflow ID above stable so edits target the
// same workflow, and mirror every canvas change back into this file.

import { workflow, node, trigger, expr } from '@n8n/workflow-sdk';

const startTest = trigger({
  type: 'n8n-nodes-base.manualTrigger',
  version: 1,
  config: {
    name: 'Start Test',
    position: [240, 300],
  },
});

const buildTestMessage = node({
  type: 'n8n-nodes-base.set',
  version: 3.5,
  config: {
    name: 'Build Test Message',
    position: [540, 300],
    parameters: {
      mode: 'manual',
      includeOtherFields: false,
      assignments: {
        assignments: [
          { id: 'message', name: 'message', value: 'Hello from opencode', type: 'string' },
          { id: 'source', name: 'source', value: 'opencode', type: 'string' },
          { id: 'run-at', name: 'runAt', value: expr('{{ $now.toISO() }}'), type: 'string' },
        ],
      },
    },
  },
});

export default workflow('opencode-test-workflow', 'OpenCode Test Workflow')
  .add(startTest)
  .to(buildTestMessage);
