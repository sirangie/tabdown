# tabdown

Convert browser tab sessions to structured markdown for note-taking and archiving.

---

## Installation

```bash
pip install tabdown
```

## Usage

Export your browser tabs to a JSON session file, then run:

```bash
tabdown export session.json --output notes.md
```

**Example output:**

```markdown
# Tab Session — 2024-01-15

## Research
- [Python Docs](https://docs.python.org) — Official Python documentation
- [Real Python](https://realpython.com) — Tutorials and articles

## Work
- [GitHub](https://github.com) — Open pull requests
```

You can also pipe directly from supported browser extensions:

```bash
tabdown export --clipboard --output notes.md
```

### Options

| Flag | Description |
|------|-------------|
| `--output` | Output file path (default: stdout) |
| `--group-by` | Group tabs by `domain`, `window`, or `tag` |
| `--format` | Output format: `markdown`, `org`, `plain` |
| `--clipboard` | Read session data from clipboard |

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

## License

MIT © tabdown contributors