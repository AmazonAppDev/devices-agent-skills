# Agent Skills

A collection of **Agent Skills** — structured knowledge packages that give AI assistants specialized capabilities and guided workflows. Skills follow the [Agent Skills specification](https://agentskills.io).

## Available Skills

| Skill | Description |
|-------|-------------|
| [vega-multi-tv-migration](vega-multi-tv-migration/SKILL.md) | Migrate Vega OS (Fire TV) apps to multi-platform React Native monorepo supporting Android TV, Apple TV, and more |

## How to Use

### 1. Install via skills.sh (Recommended)

The quickest way to install a skill is with the [skills.sh](https://skills.sh/) CLI. No setup needed, just run it with `npx`.

Install all skills from this repo:

```bash
npx skills add AmazonAppDev/devices-agent-skills
```

Install a specific skill:

```bash
npx skills add AmazonAppDev/devices-agent-skills --skill vega-multi-tv-migration
```

For more options, see the [skills CLI documentation](https://skills.sh/docs/cli).

### 2. Manual Installation

1. Copy a skill directory into your AI assistant's skills folder (e.g. `~/.kiro/skills/` for Kiro).
2. The assistant will automatically discover and activate the skill based on your conversation.

### Using a Skill

Once installed, tell the assistant which phase or task you need help with, and it will load the appropriate reference documents and guide you through.

Each skill's reference documents also work as standalone step-by-step guides. Start with `SKILL.md` for an overview, then follow the referenced phases in order.

## Contributing

We welcome contributions, whether it's improving existing skills, adding new ones, or sharing feedback. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

See individual skill directories for details.
