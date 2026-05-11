# Agent Skills

A collection of **Agent Skills** — structured knowledge packages that give AI assistants specialized capabilities and guided workflows. Skills follow the [Agent Skills specification](https://agentskills.io).

This repository contains skills that work across open-source frameworks, tools and workflows that benefit from community input. For Amazon specific skills covering proprietary SDKs, APIs, and  workflows, see [amazon-devices-buildertools](https://github.com/AmazonAppDev/amazon-devices-buildertools).

## Available Skills

| Skill | Description |
|-------|-------------|
| [vega-multi-tv-migration](vega-multi-tv-migration/SKILL.md) | Migrate Vega OS (Fire TV) apps to multi-platform React Native monorepo supporting Android TV, Apple TV, and more |
| [rn-tv-ui-best-practices](rn-tv-ui-best-practices/SKILL.md) | React Native TV UI best practices for tvOS, Android TV, Fire TV, and Vega OS — focus management, layouts, typography, and remote/D-pad navigation |

## Installation

### 1. Install via skills.sh (Recommended)

The quickest way to install a skill is with the [skills.sh](https://skills.sh/) CLI. No setup needed, just run it with `npx`.

Install all skills from this repo:

```bash
npx skills add AmazonAppDev/devices-agent-skills
```

Install a specific skill:

```bash
npx skills add AmazonAppDev/devices-agent-skills --skill vega-multi-tv-migration
npx skills add AmazonAppDev/devices-agent-skills --skill rn-tv-ui-best-practices
```

For more options, see the [skills CLI documentation](https://skills.sh/docs/cli).

### 2. Manual Installation

1. Copy a skill directory into your AI assistant's skills folder (e.g. `~/.kiro/skills/` for Kiro).
2. The assistant will automatically discover and activate the skill based on your conversation.

## Usage

Once installed, your AI agent will automatically activate the skill when your conversation matches its topic. The agent uses the skill's guides and references to walk you through the right workflow for your situation.

You can also open any skill's `SKILL.md` directly to browse its phases, reference docs, and templates.

## Contributing

We welcome contributions, whether it's improving existing skills, adding new ones, or sharing feedback. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

See individual skill directories for details.
