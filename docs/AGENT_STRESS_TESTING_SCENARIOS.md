# Agent Stress Testing Scenarios

**Real Estate Agentic System - Comprehensive Testing Protocol**

This document provides 20 comprehensive stress testing scenarios designed to thoroughly test the real estate agent system's capabilities, edge cases, and robustness. The system uses LangGraph-Swarm architecture with three specialized agents: SearchAgent (Alex), PropertyAgent (Emma), and SchedulingAgent (Mike).

## System Overview

**Architecture:** LangGraph-Swarm with PydanticAI integration
**Agents:**

- SearchAgent (Alex) - Property search specialist
- PropertyAgent (Emma) - Property analysis specialist
- SchedulingAgent (Mike) - Scheduling specialist

**Test Environment:** Mock mode with simulated property data
**Focus Areas:** Agent handoffs, natural language understanding, temporal intelligence, error handling

---

## Testing Protocol Instructions

1. **Start each scenario from a fresh chat session**
2. **Test in mock mode** to avoid API costs
3. **Document agent responses and handoffs**
4. **Note any failures or unexpected behaviors**
5. **Test the complete conversation flow**
6. **Verify system maintains context throughout**

---

## Scenario 1: Vague Initial Query → Clarification → Search → Analysis → Scheduling

**Testing:** Progressive refinement from vague to specific

**User Flow:**

```
User: "I need a place to live"
Expected: SearchAgent requests clarification

User: "Something nice in Miami"
Expected: SearchAgent asks for specifics (budget, bedrooms, etc.)

User: "2 bedrooms, budget around $2500"
Expected: SearchAgent performs search, hands off to PropertyAgent

User: "Tell me more about the first one"
Expected: PropertyAgent provides detailed analysis

User: "Can I visit it tomorrow afternoon?"
Expected: Handoff to SchedulingAgent, time parsing
```

**Stress Elements:**

- Extremely vague initial query
- Progressive clarification requests
- Multiple agent handoffs
- Temporal reference parsing

---

## Scenario 2: Hyper-Specific Query with Impossible Requirements

**Testing:** System handling of unrealistic demands

**User Flow:**

```
User: "I want a 5-bedroom penthouse with ocean view, gym, pool, concierge, parking for 3 cars, pet-friendly, furnished, in Miami Beach for under $1500/month"
Expected: SearchAgent handles impossible criteria gracefully

User: "Are you sure there's nothing available?"
Expected: Agent explains market reality, suggests alternatives

User: "What about if I increase to $3000?"
Expected: Modified search with realistic expectations

User: "Show me the best option then"
Expected: Handoff to PropertyAgent with top recommendation

User: "This is still too expensive, what about studios?"
Expected: Complete criteria change, new search
```

**Stress Elements:**

- Impossible budget requirements
- Complex multiple criteria
- Reality check handling
- Criteria modification mid-conversation

---

## Scenario 3: Rapid Context Switching

**Testing:** System's ability to handle topic jumps

**User Flow:**

```
User: "Show me apartments in Miami"
Expected: SearchAgent shows results

User: "Actually, what about houses in Orlando?"
Expected: New search with different criteria

User: "Wait, I meant apartments again, but in Tampa"
Expected: Another search pivot

User: "Let's go back to Miami apartments, the 2-bedroom one"
Expected: PropertyAgent recalls previous search context

User: "Can I schedule for this weekend?"
Expected: SchedulingAgent with weekend validation rules
```

**Stress Elements:**

- Multiple location changes
- Property type switching
- Context memory testing
- Invalid scheduling requests

---

## Scenario 4: Complex Temporal Intelligence Test

**Testing:** SchedulingAgent's natural language time parsing

**User Flow:**

```
User: "I want to visit an apartment"
Expected: PropertyAgent or SearchAgent guidance

User: "Show me something in South Beach"
Expected: SearchAgent provides options

User: "I like the second one, can I see it the day after tomorrow in the morning?"
Expected: SchedulingAgent parses relative date + time period

User: "Actually, how about next Friday around lunchtime?"
Expected: Different time parsing

User: "Or maybe this Thursday at 2:30 PM?"
Expected: Specific time handling

User: "What if I can only do weekends?"
Expected: Business hours validation conflict
```

**Stress Elements:**

- Relative date references
- Time period descriptions
- Specific time requests
- Business hours conflicts

---

## Scenario 5: Interruption and Recovery Flow

**Testing:** System resilience to conversation interruptions

**User Flow:**

