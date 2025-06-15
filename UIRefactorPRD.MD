# Customs Broker Portal - UX Refactor PRD

## Executive Summary

Refactor the existing customs broker portal from a 5-page structure to a streamlined 3-page UX focused on distinct user workflows: **Professional Dashboard**, **Interactive Tariff Explorer**, and **AI Assistant**. This reorganization maintains all existing backend functionality while dramatically improving user experience and reducing navigation complexity.

## Current vs. Proposed Structure

### Current Structure (5 pages)
- `/` - Home/Landing page
- `/dashboard` - Mixed workspace 
- `/duty-calculator` - Standalone calculator
- `/search` - AI search interface
- `/tariff-lookup` - Tariff browser

### Proposed Structure (4 pages)
1. **`/dashboard`** - Professional News & Intelligence Center
2. **`/tariff-tree`** - Complete Interactive Schedule 3 Explorer  
3. **`/ai-assistant`** - Unified AI-Powered Consultation Hub
4. **`/export-tariffs`** - Export Classification & Requirements Center

---

## Page 4: Export Tariff Details (`/export-tariffs`)

### Purpose
Comprehensive export classification and requirements center for Australian exporters, covering AHECC codes, export documentation, and international market access requirements.

### Key Features

#### 📤 Export Classification Browser
**AHECC Code Explorer (Left Panel - 40% width)**
- Interactive AHECC (Australian Harmonized Export Commodity Classification) tree
- Hierarchical browsing from commodity groups to specific statistical codes
- Cross-reference mapping to corresponding import HS codes
- Statistical unit requirements (kg, litres, number of items, etc.)
- Recently classified exports history

**Export Code Structure:**
```
📁 Section 01 - Live Animals and Animal Products
  📁 Chapter 01 - Live Animals  
    📁 0101 - Live Horses, Asses, Mules and Hinnies
      📄 01011000 - Pure-bred breeding animals
        ├── Statistical Unit: Number of head
        ├── Corresponding Import Code: 0101.10.00
        ├── Export License: Required for breeding stock
        └── Quarantine: AQIS health certificate mandatory
```

#### 📋 Export Requirements Dashboard (Right Panel - 60% width)
**When AHECC code selected, display:**

**Classification Details**
- Full commodity description and scope
- Statistical reporting requirements
- Unit of quantity and measurement
- Related import classification for reference

**Export Documentation**
- Required export permits and licenses
- Department of Agriculture export certificates
- AQIS quarantine requirements
- Industry-specific certifications (organic, halal, etc.)

**Market Access Requirements**
- Country-specific import requirements for major destinations
- Phytosanitary certificates for agricultural products
- Health certificates for food and animal products
- Technical standards and conformity assessments

**Trade Agreement Benefits**
- Preferential treatment under Australian FTAs
- Certificate of origin requirements
- Rules of origin criteria for preferential treatment
- Quota allocations and utilization tracking

#### 🌏 Destination Market Intelligence
**Country-Specific Requirements Panel**
- Searchable database of import requirements by destination country
- Integration with DFAT market intelligence
- Tariff rates applied by importing countries to Australian goods
- Non-tariff barriers and technical requirements
- Recent changes to import policies affecting Australian exports

**Market Access Tools**
- FTA utilization calculator (potential savings from preferential treatment)
- Export permit application links and guidance
- Quarantine treatment requirements by commodity and destination
- Prohibited and restricted goods lists by country

#### 📊 Export Statistics & Analytics
**Trade Performance Dashboard**
- Export volumes and values by AHECC code
- Top destination markets for specific commodities
- Seasonal export patterns and trends
- Price benchmarking against international markets
- Market share analysis for Australian exports

### Database Integration
**Uses existing tables:**
- `export_codes` - AHECC classification system
- `tariff_codes` - Cross-reference to import classifications
- `fta_rates` - Export benefits from trade agreements
- `news_items` - Export-related regulatory updates
- `legislation_documents` - Export control regulations

**Additional data sources:**
- Department of Agriculture export permit database
- AQIS quarantine requirements
- DFAT market access information
- ABS export statistics

**New API Endpoints Needed:**
```typescript
GET /api/export/ahecc-tree // Complete AHECC hierarchical structure
GET /api/export/code/{ahecc_code}/details // Comprehensive export information
GET /api/export/requirements/{ahecc_code}/{country} // Country-specific requirements
GET /api/export/permits/{commodity_group} // Required permits and licenses
GET /api/export/quarantine/{ahecc_code} // AQIS requirements
GET /api/export/statistics/{ahecc_code} // Trade performance data
GET /api/export/market-access/{country} // Destination market requirements
```

