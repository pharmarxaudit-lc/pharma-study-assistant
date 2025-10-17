# MCP Servers Configuration

This project uses Model Context Protocol (MCP) servers to enhance Claude Code's capabilities.

## Configured MCP Servers

### 1. Playwright MCP Server
**Purpose**: Browser automation and E2E testing
**Package**: `@playwright/mcp@latest`

**Available Tools**:
- Browser navigation and interaction
- Screenshot capture
- Page snapshot analysis
- Form filling and testing
- Console message monitoring
- Network request tracking

**Usage**: Automatically available for all E2E testing tasks in Claude Code.

### 2. Context7 MCP Server
**Purpose**: Up-to-date code documentation and examples
**Package**: `@upstash/context7-mcp@latest`

**Features**:
- Pulls version-specific documentation from official sources
- Provides current code examples and best practices
- Auto-updates to reflect latest framework/library versions
- Supports multiple programming languages and frameworks

**Usage**: Add `use context7` to your prompt when you need:
- Current documentation for a specific library version
- Up-to-date API references
- Modern code examples and patterns
- Latest best practices for frameworks

**Example Prompts**:
```
"How do I implement Vue 3 Composition API with TypeScript? use context7"
"Show me the latest Flask routing patterns use context7"
"What's the current way to handle SQLAlchemy sessions? use context7"
```

## Configuration File

MCP servers are configured in `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    }
  }
}
```

**Note**: This is a **project-scoped** configuration that:
- Is checked into version control
- Applies only to this project
- Allows team members to use the same MCP servers

## Requirements

- Node.js version 18 or higher
- npx (comes with Node.js)

## Adding New MCP Servers

To add a new MCP server:

1. Find the MCP server package (usually on npm)
2. Add configuration to `.mcp.json`:
   ```json
   {
     "mcpServers": {
       "server-name": {
         "command": "npx",
         "args": ["-y", "package-name@latest"]
       }
     }
   }
   ```
3. Restart Claude Code to load the new server
4. Update this documentation

## Troubleshooting

### MCP Server Not Loading
- Ensure Node.js 18+ is installed: `node --version`
- Check npx is available: `npx --version`
- Try clearing npm cache: `npm cache clean --force`

### Context7 Not Working
- Make sure to add `use context7` at the end of your prompt
- Check network connectivity (Context7 fetches docs from the web)
- Verify the package name is correct in config

### Playwright MCP Issues
- Ensure Playwright is installed: `npx playwright install`
- Check browser binaries are available
- Review Playwright logs in test results

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Playwright MCP Server](https://github.com/playwright/mcp)
- [Context7 MCP Server](https://github.com/upstash/context7)
- [Awesome MCP Servers](https://mcpservers.org/)

---

Last updated: 2025-10-17
