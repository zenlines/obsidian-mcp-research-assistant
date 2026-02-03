# AI-Assisted Knowledge Management for Obsidian

## Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Claude Desktop](https://claude.ai/download)
- [Obsidian](https://obsidian.md/)

--- 

### Setup

1. Clone this repo
```bash
git clone https://github.com/zenlines/obsidian-mcp-research-assistant.git
cd obsidian-mcp-research-assistant
```

2. Create the vault directory. Open Obsidian → Open folder as vault → select your new vault, ex. 'obsidian-vault'


3. In Claude Desktop, add this to Settings → Developer → Edit Config:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "YOUR_ABSOLUTE_PATH_HERE/obsidian_vault"
      ]
    }
  }
}
```

Replace `YOUR_ABSOLUTE_PATH_HERE/obsidian_vault` with your actual path.

4. Restart Claude Desktop

Done.

## Usage

Ask Claude: "Can you list the files in the Obsidian vault on my machine that you have access to with the filesystem MCP server?"

If working correctly, Claude will use the filesystem tools to list the contents of your vault.

## Safety

The MCP server can only access the contents of the vault folder you specify.