#### 🔍 Export Classification Tools
**AI-Powered Export Classification**
- Product description to AHECC code matching
- Comparison with similar exported products
- Statistical unit determination assistance
- Export permit requirement identification

**Documentation Assistant**
- Generate export documentation checklists
- Pre-fill certificate of origin applications
- Quarantine treatment scheduling assistance
- Export permit application guidance

**Compliance Monitoring**
- Track changes to export requirements
- Monitor quota utilization for managed commodities
- Alert system for new market access opportunities
- Regulatory update notifications for specific AHECC codes

---

## Page 1: Professional Dashboard (`/dashboard`)

### Purpose
Central intelligence hub for customs brokers to stay current with regulatory changes, trade developments, and market intelligence.

### Key Features

#### 📰 News Intelligence Center
**Primary Feed (60% of screen real estate)**
- Scrollable timeline of latest news items with infinite scroll
- Real-time updates from existing news aggregation system
- Click-to-expand article view with full content
- AI-generated impact summaries for each item
- Filter by: All, Critical, Regulatory Changes, TCO Updates, Dumping Cases, FTA News

**News Item Card Structure:**
```
[Source Badge] [Category Tag] [Impact Score ●●●○○]
Headline (clickable)
AI Summary (2-3 sentences)
Related HS Codes: [1234.56.78] [9876.54.32] (clickable)
[Read Full Article] [Save] [Share]
───
```

#### 📊 Trade Intelligence Sidebar (40% of screen)
**Real-Time Statistics Dashboard**
- Weekly TCO publications count
- New anti-dumping investigations
- Recent FTA rate changes
- Legislative amendments pending
- System health indicators

**Recent Rulings Section**
- Latest binding tariff rulings
- Anti-dumping determination updates
- Court decisions affecting trade
- AQIS policy updates

**Quick Actions Panel**
- "Classify New Product" → AI Assistant
- "Browse Tariff Tree" → Tariff Tree page
- "Check TCO Status"
- "Calculate Duties"

### Database Integration
**Uses existing tables:**
- `news_items` - All news content
- `regulatory_changes` - Legislative updates
- `tcos` - TCO status and updates
- `dumping_duties` - Anti-dumping measures
- `legislation_documents` - Regulatory documents

**New API Endpoints Needed:**
```typescript
// Enhance existing news API
GET /api/news/dashboard-feed?limit=50&category=all&since=timestamp
GET /api/news/statistics/weekly-summary
GET /api/rulings/recent?limit=10
GET /api/system/health-status
```

---

## Page 2: Interactive Tariff Tree Explorer (`/tariff-tree`)

### Purpose
Complete Schedule 3 Australian Harmonized Tariff browsing experience - the definitive reference tool for tariff classification.

### Key Features

#### 🌳 Full Hierarchical Tree Interface
**Left Panel: Expandable Tree (40% width)**
```
📁 Section I - Live Animals; Animal Products
  📁 Chapter 01 - Live Animals
    📁 0101 - Live Horses, Asses, Mules and Hinnies
      📄 010110 - Pure-bred breeding animals
      📄 010190 - Other
    📁 0102 - Live Bovine Animals
      📄 010210 - Pure-bred breeding animals
      📄 010221 - Buffalo
      📄 010229 - Other cattle
```

**Right Panel: Detailed Information (60% width)**
When HS code selected, display:
- **Code Information**: Full description, unit of quantity, statistical code
- **Duty Rates**: General rate, all applicable FTA preferential rates  
- **Additional Measures**: Anti-dumping duties, safeguards, TCO exemptions
- **Regulatory Notes**: Chapter notes, classification guidance
- **Related Information**: Export requirements, AQIS considerations
- **Recent Changes**: Updates to this code in last 90 days

#### 🔍 Advanced Tree Navigation
- **Search-in-Tree**: Real-time filtering as you type
- **Keyword Highlighting**: Highlight matching terms in descriptions
- **Path Breadcrumbs**: Show current location (Section → Chapter → Heading → Subheading)
- **Quick Jump**: Direct HS code entry field
- **Bookmark System**: Save frequently used codes
- **Recently Viewed**: History of accessed codes

