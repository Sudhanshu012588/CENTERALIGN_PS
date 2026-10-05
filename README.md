# CENTERALIGN_PS
# CentrAlign Worker

CentrAlign Worker is an autonomous AI worker designed to interpret natural-language tasks, break them into actionable steps, and execute those steps using available tools. The system is built around **LangGraph** and **LangChain**, allowing an LLM to act as a planner and executor rather than simply generating text. The current implementation focuses on filesystem automation inside a controlled Sandbox environment, where the worker can create, read, modify, search, organize, and open files and folders while preventing access outside the configured Sandbox.

## Capabilities

CentrAlign can currently perform the following filesystem operations:

- Create files with specified content
- Read existing files
- Update/overwrite file contents
- Create folders and nested directories
- List the contents of a folder
- Rename or move folders
- Recursively search for files across the Sandbox
- Open files using the operating system's default application
- Plan multi-step tasks using an LLM
- Execute planned tasks through LangGraph
- Restrict filesystem operations to a dedicated Sandbox directory
- Prevent path traversal and unauthorized access outside the Sandbox

For example, a user can provide a request such as:

```text
Create a folder named test, create test1.txt inside it,
and write "Hello" inside test1.txt.
```

The worker can convert this natural-language request into the required sequence of filesystem operations and execute them automatically.

Another example:

```text
Find resume_format.pdf in the sandbox and open it.
```

The worker can recursively search the Sandbox for the file and then open the discovered file using the appropriate path.

## Architecture

The current system follows an AI-worker architecture:

```text
                         ┌─────────────────┐
                         │      USER       │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     PLANNER     │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   TASK GRAPH    │
                         └────────┬────────┘
                                  │
                                  ▼
                   ┌──────────────────────────┐
                   │        EXECUTOR          │
                   │                          │
                   │  Reason → Tool → Observe │
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │       TOOL LAYER         │
                   │                          │
                   │ Filesystem │ Browser │   │
                   │ Terminal   │ APIs    │...│
                   └────────────┬─────────────┘
                                │
                                ▼
                   ┌──────────────────────────┐
                   │      ENVIRONMENT         │
                   │                          │
                   │       SANDBOX            │
                   └────────────┬─────────────┘
                                │
                                │ Observation
                                ▼
                   ┌──────────────────────────┐
                   │       VERIFIER           │
                   │                          │
                   │  Expected ≠ Actual ?     │
                   └────────────┬─────────────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                  SUCCESS                FAILURE
                     │                     │
                     ▼                     │
              ┌─────────────┐             │
              │    FINAL    │             │
              │   RESPONSE  │             │
              └─────────────┘             │
                                           │
                                           └──────► REPLAN
                                                      │
                                                      └──► EXECUTOR
```

The project uses **LangGraph** to orchestrate the workflow and an LLM to interpret user requests and determine the appropriate actions.

### Filesystem Sandbox

All filesystem operations are restricted to the configured Sandbox directory.

For example:

```text
Sandbox/
├── test/
│   └── test1.txt
├── NewFolder/
└── resume_format.pdf
```

The worker cannot access paths outside this directory through its filesystem tools.

## LLM Support

CentrAlign can use local or cloud-based LLMs through LangChain integrations.

### Ollama

Ollama is recommended for local development because it does not require an API key.

Example:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)
```

Other supported models can be installed through Ollama and selected in the configuration.

### Google Gemini

Gemini can be used through Google's LangChain integration:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
```

An appropriate Gemini API key must be configured in the environment.

## Requirements

Before running the project, make sure you have:

- Python 3.12+
- Git
- Ollama (if using a local LLM)
- A supported LLM/API key if using a cloud model

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd CentrAlign_PS
```

### 2. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the core dependencies:

```bash
pip install langchain langchain-core langgraph langchain-ollama python-dotenv rich
```

Install the Google integration if you want to use Gemini:

```bash
pip install langchain-google-genai
```

## Setting Up Ollama

If you want to run the worker completely locally, install Ollama from:

https://ollama.com/

Verify the installation:

```bash
ollama --version
```

Download the recommended model:

```bash
ollama pull qwen3:8b
```

Verify that the model is available:

```bash
ollama list
```

You can also test the model directly:

```bash
ollama run qwen3:8b
```

## Configuration

Configure the LLM used by the worker in the project configuration or `Main.py`.

For Ollama:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0
)
```

For Gemini, create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
```

Then load it using:

```python
from dotenv import load_dotenv

load_dotenv()
```

## Running the Worker

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Then run:

```bash
python3 Main.py
```

You should see the CentrAlign Worker interface:

```text
============================================================
CentrAlign Worker
============================================================

What Would You Like me To do >
```

Enter a natural-language task.

For example:

```text
Create a folder named test and create test1.txt inside it
with the content Hello
```

The worker will plan and execute the required operations.

## Sandbox Configuration

The filesystem worker requires a Sandbox directory.

Example:

```python
fs = FileSystemTools("./Sandbox")
```

This creates the Sandbox automatically if it does not exist.

All paths passed to filesystem tools are resolved relative to this directory.

For example:

```text
Sandbox/test/test1.txt
```

is accessed through:

```text
test/test1.txt
```

The worker prevents paths such as:

```text
../../important_file.txt
```

from escaping the Sandbox.

## Project Structure

A typical project structure is:

```text
CentrAlign_PS/
│
├── Main.py
├── requirements.txt
├── README.md
├── .env
│
├── Agent/
│   ├── planner.py
│   ├── executor.py
│   ├── state.py
│   └── FinalResponse.py
│
├── Tools/
│   ├── FileSystemTools.py
│   └── TerminalUI.py
│
└── Sandbox/
    └── ...
```

## Example Tasks

### Create a file

```text
Create hello.txt and write Hello World inside it.
```

### Create a directory structure

```text
Create a folder called project and inside it create
folders src and data.
```

### Search for a file

```text
Find resume_format.pdf in the sandbox.
```

The worker recursively searches through the Sandbox and its subdirectories.

### Find and open a file

```text
Find resume_format.pdf in the sandbox and open it.
```

The expected workflow is:

```text
find_file("resume_format.pdf")
        ↓
obtain matching path
        ↓
open_file(matching_path)
```

## Security

CentrAlign currently uses a Sandbox-based security model.

Every filesystem path is resolved and checked before execution:

```python
target = (self.SandBox / relative_path).resolve()

if not target.is_relative_to(self.SandBox):
    raise PermissionError(...)
```

This prevents the AI worker from using path traversal to access files outside the Sandbox.

The Sandbox should therefore be treated as the worker's working environment.

## Future Improvements

Planned improvements include:

- Browser automation
- Web search and web interaction
- Terminal/command execution with additional security controls
- More robust task verification
- Automatic error recovery
- Dynamic replanning after failed tasks
- Multiple LLM provider support
- Better tool selection
- Persistent task state
- Human approval for sensitive operations
- GUI/computer interaction
- Cross-application workflows

The long-term goal of CentrAlign is to evolve from a filesystem automation agent into a general-purpose AI worker capable of understanding a natural-language objective, interacting with multiple applications and tools, verifying its actions, and autonomously completing multi-step workflows.
