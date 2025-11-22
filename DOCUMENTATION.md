## 📁 Project Structure

```
Gift Planning Agent/
├── main.py                          # CLI entry point (legacy)
├── server.py                        # FastAPI server for deployment
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container configuration
├── .dockerignore                    # Docker ignore rules
├── .gitignore                       # Git ignore rules
├── README.md                        # Main documentation
├── DOCUMENTATION.md                 # Additional docs
│
├── gift_planning_assistant/         # Main package (ADK agent)
│   ├── __init__.py
│   ├── agent.py                    # ADK root agent + FunctionTools
│   │
│   ├── agents/                     # Helper modules
│   │   ├── __init__.py
│   │   ├── orchestrator.py         # Legacy orchestrator (not used in ADK)
│   │   ├── recipient_manager.py    # Recipient management logic
│   │   ├── occasion_tracker.py     # Occasion tracking logic
│   │   ├── gift_finder.py          # Gift suggestion logic
│   │   ├── budget_manager.py       # Budget tracking logic
│   │   └── purchase_coordinator.py # Price comparison logic
│   │
│   ├── tools/                      # Custom tools
│   │   ├── __init__.py
│   │   ├── date_calculator.py      # Date utilities
│   │   └── budget_calculator.py    # Budget utilities
│   │
│   ├── memory/                     # Memory management
│   │   ├── __init__.py
│   │   └── memory_manager.py       # Memory Bank implementation
│   │
│   ├── config/                     # Configuration
│   │   ├── __init__.py
│   │   └── settings.py             # App settings
│   │
│   └── .env                        # Environment variables (not in git)
│
├── adk_app/                        # ADK CLI compatibility
│   ├── __init__.py
│   └── agent.py                    # Imports root_agent for ADK
│
└── webui/                          # React frontend
    ├── public/
    ├── src/
    │   ├── App.js                  # Main React component
    │   ├── App.css                 # Styles
    │   └── index.js                # Entry point
    ├── package.json
    └── build/                      # Production build (generated)
```

## 🔧 ADK Features Used

This project demonstrates the following ADK capabilities:

### 1. Multi-Agent System via Tool-Based Architecture
- **ADK Agent**: Root agent coordinates 5 specialized agent capabilities
- **FunctionTools**: 10 custom tools expose agent functionality to the LLM
- **Tool-Based Coordination**: Agents collaborate through shared tools and memory
- **Specialized Agents**: RecipientManager, OccasionTracker, GiftFinder, BudgetManager, PurchaseCoordinator

### 2. Tools Integration
- **Google Search Tool**: Real-time gift searches and price comparison
- **Code Execution Tool**: Precise budget calculations and analysis
- **Custom FunctionTools**: 10 tools for recipient, occasion, budget, gift, and purchase management
- **Custom Utilities**: Date calculator and budget analyzer

### 3. Memory & State Management
- **InMemorySessionService**: Conversation context across interactions (used in server.py)
- **Memory Bank Pattern**: Session-based storage of recipients, occasions, budgets
- **ToolContext State**: Shared state across all agent tool invocations
- **Session Persistence**: Data persists across conversation turns

### 4. Model Configuration
- **Gemini 2.0 Flash**: Using `gemini-2.0-flash`
- **Tool Grounding**: All responses grounded in explicit tool calls
- **Function Calling**: Structured tool interactions with type validation

## 🌟 Future Enhancements

Potential improvements for production deployment:

### Short-term
- [ ] **Persistent Storage**: Replace InMemorySessionService with Firebase or PostgreSQL
- [ ] **Enhanced Search**: Integrate actual Google Search API
- [ ] **Price Tracking**: Monitor price changes over time
- [ ] **Email Notifications**: Send reminders via email
- [ ] **Export/Import**: Backup and restore recipient data

### Medium-term
- [ ] **Collaborative Filtering**: Suggest gifts based on similar recipients
- [ ] **Gift Wrapping**: Find gift wrapping services
- [ ] **Card Generator**: AI-generated personalized messages
- [ ] **Calendar Integration**: Sync with Google Calendar
- [ ] **Mobile App**: React Native or Flutter interface

### Long-term  
- [ ] **Social Features**: Share gift lists with family/friends
- [ ] **Group Gifting**: Coordinate group purchases
- [ ] **Wishlist Integration**: Import from Amazon, Target, etc.
- [ ] **AR Preview**: Visualize gifts in recipient's space
- [ ] **Cloud Deployment**: Deploy to Cloud Run or Kubernetes

## 🐛 Troubleshooting

### Common Issues

**Error: `GEMINI_API_KEY not found`**
- Solution: Create `.env` file and add your API key

**Error: `ModuleNotFoundError`**
- Solution: Run `pip install -r requirements.txt`

**Search not working**
- Note: Google Search may require additional API credentials
- Fallback: System works without search, using LLM knowledge

**Memory not persisting**
- Expected: Uses InMemorySessionService (session-based only)
- For persistence: Implement custom session service

## 📝 License

This project is created for educational purposes as a demonstration of Google ADK capabilities.

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/genai-python-sdk)
- Powered by [Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/)
- Inspired by real-world gift planning challenges

---

**Happy Gift Planning! 🎁**

For questions or issues, please refer to the Google ADK documentation or create an issue in the repository.