#### 📋 Professional Tools
- **Compare Codes**: Side-by-side comparison of multiple HS codes
- **Export Options**: PDF export of selected sections
- **Print-Friendly**: Optimized layouts for physical reference
- **Code Sharing**: Generate shareable links to specific codes

### Database Integration
**Uses existing tables:**
- `tariff_codes` - Complete Schedule 3 hierarchy
- `duty_rates` - General and preferential rates
- `fta_rates` - All FTA preferential rates
- `dumping_duties` - Anti-dumping measures
- `tcos` - Tariff concession orders
- `tariff_sections` & `tariff_chapters` - Hierarchical structure

**API Endpoints (mostly existing):**
```typescript
GET /api/tariff/tree/{section_id} // Enhanced with full tree data
GET /api/tariff/code/{hs_code}/details // Comprehensive code information
GET /api/tariff/search?q={query}&tree=true // Tree-filtered search
GET /api/tariff/compare?codes={code1,code2,code3} // New comparison endpoint
```

---

## Page 3: AI Assistant (`/ai-assistant`)

### Purpose
Unified consultation hub for non-customs broker team members, combining conversational AI with professional tools like duty calculation.

### Key Features

#### 🤖 Conversational AI Interface
**Main Chat Interface (70% of screen)**
- ChatGPT-style conversation interface
- Context-aware responses using RAG from all database tables
- Multi-turn conversations with memory
- Suggested follow-up questions
- Ability to ask about:
  - Product classification guidance
  - Regulatory requirements
  - AQIS import conditions
  - FTA eligibility
  - Duty calculations
  - Legislative interpretations

**Example Conversation Flow:**
```
User: "What are the import requirements for industrial plastic pipes from Germany?"

AI: Based on your query, industrial plastic pipes would likely classify under 
HS Chapter 39 (Plastics). Let me provide comprehensive guidance:

🏷️ CLASSIFICATION
Most industrial plastic pipes fall under:
- 3917.40.00 - Fittings (flanges, elbows, etc.)
- 3917.32.00 - Flexible tubes, pipes and hoses

📊 DUTY RATES
From Germany (EU-Australia FTA eligible):
- General rate: 5.0%
- FTA preferential rate: Free (0%)
- Potential savings: 5% of customs value

🛃 REGULATORY REQUIREMENTS
- AQIS: No specific import permits required for plastic pipes
- Standards: Must comply with AS/NZS standards if for potable water
- Documentation: Commercial invoice, packing list, certificate of origin

Would you like me to:
1. Calculate exact duties for a specific shipment?
2. Check if any TCO exemptions apply?
3. Provide detailed FTA certificate requirements?

[Calculate Duties] [Check TCOs] [FTA Requirements]
```

#### 🧮 Enhanced Duty Calculator
**Comprehensive Tax Calculator Panel (30% of screen, collapsible)**
- **Customs Duties**: General and preferential rates from FTAs
- **GST**: 10% on dutiable value (customs value + duties)
- **Luxury Car Tax (LCT)**: 33% on luxury vehicles over threshold ($71,849 for 2024-25)
- **Wine Equalisation Tax (WET)**: 29% on wine imports
- **Tobacco Excise**: Complex calculations for tobacco products
- **Fuel Excise**: For petroleum and fuel imports
- **Other Levies**: ACMA charges, container deposits, etc.

**Enhanced Calculator Features:**
- **Multi-Tax Calculation**: All applicable taxes calculated simultaneously
- **Threshold Detection**: Automatic luxury car tax threshold checking
- **Vehicle Classification**: Special handling for motor vehicles and luxury cars
- **Alcohol/Tobacco**: Specialized calculations for excisable goods
- **Real-time Updates**: Live calculation as user types
- **Tax Breakdown**: Detailed line-by-line cost breakdown
- **Export Options**: Enhanced PDF/CSV with all tax components
- **Compliance Notes**: Automatic alerts for special requirements

**Example Enhanced Calculation Display:**
```
Customs Value: $80,000 AUD
Country: Germany (FTA Eligible)

CUSTOMS DUTY
├── General Rate: 5.0% = $4,000
├── FTA Rate: 0.0% = $0 ✓ (EU-Australia FTA)
└── Applied: $0

LUXURY CAR TAX
├── LCT Threshold: $71,849
├── Excess Amount: $8,151
├── LCT Rate: 33%
└── LCT Amount: $2,690

GST
├── Dutiable Value: $80,000 + $0 = $80,000
├── GST Rate: 10%
└── GST Amount: $8,000

TOTAL LANDED COST
├── Customs Value: $80,000
├── Customs Duty: $0
├── Luxury Car Tax: $2,690
├── GST: $8,000
└── TOTAL: $90,690

💡 LCT OPTIMIZATION TIP: Consider importing vehicle components separately to potentially reduce LCT exposure.
```