```
User: "Find me a 3-bedroom house"
Expected: SearchAgent working

User: "Wait stop, I have a question about property taxes"
Expected: PropertyAgent handles general question

User: "Never mind, back to the house search"
Expected: System resumes previous search

User: "Actually I changed my mind, I want apartments now"
Expected: New search parameters

User: "Can you remind me what we were looking at before?"
Expected: Context history recall
```

**Stress Elements:**

- Conversation interruptions
- Context switching
- History recall
- State recovery

---

## Scenario 6: Error Handling and Edge Cases

**Testing:** System robustness under error conditions

**User Flow:**

```
User: "Find me properties for -$500"
Expected: SearchAgent handles negative price gracefully

User: "I want 0 bedrooms and 15 bathrooms"
Expected: Logical constraint validation

User: "Show me everything in Atlantis City"
Expected: Non-existent location handling

User: "Schedule a visit for February 30th"
Expected: Invalid date handling

User: "Book me at 25:00 PM"
Expected: Invalid time format handling
```

**Stress Elements:**

- Invalid input values
- Logical inconsistencies
- Non-existent locations
- Invalid dates/times

---

## Scenario 7: Multi-Property Comparison Analysis

**Testing:** PropertyAgent's comparative analysis capabilities

**User Flow:**

```
User: "Show me apartments under $3000 in Miami"
Expected: SearchAgent provides multiple options

User: "Compare the first three properties"
Expected: PropertyAgent detailed comparison

User: "Which has the best location?"
Expected: Location-based analysis

User: "What about value for money?"
Expected: Price/feature analysis

User: "I like the second one, what are the pros and cons?"
Expected: Balanced analysis with advantages/disadvantages

User: "Can I visit all three this week?"
Expected: SchedulingAgent multiple appointment handling
```

**Stress Elements:**

- Multiple property analysis
- Comparative evaluation
- Subjective criteria assessment
- Multiple scheduling requests

---

## Scenario 8: Budget Negotiation and Alternatives

**Testing:** Agent flexibility with budget constraints

**User Flow:**

```
User: "I need a place for $1500 but want luxury amenities"
Expected: SearchAgent addresses budget/amenity mismatch

User: "What's the cheapest luxury place?"
Expected: Alternative suggestions within budget reality

User: "Can I get a payment plan?"
Expected: Agent explains rental vs. purchase misconceptions

User: "What about shared apartments?"
Expected: Alternative housing suggestions

User: "Show me the best I can get for $1500"
Expected: Optimized search within budget
```

**Stress Elements:**

- Budget-amenity conflicts
- Alternative solution suggestions
- Financial misconceptions
- Optimization within constraints

---

## Scenario 9: Location-Specific Intelligence

**Testing:** System's geographical and neighborhood knowledge

**User Flow:**

```
User: "I work in downtown Miami, where should I live?"
Expected: Location-based recommendations

User: "What about commute times?"
Expected: Transportation and proximity analysis

User: "I have kids, which areas have good schools?"
Expected: Family-oriented neighborhood advice

User: "I'm worried about safety"
Expected: Safety and security information

User: "What's the nightlife like in these areas?"
Expected: Lifestyle and entertainment information

User: "Show me something in the safest area"
Expected: Search refinement based on safety criteria
```

**Stress Elements:**

- Commute considerations
- Family requirements
- Safety concerns
- Lifestyle preferences

---

## Scenario 10: Pet Owner Special Requirements

**Testing:** Specific accommodation needs handling

**User Flow:**

```
User: "I have two large dogs, find me pet-friendly places"
Expected: SearchAgent filters for pet policies

User: "Do they allow big dogs or just small pets?"
Expected: Detailed pet policy clarification

User: "What about pet deposits and fees?"
Expected: Financial implications of pets

User: "Are there dog parks nearby?"
Expected: Neighborhood amenities for pets

User: "I also have a cat, is that a problem?"
Expected: Multiple pet considerations

User: "Can I visit with my dogs?"
Expected: SchedulingAgent pet visitation policies
```

**Stress Elements:**

- Specific pet requirements
- Policy details
- Additional fees
- Lifestyle considerations for pets

---

## Scenario 11: Furnished vs. Unfurnished Confusion

**Testing:** Property specification understanding

**User Flow:**

