## 📁 Project Structure

```
Gift Planning Agent/
├── main.py                          # CLI entry point
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── README.md                         # Main documentation
├── gift_assistant.log                # Application logs
│
├── agents/                          # Agent modules
│   ├── __init__.py
│   ├── orchestrator.py              # Main orchestrator
│   ├── recipient_manager.py         # Recipient management
│   ├── occasion_tracker.py          # Occasion tracking
│   ├── gift_finder.py               # Gift suggestions
│   ├── budget_manager.py            # Budget tracking
│   └── purchase_coordinator.py      # Price comparison
│
├── tools/                           # Custom tools
│   ├── __init__.py
│   ├── date_calculator.py           # Date utilities
│   └── budget_calculator.py         # Budget utilities
│
├── memory/                          # Memory management
│   ├── __init__.py
│   └── memory_manager.py            # Memory Bank implementation
│
├── config/                          # Configuration
│   ├── __init__.py
│   └── settings.py                  # App settings
│
└── adk_app/                         # ADK integration
    └── __init__.py                  # Root agent export
```

## 🔧 ADK Features Used

This project demonstrates the following ADK capabilities:

### 1. Multi-Agent Orchestration
- **LlmAgent**: All 5 specialized agents use LLM-based reasoning
- **SequentialAgent**: Profile → Gift Search → Price Comparison workflow
- **ParallelAgent**: Gift Finder + Budget Manager run simultaneously

### 2. Tools Integration
- **Google Search Tool**: Real-time gift searches and price comparison
- **Code Execution Tool**: Precise budget calculations and analysis
- **Custom Tools**: Date calculator and budget analyzer

### 3. Memory & State Management
- **InMemorySessionService**: Conversation context across interactions
- **Memory Bank Pattern**: Persistent storage of recipients, occasions, budgets
- **Session State**: Shared state across all agents

### 4. Model Configuration
- **Gemini 2.0 Flash**: Using `gemini-2.0-flash`
- **Streaming Support**: Ready for streaming responses
- **Function Calling**: Structured tool interactions

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