#### 🎯 Smart Context Features
- **Document Upload**: Upload commercial invoices for automatic analysis
- **Product Image Recognition**: Upload product photos for classification assistance
- **Conversation Export**: Export entire consultation sessions
- **Follow-up Reminders**: Set alerts for regulatory changes affecting discussed topics

### Database Integration
**Uses ALL existing tables for RAG context:**
- `tariff_codes` - Classification guidance
- `legislation_documents` & `legislation_sections` - Regulatory text
- `news_items` - Current developments
- `fta_rates` - Trade agreement benefits
- `tcos` - Exemption opportunities
- `dumping_duties` - Anti-dumping considerations

**Enhanced AI Endpoints:**
```typescript
POST /api/ai/chat // Enhanced with full database RAG
POST /api/ai/classify-image // New image classification
POST /api/ai/analyze-document // New document analysis
GET /api/ai/conversation/{session_id} // Conversation persistence
POST /api/duty/calculate-from-context // Enhanced calculator integration
```

---

## Technical Implementation Plan

### Phase 1: Backend Enhancements (Week 1-2)

#### Enhanced Tax Calculation System
```python
# Enhanced duty calculator with all Australian import taxes
@app.post("/api/duty/calculate-comprehensive")
async def calculate_comprehensive_duties(
    hs_code: str,
    country_of_origin: str,
    customs_value: float,
    currency: str = "AUD",
    vehicle_details: Optional[dict] = None,  # For LCT calculations
    alcohol_details: Optional[dict] = None,  # For WET calculations
    tobacco_details: Optional[dict] = None   # For tobacco excise
):
    """
    Comprehensive duty calculation including:
    - Customs duties (general and preferential)
    - GST (10%)
    - Luxury Car Tax (33% over threshold)
    - Wine Equalisation Tax (29%)
    - Tobacco Excise (complex rates)
    - Fuel Excise
    - Other applicable levies
    """
    
    result = {
        'customs_duty': calculate_customs_duty(hs_code, country_of_origin, customs_value),
        'gst': calculate_gst(customs_value, customs_duty),
        'luxury_car_tax': calculate_lct(hs_code, customs_value, vehicle_details),
        'wine_equalisation_tax': calculate_wet(hs_code, customs_value, alcohol_details),
        'tobacco_excise': calculate_tobacco_excise(hs_code, tobacco_details),
        'fuel_excise': calculate_fuel_excise(hs_code, customs_value),
        'other_levies': calculate_other_levies(hs_code, customs_value),
        'total_landed_cost': 0,  # Sum of all above
        'optimization_tips': generate_tax_optimization_tips(hs_code, customs_value)
    }
    
    result['total_landed_cost'] = sum([
        result['customs_duty'], result['gst'], result['luxury_car_tax'],
        result['wine_equalisation_tax'], result['tobacco_excise'], 
        result['fuel_excise'], result['other_levies']
    ])
    
    return result

def calculate_lct(hs_code: str, customs_value: float, vehicle_details: dict = None):
    """Calculate Luxury Car Tax for vehicles over threshold"""
    LCT_THRESHOLD_2024_25 = 71849  # Updated annually
    LCT_RATE = 0.33
    
    # Check if product is a motor vehicle subject to LCT
    vehicle_hs_codes = ['8703', '8704', '8705']  # Passenger cars, commercial vehicles
    
    if not any(hs_code.startswith(code) for code in vehicle_hs_codes):
        return {'applicable': False, 'amount': 0, 'details': 'Not a motor vehicle'}
    
    if customs_value <= LCT_THRESHOLD_2024_25:
        return {
            'applicable': True, 
            'amount': 0, 
            'details': f'Under LCT threshold of ${LCT_THRESHOLD_2024_25:,}'
        }
    
    excess_amount = customs_value - LCT_THRESHOLD_2024_25
    lct_amount = excess_amount * LCT_RATE
    
    return {
        'applicable': True,
        'amount': lct_amount,
        'threshold': LCT_THRESHOLD_2024_25,
        'excess_amount': excess_amount,
        'rate': LCT_RATE,
        'details': f'LCT of ${lct_amount:,.2f} on excess amount of ${excess_amount:,}'
    }

def calculate_wet(hs_code: str, customs_value: float, alcohol_details: dict = None):
    """Calculate Wine Equalisation Tax"""
    WET_RATE = 0.29
    
    # Wine HS codes (Chapter 22)
    wine_hs_codes = ['2204', '2205', '2206']
    
    if not any(hs_code.startswith(code) for code in wine_hs_codes):
        return {'applicable': False, 'amount': 0}
    
    wet_amount = customs_value * WET_RATE
    
    return {
        'applicable': True,
        'amount': wet_amount,
        'rate': WET_RATE,
        'details': f'WET of ${wet_amount:,.2f} at {WET_RATE*100}%'
    }
```