```
User: "Find me a furnished apartment"
Expected: SearchAgent filters for furnished properties

User: "What does furnished include?"
Expected: PropertyAgent explains furniture inclusions

User: "I have my own furniture, what about unfurnished?"
Expected: Price and option comparisons

User: "Can furnished places remove their furniture?"
Expected: Flexibility and customization options

User: "What's the price difference?"
Expected: Cost comparison analysis

User: "Show me both options side by side"
Expected: Comparative analysis of furnished vs. unfurnished
```

**Stress Elements:**

- Specification clarifications
- Flexibility options
- Price comparisons
- Customization possibilities

---

## Scenario 12: Investment vs. Personal Use

**Testing:** Different usage purpose handling

**User Flow:**

```
User: "I'm looking for an investment property in Miami"
Expected: Different analysis criteria for investment

User: "What's the rental yield in this area?"
Expected: Investment-focused metrics

User: "Actually, I might live in it myself"
Expected: Personal use considerations

User: "Can I do both - live in it and rent out rooms?"
Expected: Mixed-use scenarios

User: "What are the legal requirements for renting?"
Expected: Regulatory and legal information

User: "Show me properties good for both scenarios"
Expected: Dual-purpose optimization
```

**Stress Elements:**

- Investment analysis
- Personal use criteria
- Mixed-use scenarios
- Legal considerations

---

## Scenario 13: Group Decision Making

**Testing:** Multiple stakeholder scenarios

**User Flow:**

```
User: "My partner and I are looking for a place"
Expected: Joint decision considerations

User: "She likes modern, I prefer classic style"
Expected: Compromise and preference balancing

User: "We have different budget ideas"
Expected: Budget negotiation guidance

User: "Can we schedule separate viewings?"
Expected: Multiple scheduling accommodations

User: "What questions should we ask during viewing?"
Expected: Viewing preparation advice

User: "How do we decide between our favorites?"
Expected: Decision-making framework
```

**Stress Elements:**

- Multiple preferences
- Compromise scenarios
- Joint decision making
- Scheduling complexity

---

## Scenario 14: Lease Terms and Legal Questions

**Testing:** Complex rental agreement discussions

**User Flow:**

```
User: "What are typical lease terms in Miami?"
Expected: Legal and contractual information

User: "Can I negotiate the lease length?"
Expected: Negotiation possibilities

User: "What about early termination?"
Expected: Exit clause discussions

User: "Do I need renters insurance?"
Expected: Insurance requirements

User: "What happens if I break something?"
Expected: Damage and liability policies

User: "Can you review my lease agreement?"
Expected: Appropriate boundaries on legal advice
```

**Stress Elements:**

- Legal information requests
- Contract negotiations
- Insurance requirements
- Liability concerns

---

## Scenario 15: Urgent Housing Needs

**Testing:** Time-sensitive scenarios

**User Flow:**

```
User: "I need to move in within 2 weeks"
Expected: Urgent timeline accommodation

User: "What's available immediately?"
Expected: Quick availability filtering

User: "Can we expedite the application process?"
Expected: Process acceleration advice

User: "I can view properties tomorrow morning"
Expected: Rapid scheduling

User: "What documents do I need ready?"
Expected: Application preparation guidance

User: "Can I put down a deposit today?"
Expected: Immediate action possibilities
```

**Stress Elements:**

- Urgent timelines
- Rapid decision making
- Process acceleration
- Immediate actions

---

## Scenario 16: International/Out-of-State Buyer

**Testing:** Remote buyer scenarios

**User Flow:**

```
User: "I'm moving to Miami from New York, never been there"
Expected: Relocation guidance

User: "Can you do virtual tours?"
Expected: Remote viewing options

User: "What areas are similar to Manhattan?"
Expected: City comparison insights

User: "How's the job market there?"
Expected: Economic and employment information

User: "Can I sign lease remotely?"
Expected: Remote transaction processes

User: "What about moving services?"
Expected: Additional service recommendations
```

**Stress Elements:**

- Remote buyer needs
- City comparisons
- Virtual services
- Relocation support

---

## Scenario 17: Student Housing Specific

**Testing:** Demographic-specific requirements

**User Flow:**

```
User: "I'm a student looking for affordable housing"
Expected: Student-focused search criteria

User: "Are there student discounts?"
Expected: Educational pricing information

User: "I need somewhere close to University of Miami"
Expected: University-proximity focus

User: "What about roommate matching?"
Expected: Shared housing options

User: "Do I need a guarantor?"
Expected: Student-specific rental requirements

User: "When do leases typically start for students?"
Expected: Academic calendar considerations
```

**Stress Elements:**

