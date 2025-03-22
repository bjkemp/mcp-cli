# MCP-MIDI CLI Documentation

This repository contains documentation and diagrams for the MCP-MIDI project, a Model Context Protocol (MCP) server implementation that provides MIDI device interaction capabilities.

## Diagrams

The `diagrams/` directory contains Mermaid.js diagrams that document the structure and functioning of the MCP-MIDI system:

- `system-overview.mmd`: High-level architecture of the MCP-MIDI system
- `project-structure.mmd`: Organization of the codebase and key files
- `midi-communication.mmd`: Flow of commands and data between components
- `tracker-structure.mmd`: Data structure of the tracker implementation
- `api-endpoints.mmd`: API endpoints provided by the server
- `claude-integration.mmd`: Ways Claude can integrate with the MCP-MIDI system

## Viewing Diagrams

These diagrams can be viewed in any Mermaid.js compatible viewer:

1. Visual Studio Code with the Mermaid extension
2. Online at [Mermaid Live Editor](https://mermaid.live/)
3. GitHub (which natively renders Mermaid diagrams in Markdown)
4. Many other Markdown editors with Mermaid support

## MCP-MIDI Overview

MCP-MIDI is a server that enables:

- Sending MIDI messages to control synthesizers
- Playing notes and chords
- Changing instruments and sounds
- Manipulating controller parameters
- Creating and playing MIDI sequences
- Loading and playing MIDI files
- Using a tracker-like format for music composition

It can be integrated with Claude AI through the MCP protocol for natural language control of MIDI devices.

## License

This documentation is licensed under the MIT License.