#### New Export-Related Endpoints
```python
@app.get("/api/export/ahecc-tree")
async def get_ahecc_tree():
    """Complete AHECC hierarchical structure for export classification"""
    pass

@app.get("/api/export/code/{ahecc_code}/requirements/{country}")
async def get_export_requirements(ahecc_code: str, country: str):
    """Country-specific export requirements and market access"""
    pass

@app.get("/api/export/permits/{commodity_group}")
async def get_required_permits(commodity_group: str):
    """Required export permits and licenses"""
    pass
```

#### Enhanced Database Queries
```sql
-- Optimized tree loading query
WITH RECURSIVE tariff_tree AS (
    SELECT id, hs_code, description, parent_code, level, 0 as depth
    FROM tariff_codes WHERE parent_code IS NULL
    UNION ALL
    SELECT t.id, t.hs_code, t.description, t.parent_code, t.level, tt.depth + 1
    FROM tariff_codes t
    JOIN tariff_tree tt ON t.parent_code = tt.hs_code
)
SELECT * FROM tariff_tree ORDER BY hs_code;

-- Enhanced news feed with intelligence
SELECT 
    n.*,
    COUNT(related_tariff_codes) as affected_codes_count,
    AVG(impact_rating) as avg_impact
FROM news_items n
WHERE n.publication_date >= %s
ORDER BY n.impact_rating DESC, n.publication_date DESC;
```

### Phase 2: Frontend Refactoring (Week 3-4)

#### New Component Structure
```typescript
// Remove existing redundant components
src/
├── components/
│   ├── dashboard/
│   │   ├── NewsIntelligenceCenter.tsx      // NEW
│   │   ├── TradeStatsSidebar.tsx           // NEW
│   │   └── RecentRulingsPanel.tsx          // NEW
│   ├── tariff-tree/
│   │   ├── InteractiveTariffTree.tsx       // NEW
│   │   ├── TariffDetailPanel.tsx           // NEW
│   │   └── TreeNavigation.tsx              // NEW
│   ├── ai-assistant/
│   │   ├── ConversationalInterface.tsx     // NEW
│   │   ├── ComprehensiveDutyCalculator.tsx // ENHANCED with all taxes
│   │   └── ContextualTools.tsx             // NEW
│   ├── export-tariffs/
│   │   ├── AHECCTreeBrowser.tsx           // NEW
│   │   ├── ExportRequirementsPanel.tsx    // NEW
│   │   ├── MarketAccessDashboard.tsx      // NEW
│   │   └── ExportDocumentationTools.tsx   // NEW
│   └── common/
│       ├── Layout.tsx                      // ENHANCED
│       └── Navigation.tsx                  // SIMPLIFIED
├── pages/
│   ├── Dashboard.tsx                       // REFACTORED
│   ├── TariffTree.tsx                      // NEW
│   ├── AIAssistant.tsx                     // NEW
│   └── ExportTariffs.tsx                   // NEW
└── hooks/
    ├── useNewsIntelligence.ts              // NEW
    ├── useTariffTree.ts                    // NEW
    ├── useAIConversation.ts                // NEW
    ├── useComprehensiveTaxCalculator.ts    // NEW
    └── useExportClassification.ts          // NEW
```

#### Files to Remove/Consolidate
```
REMOVE:
- src/pages/Home.tsx (functionality moved to Dashboard)
- src/pages/Search.tsx (functionality moved to AIAssistant)
- src/pages/TariffLookup.tsx (functionality moved to TariffTree)
- src/components/duty/ (move to ai-assistant/)
- src/components/search/ (functionality integrated into AI)

CONSOLIDATE:
- All news-related components → dashboard/
- All tariff browsing → tariff-tree/
- Search + calculator + AI → ai-assistant/
```

