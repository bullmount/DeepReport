# Deep Research for the italian language

Automated deep-research system for the Italian language, with a modular back-end architecture (based on LangGraph) and interactive front-end developed in Blazor. Inspired by [LangChain's Open Deep Research](https://github.com/langchain-ai/open_deep_research), but thoroughly revised to optimize research, generation, and revision of complex reports in Italian with source citations for greater transparency.

![Deep research system diagram](Ita_deep_research.png)

## Table of Contents

- [Description](#description)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Inspiration and Differences](#inspiration-and-differences)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)


## Description

This project offers an automated research platform for the Italian language, divided into a back-end and a user-friendly front-end. The system has been designed to experiment with the use of AI systems for creating documented, structured, and easily verifiable reports.

The back-end, developed with [LangGraph](https://github.com/langchain-ai/langgraph), handles planning, research, generation, and content revision. The front-end, built with [Blazor](https://dotnet.microsoft.com/apps/aspnet/web-apps/blazor), allows users to follow the process progress in real-time, provide feedback, and manage the entire workflow intuitively.

## Key Features

- **Intelligent Planning**: The planner conducts preliminary research to determine the most effective queries, optimizing research for report section planning.
- **Human-in-the-loop**: Complete support for human feedback, with the ability to approve the section plan or provide feedback for revision.
- **No API Key Research**: Uses search systems that don't require API keys, ensuring easy startup and reduced costs. Can be extended with paid services.
- **Specific Prompts**: Completely revised prompts for drafting and reviewing sections, with strategies to avoid overlaps between writers and improve report coherence.
- **Transparent Citations**: Content generation with numbered citations (obtained by consolidating sources acquired for each section), ensuring traceability and transparency of sources.
- **Final Review**: Dedicated phase for global report review to ensure coherence, completeness, and quality.
- **Scraping Cache**: Caching system to optimize content scraping and reduce response times.
- **PDF Support**: Reading and analysis of content in PDF format as well.
- **LLM Extensibility**: Ability to integrate proprietary or third-party language models (currently supporting OpenRouter).
- **Blazor Front-end**: Interface that shows the report's evolution in real-time and allows continuous user interaction.
- **Process Control**: Ability to interrupt the process directly from the front-end.


## Architecture

| Component | Technology | Description |
| :-- | :-- | :-- |
| Back-end | LangGraph (Python) | Workflow management, planning, scraping, text generation and revision. |
| Front-end | Blazor (.NET) | Reactive user interface, feedback, monitoring and process control. |
| LLM | OpenRouter | Content generation and revision through extensible LLMs. |
| Search & Cache | Custom | Scraping optimization and PDF management. |

## How It Works

1. **Input and Planning**: The user enters the research topic. The planner conducts preventive research to determine the most useful queries and develop a draft section plan.

2. **Human Review**: The plan is presented to the user, who can provide feedback to revise it or approve it.

3. **Research and Generation**: The system executes web searches in parallel for each section, aggregates and caches sources, and generates content using distinct prompts for the first draft and subsequent revisions.

4. **Citations and Sources**: Each section includes renumbered citations, with source consolidation for clarity and verifiability.

5. **Final Review**: The complete report undergoes automatic global revision and, if necessary, manual review.

6. **Live Visualization**: The front-end shows progress in real-time, allows feedback, and permits aborting the process at any time.


## Installation

> **Note:** Detailed instructions will be available soon.
> A Python configuration is required for the back-end and a .NET environment for the front-end.

1. Clone the repository:

```bash
git clone https://github.com/bullmount/DeepReport.git
```

## Usage

- Configure the API key for `openrouter`.
- Start the back-end (deep_research_server.py) and the front-end with vs2022.
- Access the Blazor interface to:
  - Enter the search query
  - Monitor the report generation in real-time
  - Provide feedback and revise content
  - Interrupt or modify the process when necessary
- View and download the final report with all organized citations.

**Prerequisites:**

- .NET 8+ (for Blazor front-end)
- Python 3.10+ (for LangGraph and back-end)
- Access to OpenRouter or your own LLM endpoint (optional)


## Inspiration and Differences

The project is inspired by [LangChain's open_deep_research](https://github.com/langchain-ai/open_deep_research), but introduces several innovations:

- Specific optimization for the Italian language
- Completely revised prompts
- Modified planning and revision workflow
- Interactive and modern front-end
- Advanced management of citations and sources
- Native support for PDFs and content caching


## Roadmap

- Integration of new search systems
- Specific version for the legal field
- Improvement of Blazor UI/UX
- Extension to on-premise LLMs


## Contributing

Contributions, suggestions, and reports are welcome!

## License

This project is distributed under the MIT license.
See the `LICENSE` file for details.

---

*Deep Research Italiano: automated, transparent, and collaborative research for the Italian language.*