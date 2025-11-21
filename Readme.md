# 🎁 Gift Planning Assistant

A comprehensive multi-agent AI system built with Google's Agent Development Kit (ADK) and Gemini 2.0 Flash to help you manage all aspects of gift-giving.

## 📋 Table of Contents

- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Architecture](#architecture)
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [ADK Features Used](#adk-features-used)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)

## 🎯 Problem Statement

Gift-giving can be challenging due to:
- **Forgetting important occasions** (birthdays, anniversaries, holidays)
- **Lack of personalization** - generic gifts that don't match recipient interests
- **Budget management** - overspending or poor allocation across recipients
- **Time-consuming research** - finding the perfect gift takes hours
- **No gift history tracking** - accidentally giving duplicate gifts

## 💡 Solution

The Gift Planning Assistant is an intelligent multi-agent system that:
- **Remembers** all your recipients and their preferences
- **Tracks** important occasions with smart reminders
- **Suggests** personalized gifts based on interests, age, and past gifts
- **Manages** your budget and spending across all recipients
- **Finds** the best prices and purchase options automatically

## 🏗️ Architecture

The system uses a **multi-agent orchestration pattern** with specialized agents:

```mermaid
graph TD
    A[User] --> B[Gift Planning Assistant<br/>Root Orchestrator]
    B --> C[Recipient Manager]
    B --> D[Occasion Tracker]
    B --> E[Gift Finder]
    B --> F[Budget Manager]
    B --> G[Purchase Coordinator]
    
    C --> H[Memory Bank]
    D --> H
    E --> H
    F --> H
    
    D --> I[Date Calculator Tool]
    F --> J[Budget Calculator Tool]
    E --> K[Google Search]
    F --> L[Code Execution]
    G --> K
    
    style B fill:#4285f4,color:#fff
    style H fill:#34a853,color:#fff
    style K fill:#fbbc04,color:#000
    style L fill:#ea4335,color:#fff
```

### Agent Responsibilities

1. **RecipientManagerAgent** 
   - Manages recipient profiles (name, age, interests, relationship)
   - Stores gift history to avoid duplicates
   - Tracks preferences and style

2. **OccasionTrackerAgent**
   - Tracks birthdays, anniversaries, holidays, custom events
   - Calculates days until occasions
   - Manages reminder schedules

3. **GiftFinderAgent** 
   - Analyzes recipient profiles for personalization
   - Uses Google Search to find current gift ideas
   - Filters by budget and past gifts
   - Ranks suggestions by relevance

4. **BudgetManagerAgent**
   - Sets and tracks overall gift budget
   - Monitors spending per recipient
   - Calculates remaining budget
   - Alerts on budget limits
   - Uses Code Execution for precise calculations

5. **PurchaseCoordinatorAgent**
   - Searches for product availability
   - Compares prices across retailers
   - Provides purchase links
   - Finds best deals

## ✨ Features

### Core Capabilities

- ✅ **Multi-Agent System** - Parallel and sequential agent execution
- ✅ **Google Search Integration** - Real-time gift and price searches
- ✅ **Code Execution** - Precise budget calculations
- ✅ **Custom Tools** - Date calculator, budget analyzer
- ✅ **Memory Bank** - Persistent storage of recipients, occasions, budgets
- ✅ **Session Management** - InMemorySessionService for conversation context
- ✅ **Gemini 2.0 Flash** - Latest Gemini model for advanced reasoning

### User Features

- 📝 Add and manage recipient profiles
- 📅 Track occasions with automatic reminders
- 🎁 Get personalized gift suggestions
- 💰 Set budgets and track spending
- 🛒 Find best prices across retailers
- 💬 Chat interface for natural interaction
- 📊 View statistics and summaries

## 🛠️ Technical Stack

- **Framework**: Google Agent Development Kit (ADK) for Python
- **Model**: `gemini-2.0-flash` (Gemini 2.0 Flash)
- **Language**: Python 3.10+
- **Tools**: Google Search, Code Execution, Custom Tools
- **Memory**: InMemorySessionService + Memory Bank pattern
- **Dependencies**: 
  - `google-genai` - Gemini API client
  - `google-generativeai` - Generative AI library
  - `python-dotenv` - Environment management
  - `pydantic` - Data validation

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Gemini API key (get one at [Google AI Studio](https://makersuite.google.com/app/apikey))
- Git (optional)

### Installation

1. **Clone or download the project**
   ```bash
   cd "Gift Planning Agent"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Verify installation**
   ```bash
   python -c "import google.genai; print('✓ Installation successful')"
   ```

## 📖 Usage

### Option 1: CLI Interface

Run the interactive command-line interface:

```bash
python main.py
```

This launches a menu-driven interface with options:
1. Add Recipient
2. Add Occasion
3. Get Gift Suggestions
4. View Budget Summary
5. View Upcoming Occasions
6. Chat with Assistant
7. View Statistics
8. Exit

### Option 2: ADK Web Interface

Run the web interface (if ADK CLI is installed):

```bash
adk web
```

Then open your browser to interact with the assistant via a web UI.

### Option 3: ADK Run (Programmatic)

Run the agent programmatically:

```bash
adk run
```

## 💬 Example Conversation

```
User: Add a new recipient named Sarah, she's 28, loves yoga and sustainable living