### Phase 3: Enhanced Features (Week 5-6)

#### Dashboard News Intelligence
```typescript
interface NewsIntelligenceProps {
  autoRefresh?: boolean;
  filterPresets?: string[];
}

const NewsIntelligenceCenter: React.FC<NewsIntelligenceProps> = ({
  autoRefresh = true,
  filterPresets = ['critical', 'regulatory', 'tco', 'dumping']
}) => {
  const { data: newsItems, refetch } = useNewsIntelligence();
  
  return (
    <div className="news-intelligence-center">
      <div className="news-filters">
        {filterPresets.map(filter => (
          <FilterButton key={filter} filter={filter} />
        ))}
      </div>
      
      <div className="news-timeline">
        <InfiniteScroll
          dataLength={newsItems.length}
          next={loadMoreNews}
          hasMore={hasMoreNews}
        >
          {newsItems.map(item => (
            <NewsIntelligenceCard 
              key={item.id} 
              item={item}
              onExpand={handleNewsExpand}
              onRelatedCodeClick={navigateToTariffTree}
            />
          ))}
        </InfiniteScroll>
      </div>
    </div>
  );
};
```

#### Enhanced AI Assistant with Comprehensive Calculator
```typescript
const ComprehensiveDutyCalculator: React.FC = () => {
  const [calculation, setCalculation] = useState({
    hsCode: '',
    countryOfOrigin: '',
    customsValue: 0,
    currency: 'AUD',
    vehicleDetails: null,
    alcoholDetails: null,
    tobaccoDetails: null
  });
  
  const { data: taxBreakdown, isLoading } = useComprehensiveTaxCalculator(calculation);
  
  return (
    <div className="comprehensive-calculator">
      <div className="calculator-inputs">
        <HSCodeInput 
          value={calculation.hsCode}
          onChange={(code) => setCalculation(prev => ({ ...prev, hsCode: code }))}
        />
        
        <CountrySelector 
          value={calculation.countryOfOrigin}
          onChange={(country) => setCalculation(prev => ({ ...prev, countryOfOrigin: country }))}
        />
        
        <CurrencyInput
          value={calculation.customsValue}
          currency={calculation.currency}
          onChange={(value, currency) => setCalculation(prev => ({ 
            ...prev, 
            customsValue: value,
            currency: currency 
          }))}
        />
        
        {/* Conditional inputs based on HS code */}
        {isMotorVehicle(calculation.hsCode) && (
          <VehicleDetailsInput 
            onChange={(details) => setCalculation(prev => ({ 
              ...prev, 
              vehicleDetails: details 
            }))}
          />
        )}
        
        {isWine(calculation.hsCode) && (
          <AlcoholDetailsInput 
            onChange={(details) => setCalculation(prev => ({ 
              ...prev, 
              alcoholDetails: details 
            }))}
          />
        )}
      </div>
      
      <div className="tax-breakdown-results">
        {taxBreakdown && (
          <TaxBreakdownDisplay 
            breakdown={taxBreakdown}
            showOptimizationTips={true}
            allowExport={true}
          />
        )}
      </div>
    </div>
  );
};

const TaxBreakdownDisplay: React.FC<{ breakdown: TaxBreakdown }> = ({ breakdown }) => {
  return (
    <div className="tax-breakdown">
      <div className="tax-line-item">
        <span>Customs Duty ({breakdown.customs_duty.rate}%)</span>
        <span>${breakdown.customs_duty.amount.toLocaleString()}</span>
      </div>
      
      {breakdown.luxury_car_tax.applicable && (
        <div className="tax-line-item luxury-car-tax">
          <span>Luxury Car Tax (33% on excess over ${breakdown.luxury_car_tax.threshold.toLocaleString()})</span>
          <span>${breakdown.luxury_car_tax.amount.toLocaleString()}</span>
        </div>
      )}
      
      {breakdown.wine_equalisation_tax.applicable && (
        <div className="tax-line-item wet">
          <span>Wine Equalisation Tax (29%)</span>
          <span>${breakdown.wine_equalisation_tax.amount.toLocaleString()}</span>
        </div>
      )}
      
      <div className="tax-line-item gst">
        <span>GST (10% on dutiable value)</span>
        <span>${breakdown.gst.amount.toLocaleString()}</span>
      </div>
      
      <div className="tax-total">
        <span>Total Landed Cost</span>
        <span>${breakdown.total_landed_cost.toLocaleString()}</span>
      </div>
      
      {breakdown.optimization_tips && (
        <div className="optimization-tips">
          <h4>💡 Cost Optimization Tips</h4>
          {breakdown.optimization_tips.map((tip, index) => (
            <p key={index}>{tip}</p>
          ))}
        </div>
      )}
    </div>
  );
};
```