- Student-specific needs
- Educational proximity
- Shared housing
- Academic timing

---

## Scenario 18: Luxury Housing Requirements

**Testing:** High-end market handling

**User Flow:**

```
User: "Show me luxury penthouses in Miami Beach"
Expected: High-end property filtering

User: "I need concierge services and valet parking"
Expected: Luxury amenity requirements

User: "What's the most expensive option?"
Expected: Premium market offerings

User: "Do these buildings have waiting lists?"
Expected: Exclusive property availability

User: "Can I get a private viewing with champagne service?"
Expected: VIP treatment requests

User: "What about helicopter landing access?"
Expected: Ultra-luxury amenity queries
```

**Stress Elements:**

- Luxury market expectations
- VIP service requests
- Exclusive amenities
- Premium pricing

---

## Scenario 19: Accessibility and Special Needs

**Testing:** Accommodation requirements

**User Flow:**

```
User: "I need wheelchair accessible apartments"
Expected: ADA compliance filtering

User: "What about bathroom modifications?"
Expected: Specific accessibility features

User: "Are there elevators in all buildings?"
Expected: Building accessibility verification

User: "I need first floor units only"
Expected: Floor preference accommodation

User: "What about service animal policies?"
Expected: Medical accommodation policies

User: "Can I visit with my mobility equipment?"
Expected: Accessible viewing arrangements
```

**Stress Elements:**

- ADA compliance requirements
- Medical accommodations
- Specific accessibility needs
- Equipment considerations

---

## Scenario 20: Complete End-to-End Success Flow

**Testing:** Full system integration from start to finish

**User Flow:**

```
User: "Hi, I'm new to Miami and looking for an apartment"
Expected: Warm welcome and needs assessment

User: "2 bedrooms, pet-friendly, under $3000, close to the beach"
Expected: SearchAgent finds relevant properties

User: "Tell me about the one in South Beach"
Expected: PropertyAgent provides detailed analysis

User: "What's the neighborhood like for young professionals?"
Expected: Lifestyle and demographic information

User: "This sounds perfect, can I visit it?"
Expected: Handoff to SchedulingAgent

User: "How about this Saturday at 2 PM?"
Expected: Weekend scheduling validation

User: "Okay, Friday at 3 PM then"
Expected: Appointment confirmation

User: "What should I bring to the viewing?"
Expected: Viewing preparation guidance

User: "Can you send me the property details?"
Expected: Information compilation and summary

User: "Thank you, you've been very helpful!"
Expected: Professional closure and follow-up offers
```

**Stress Elements:**

- Complete workflow integration
- Multiple agent handoffs
- Context preservation
- Professional service delivery

---

## Evaluation Criteria

For each scenario, evaluate:

### ✅ Successful Behaviors:

- **Agent Recognition**: Correct agent handles each query type
- **Context Preservation**: Information maintained across handoffs
- **Natural Language**: Understands conversational requests
- **Error Recovery**: Handles mistakes gracefully
- **Personalization**: Adapts to user preferences
- **Professional Tone**: Maintains helpful, expert demeanor

### ❌ Failure Indicators:

- **Wrong Agent**: Inappropriate agent handles request
- **Context Loss**: Previous information forgotten
- **Parsing Errors**: Misunderstands clear requests
- **Infinite Loops**: Repetitive responses
- **Inappropriate Responses**: Off-topic or incorrect information
- **System Crashes**: Technical failures

### 📊 Performance Metrics:

- **Response Time**: Speed of agent responses
- **Handoff Accuracy**: Correct agent transitions
- **Information Quality**: Relevant and accurate details
- **User Satisfaction**: Helpful and complete responses
- **Error Handling**: Graceful failure management

---

## Testing Notes

**System Configuration:**

- Use **Mock Mode** to avoid API costs
- Test with fresh chat sessions for each scenario
- Document any unexpected behaviors
- Note performance issues or delays

**Expected Agent Personalities:**

- **Alex (Search)**: Methodical, detail-oriented, clarification-focused
- **Emma (Property)**: Analytical, informative, comparison-skilled
- **Mike (Scheduling)**: Precise, time-aware, logistically-minded

**Critical Test Areas:**

1. **Handoff Intelligence**: Agents know when to transfer
2. **Context Memory**: Information preserved across agents
3. **Natural Language**: Understands conversational English
4. **Error Resilience**: Handles invalid inputs gracefully
5. **Domain Expertise**: Provides accurate real estate guidance

---

**Happy Testing! 🏠🤖**
