# Claude adapter

- Follow the active Claude Code permission model and repository instructions.
- Prefer read-only discovery before mutations.
- Present approval gates with the exact action, target, impact, verification, and rollback.
- Do not infer success from an issued command; inspect its exit status and the system state.
- Keep platform-specific tool names out of the portable runbook unless they are essential to the procedure.
- Never claim an external mutation, deployment, message, or test succeeded without evidence or user confirmation.