#### Export Tariffs Page Implementation
```typescript
const ExportTariffs: React.FC = () => {
  const { ahecTree, selectedCode, expandedNodes } = useExportClassification();
  const { exportRequirements } = useExportRequirements(selectedCode);
  
  return (
    <div className="export-tariffs-layout">
      <div className="ahecc-tree-panel">
        <AHECCTreeBrowser 
          data={ahecTree}
          onSelect={handleAHECCSelect}
          onExpand={handleNodeExpand}
          searchEnabled={true}
          crossReferenceEnabled={true}
        />
      </div>
      
      <div className="export-requirements-panel">
        {selectedCode && (
          <>
            <ExportCodeDetails code={selectedCode} />
            <ExportRequirementsDisplay requirements={exportRequirements} />
            <MarketAccessInformation code={selectedCode} />
            <ExportDocumentationChecklist code={selectedCode} />
          </>
        )}
      </div>
    </div>
  );
};

const AHECCTreeBrowser: React.FC = ({ data, onSelect, searchEnabled }) => {
  return (
    <div className="ahecc-tree-browser">
      <div className="tree-header">
        <h3>AHECC Export Classification</h3>
        {searchEnabled && (
          <SearchInput 
            placeholder="Search AHECC codes or descriptions"
            onSearch={handleAHECCSearch}
          />
        )}
      </div>
      
      <Tree
        showLine
        showIcon
        onSelect={onSelect}
        treeData={data}
        className="ahecc-tree"
        titleRender={(nodeData) => (
          <div className="tree-node">
            <span className="ahecc-code">{nodeData.ahecc_code}</span>
            <span className="description">{nodeData.description}</span>
            {nodeData.corresponding_import_code && (
              <span className="import-ref">
                HS: {nodeData.corresponding_import_code}
              </span>
            )}
          </div>
        )}
      />
    </div>
  );
};

const ExportRequirementsDisplay: React.FC<{ requirements: ExportRequirements }> = ({ 
  requirements 
}) => {
  return (
    <div className="export-requirements">
      <div className="requirements-section">
        <h4>📋 Export Documentation</h4>
        <ul>
          {requirements.documentation.map((doc, index) => (
            <li key={index} className="requirement-item">
              <span className="doc-type">{doc.type}</span>
              <span className="doc-description">{doc.description}</span>
              {doc.mandatory && <Badge color="red">Required</Badge>}
            </li>
          ))}
        </ul>
      </div>
      
      <div className="requirements-section">
        <h4>🛂 AQIS/Quarantine Requirements</h4>
        {requirements.quarantine.map((req, index) => (
          <div key={index} className="quarantine-requirement">
            <p><strong>{req.requirement_type}:</strong> {req.description}</p>
            {req.treatment_required && (
              <p className="treatment-note">Treatment: {req.treatment_details}</p>
            )}
          </div>
        ))}
      </div>
      
      <div className="requirements-section">
        <h4>🌏 Market Access by Destination</h4>
        <MarketAccessTable destinations={requirements.major_destinations} />
      </div>
    </div>
  );
};
```

## Updated Routing Configuration

```typescript
// App.tsx routing changes
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Redirect home to dashboard */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          {/* Four main pages */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/tariff-tree" element={<TariffTree />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
          <Route path="/export-tariffs" element={<ExportTariffs />} />
          
          {/* Direct code access */}
          <Route path="/tariff/:hsCode" element={<TariffTree />} />
          <Route path="/export/:ahecCode" element={<ExportTariffs />} />
          
          {/* 404 redirect */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
}
```

## Navigation Simplification

```typescript
const Navigation: React.FC = () => {
  return (
    <nav className="main-navigation">
      <div className="nav-links">
        <NavLink to="/dashboard" icon="📰">
          News & Intelligence
        </NavLink>
        <NavLink to="/tariff-tree" icon="🌳">
          Import Tariffs
        </NavLink>
        <NavLink to="/export-tariffs" icon="📤">
          Export Classification
        </NavLink>
        <NavLink to="/ai-assistant" icon="🤖">
          AI Assistant
        </NavLink>
      </div>
      
      <div className="nav-actions">
        <SearchGlobal />
        <UserProfile />
        <SystemStatus />
      </div>
    </nav>
  );
};
```

## Database Schema Preservation

**✅ No changes required to existing database schema**

All existing tables remain unchanged:
- `tariff_codes` - Complete Schedule 3 data
- `export_codes` - AHECC classification system (already implemented)
- `news_items` - News aggregation system
- `duty_rates` & `fta_rates` - Duty calculation data
- `legislation_documents` - Regulatory intelligence
- `tcos` & `dumping_duties` - Special measures
- All AI and relationship tables

**✅ Enhanced tax calculation logic (no schema changes)**

The comprehensive tax calculator uses existing tariff data with enhanced business logic:
- **Luxury Car Tax**: Calculated based on HS codes 8703-8705 and value thresholds
- **Wine Equalisation Tax**: Applied to HS codes 2204-2206 
- **Tobacco Excise**: Complex calculations for Chapter 24 products
- **Fuel Excise**: Applied to petroleum products
- **Other Levies**: ACMA charges, container deposits calculated by product type

**✅ Export functionality uses existing tables**

Export features leverage the already-implemented export infrastructure:
- `export_codes` table contains complete AHECC data
- Cross-references to `tariff_codes` for import/export code mapping
- `fta_rates` used for export market access benefits
- `news_items` filtered for export-related updates

**✅ Existing APIs enhanced, not replaced**

Current API endpoints remain functional with enhancements:
- Enhanced response data for better UX
- Additional filtering and sorting options
- Improved caching and performance
- New AI integration endpoints

## Migration Strategy

### Week 1: Backend API Enhancements
1. **Enhanced Tax Calculator**: Add luxury car tax, WET, tobacco excise calculations
2. **Export APIs**: Implement AHECC tree and export requirements endpoints
3. **Dashboard News**: Add aggregation endpoints for trade intelligence
4. **Performance Optimization**: Optimize existing queries for new UI patterns

### Week 2: Frontend Component Development
1. **NewsIntelligenceCenter**: Build scrollable news feed with filters
2. **InteractiveTariffTree**: Develop complete Schedule 3 browser
3. **ConversationalInterface**: Create AI chat with context integration
4. **ComprehensiveDutyCalculator**: Enhanced calculator with all Australian taxes
5. **AHECCTreeBrowser**: Build export classification explorer

### Week 3: Page Integration & Routing
1. **Dashboard**: Refactor with news-focused layout
2. **TariffTree**: Build dedicated import tariff browser
3. **AIAssistant**: Create consultation hub with integrated calculator
4. **ExportTariffs**: Build comprehensive export classification center
5. **Navigation**: Update routing for 4-page structure

### Week 4: Enhanced Features & Testing
1. **Tax Calculation**: Implement luxury car tax and other import taxes
2. **Export Requirements**: Add country-specific export requirements
3. **User Testing**: Acceptance testing with customs brokers
4. **Performance**: Optimize loading and calculation speeds

### Week 5: Cleanup & Deployment
1. **Component Cleanup**: Remove redundant pages and components
2. **Export Intelligence**: Complete export documentation and permit tools
3. **Production Deployment**: Roll out enhanced 4-page system
4. **Training**: User training on new export features and enhanced calculator

## Success Metrics

### User Experience Improvements
- **Task Completion Time**: 40% reduction in time to find relevant news
- **Navigation Efficiency**: 60% fewer clicks to access tariff information
- **User Adoption**: 90% of team using AI Assistant within 30 days
- **Search Success Rate**: 85% of AI queries result in actionable information

### Technical Performance
- **Page Load Time**: <2 seconds for all pages
- **News Feed Performance**: Real-time updates with <1 second latency
- **Tree Navigation**: <500ms response time for tree expansion
- **AI Response Time**: <3 seconds for complex queries

### Business Impact
- **Reduced Training Time**: 50% faster onboarding for new team members
- **Compliance Accuracy**: 30% improvement in regulatory compliance tracking
- **Cost Optimization**: 20% better identification of duty savings opportunities
- **Team Productivity**: 25% increase in cases processed per day

This refactored structure provides a much cleaner, more intuitive user experience while preserving all the powerful functionality you've built in the backend systems.
